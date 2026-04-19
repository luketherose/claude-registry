#!/usr/bin/env bash
# publish.sh
# Publishes a capability from claude-catalog to claude-marketplace.
#
# Usage:
#   ./claude-marketplace/scripts/publish.sh <capability-name> <version> <tier>
#
# Example:
#   ./claude-marketplace/scripts/publish.sh software-architect 1.1.0 stable
#   ./claude-marketplace/scripts/publish.sh technical-analyst 0.2.0 beta
#
# Prerequisites:
#   - Run from the repository root (claude-registry/)
#   - python3 available in PATH (for JSON manipulation)
#   - git configured with write access
#
# What this script does:
#   1. Validates arguments and source file existence
#   2. Copies the .md file from claude-catalog/agents/ to claude-marketplace/{tier}/
#   3. Updates catalog.json with the new version, tier, and publish date
#   4. Commits the marketplace changes

set -euo pipefail

CAPABILITY_NAME="${1:-}"
VERSION="${2:-}"
TIER="${3:-}"

# Validate arguments
if [[ -z "$CAPABILITY_NAME" || -z "$VERSION" || -z "$TIER" ]]; then
  echo "Usage: $0 <capability-name> <version> <tier>"
  echo "  tier: stable | beta"
  exit 1
fi

if [[ "$TIER" != "stable" && "$TIER" != "beta" ]]; then
  echo "Error: tier must be 'stable' or 'beta', got '$TIER'"
  exit 1
fi

# Paths (relative to repository root)
SOURCE_FILE="claude-catalog/agents/${CAPABILITY_NAME}.md"
TARGET_DIR="claude-marketplace/${TIER}"
TARGET_FILE="${TARGET_DIR}/${CAPABILITY_NAME}.md"
CATALOG_FILE="claude-marketplace/catalog.json"
TODAY=$(date -u +%Y-%m-%d)

# Validate source file exists
if [[ ! -f "$SOURCE_FILE" ]]; then
  echo "Error: Source file not found: $SOURCE_FILE"
  echo "Ensure the capability exists in claude-catalog/agents/ before publishing."
  exit 1
fi

# Validate catalog file exists
if [[ ! -f "$CATALOG_FILE" ]]; then
  echo "Error: catalog.json not found: $CATALOG_FILE"
  exit 1
fi

echo "Publishing: $CAPABILITY_NAME@$VERSION → $TIER"
echo "  Source:  $SOURCE_FILE"
echo "  Target:  $TARGET_FILE"

# Step 1: Copy the capability file
mkdir -p "$TARGET_DIR"
cp "$SOURCE_FILE" "$TARGET_FILE"
echo "  ✓ Copied to $TARGET_FILE"

# Step 2: Update catalog.json
python3 - "$CATALOG_FILE" "$CAPABILITY_NAME" "$VERSION" "$TIER" "$TODAY" <<'PYEOF'
import json, sys

catalog_path = sys.argv[1]
name = sys.argv[2]
version = sys.argv[3]
tier = sys.argv[4]
today = sys.argv[5]

with open(catalog_path) as f:
    catalog = json.load(f)

# Find existing entry or create new one
found = False
for cap in catalog.get("capabilities", []):
    if cap.get("name") == name:
        cap["version"] = version
        cap["tier"] = tier
        cap["status"] = "active"
        cap["file"] = f"{tier}/{name}.md"
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
        "file": f"{tier}/{name}.md",
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

print(f"  ✓ Updated catalog.json: {name}@{version} → {tier}")
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
