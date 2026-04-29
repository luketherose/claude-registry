#!/usr/bin/env bash
# publish.sh
# Publishes a capability from claude-catalog to claude-marketplace.
#
# Usage:
#   ./claude-marketplace/scripts/publish.sh <capability-name> <version> <tier> [--topic <topic>]
#
# Example:
#   ./claude-marketplace/scripts/publish.sh software-architect 1.1.0 stable
#   ./claude-marketplace/scripts/publish.sh technical-analyst 0.2.0 beta
#   ./claude-marketplace/scripts/publish.sh new-agent 0.1.0 beta --topic quality
#
# Prerequisites:
#   - Run from the repository root (claude-registry/)
#   - python3 available in PATH (for JSON manipulation)
#   - git configured with write access
#
# Topic resolution (in order):
#   1. --topic <topic> argument (overrides everything)
#   2. existing entry in catalog.json (preserves the published topic on re-publish)
#   3. catalog source path: if claude-catalog/agents/<topic>/<name>.md exists, use <topic>
#   4. error — ask the user to pass --topic explicitly
#
# What this script does:
#   1. Validates arguments and source file existence
#   2. Resolves the marketplace topic for grouping
#   3. Copies the .md file from claude-catalog/agents/ to claude-marketplace/{tier}/{topic}/
#   4. Updates catalog.json with the new version, tier, file path, and publish date
#   5. Commits the marketplace changes

set -euo pipefail

CAPABILITY_NAME=""
VERSION=""
TIER=""
TOPIC=""

# Parse positional + --topic flag
POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --topic)
      TOPIC="${2:-}"
      shift 2
      ;;
    --topic=*)
      TOPIC="${1#--topic=}"
      shift
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done
CAPABILITY_NAME="${POSITIONAL[0]:-}"
VERSION="${POSITIONAL[1]:-}"
TIER="${POSITIONAL[2]:-}"

# Validate arguments
if [[ -z "$CAPABILITY_NAME" || -z "$VERSION" || -z "$TIER" ]]; then
  echo "Usage: $0 <capability-name> <version> <tier> [--topic <topic>]"
  echo "  tier: stable | beta"
  exit 1
fi

if [[ "$TIER" != "stable" && "$TIER" != "beta" ]]; then
  echo "Error: tier must be 'stable' or 'beta', got '$TIER'"
  exit 1
fi

# Paths (relative to repository root)
CATALOG_AGENTS_DIR="claude-catalog/agents"
CATALOG_FILE="claude-marketplace/catalog.json"
TODAY=$(date -u +%Y-%m-%d)

# Locate the catalog source file (may be at root or under a topic subfolder)
SOURCE_FILE=""
for candidate in "$CATALOG_AGENTS_DIR/${CAPABILITY_NAME}.md" $(find "$CATALOG_AGENTS_DIR" -maxdepth 2 -name "${CAPABILITY_NAME}.md" 2>/dev/null); do
  if [[ -f "$candidate" ]]; then
    SOURCE_FILE="$candidate"
    break
  fi
done

# Validate source file exists
if [[ -z "$SOURCE_FILE" || ! -f "$SOURCE_FILE" ]]; then
  echo "Error: Source file not found for '${CAPABILITY_NAME}' under ${CATALOG_AGENTS_DIR}/."
  echo "Ensure the capability exists in claude-catalog/agents/<topic>/${CAPABILITY_NAME}.md before publishing."
  exit 1
fi

# Resolve TOPIC if not given via --topic
if [[ -z "$TOPIC" ]]; then
  # 2. Try existing catalog.json entry (preserves topic on re-publish)
  TOPIC=$(python3 - "$CATALOG_FILE" "$CAPABILITY_NAME" <<'PYEOF'
import json, sys
try:
    catalog = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
name = sys.argv[2]
for cap in catalog.get("capabilities", []):
    if cap.get("name") == name:
        f = cap.get("file", "")
        # file = "<tier>/<topic>/<name>.md" -> topic = parts[1] if depth >= 3 else ""
        parts = f.split("/")
        if len(parts) >= 3:
            print(parts[1])
        break
PYEOF
)
fi
if [[ -z "$TOPIC" ]]; then
  # 3. Try catalog source path: claude-catalog/agents/<topic>/<name>.md
  src_dir="$(dirname "$SOURCE_FILE")"
  if [[ "$src_dir" != "$CATALOG_AGENTS_DIR" ]]; then
    TOPIC="$(basename "$src_dir")"
  fi
fi
if [[ -z "$TOPIC" ]]; then
  echo "Error: could not resolve a marketplace topic for '${CAPABILITY_NAME}'."
  echo "Pass --topic <name> explicitly, or place the source under claude-catalog/agents/<topic>/."
  exit 1
fi

TARGET_DIR="claude-marketplace/${TIER}/${TOPIC}"
TARGET_FILE="${TARGET_DIR}/${CAPABILITY_NAME}.md"
TARGET_RELPATH="${TIER}/${TOPIC}/${CAPABILITY_NAME}.md"

echo "Publishing: $CAPABILITY_NAME@$VERSION → $TIER (topic: $TOPIC)"
echo "  Source:  $SOURCE_FILE"
echo "  Target:  $TARGET_FILE"

# Step 1: Copy the capability file. If a flat or differently-grouped previous
# version of this capability exists in the marketplace, remove it so we don't
# leave orphan files behind.
mkdir -p "$TARGET_DIR"
while IFS= read -r stale; do
  [[ -z "$stale" || "$stale" == "$TARGET_FILE" ]] && continue
  echo "  · removing stale: $stale"
  git rm -f "$stale" >/dev/null 2>&1 || rm -f "$stale"
done < <(find "claude-marketplace/${TIER}" -name "${CAPABILITY_NAME}.md" 2>/dev/null)
cp "$SOURCE_FILE" "$TARGET_FILE"
echo "  ✓ Copied to $TARGET_FILE"

# Step 2: Update catalog.json
python3 - "$CATALOG_FILE" "$CAPABILITY_NAME" "$VERSION" "$TIER" "$TODAY" "$TARGET_RELPATH" <<'PYEOF'
import json, sys

catalog_path = sys.argv[1]
name = sys.argv[2]
version = sys.argv[3]
tier = sys.argv[4]
today = sys.argv[5]
relpath = sys.argv[6]

with open(catalog_path) as f:
    catalog = json.load(f)

# Find existing entry or create new one
found = False
for cap in catalog.get("capabilities", []):
    if cap.get("name") == name:
        cap["version"] = version
        cap["tier"] = tier
        cap["status"] = "active"
        cap["file"] = relpath
        cap["published"] = today
        found = True
        break

if not found:
    print(f"WARNING: Capability '{name}' not found in catalog.json. Adding a minimal entry.", file=sys.stderr)
    print("Please manually complete the entry (description, tools, model, tags) in catalog.json", file=sys.stderr)
    catalog.setdefault("capabilities", []).append({
        "name": name,
        "version": version,
        "tier": tier,
        "status": "active",
        "description": "TODO: add description",
        "file": relpath,
        "tools": [],
        "model": "sonnet",
        "tags": [],
        "published": today,
        "changelog": f"Published {version}"
    })

catalog["generated"] = today

with open(catalog_path, "w") as f:
    json.dump(catalog, f, indent=2)
    f.write("\n")

print(f"  ✓ Updated catalog.json: {name}@{version} → {relpath}")
PYEOF

# Step 3: Stage and commit
git add "$TARGET_FILE" "$CATALOG_FILE"
git commit -m "release: ${CAPABILITY_NAME}@${VERSION} → ${TIER}

Published capability '${CAPABILITY_NAME}' version ${VERSION} to ${TIER} tier."

echo ""
echo "Done. ${CAPABILITY_NAME}@${VERSION} published to ${TIER}."
echo ""
echo "Next steps:"
echo "  1. Push to remote: git push origin main"
echo "  2. Create git tag: git tag ${CAPABILITY_NAME}@${VERSION} && git push origin ${CAPABILITY_NAME}@${VERSION}"
echo "  3. Notify the team of the new release"
