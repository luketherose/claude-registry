#!/usr/bin/env bash
# setup-capabilities.sh
# Installs capabilities from claude-registry into a Claude Code project or globally.
#
# Usage:
#   ./setup-capabilities.sh                        # interactive, installs into current directory
#   ./setup-capabilities.sh /path/to/project       # interactive, installs into given project
#   ./setup-capabilities.sh /path/to/project all   # installs all agents + skills, no prompt
#   ./setup-capabilities.sh --global               # installs everything into ~/.claude (global)
#
# The --global flag (or passing ~/.claude as project path) installs all agents and skills
# so they are available in every Claude Code session, without per-project setup.

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
RED='\033[0;31m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MARKETPLACE_ROOT="$REGISTRY_ROOT/claude-marketplace"
CATALOG="$MARKETPLACE_ROOT/catalog.json"

# Parse --global flag
GLOBAL=false
ARGS=()
for arg in "$@"; do
  if [[ "$arg" == "--global" ]]; then
    GLOBAL=true
  else
    ARGS+=("$arg")
  fi
done

if $GLOBAL; then
  PROJECT_DIR="$HOME/.claude"
  SELECTION="all"
else
  PROJECT_DIR="${ARGS[0]:-$(pwd)}"
  SELECTION="${ARGS[1]:-}"
fi

if [[ ! -f "$CATALOG" ]]; then
  echo -e "${RED}Error:${RESET} catalog.json not found: $CATALOG"
  exit 1
fi

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo -e "${RED}Error:${RESET} target directory not found: $PROJECT_DIR"
  exit 1
fi

# When target is ~/.claude, agents go directly in ~/.claude/agents (no .claude/ subdirectory)
if [[ "$PROJECT_DIR" == "$HOME/.claude" ]]; then
  AGENTS_DIR="$PROJECT_DIR/agents"
  SETTINGS_FILE="$PROJECT_DIR/settings.json"
else
  AGENTS_DIR="$PROJECT_DIR/.claude/agents"
  SETTINGS_FILE="$PROJECT_DIR/.claude/settings.json"
fi

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║     Claude Registry — Setup Capabilities     ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  Registry: ${DIM}$REGISTRY_ROOT${RESET}"
echo -e "  Target:   ${CYAN}$AGENTS_DIR${RESET}"
$GLOBAL && echo -e "  Mode:     ${GREEN}global (all agents + skills)${RESET}"
echo ""

# Build list of agents from catalog
CATALOG_TMP=$(mktemp /tmp/claude-catalog-XXXXXX.json)
python3 -c "
import json
with open('$CATALOG') as f:
    data = json.load(f)
caps = [c for c in data.get('capabilities', [])
        if not any(k.startswith('_') for k in c)
        and c.get('type', 'agent') == 'agent']
with open('$CATALOG_TMP', 'w') as out:
    json.dump(caps, out)
"
trap "rm -f $CATALOG_TMP" EXIT

N=$(python3 -c "import json; print(len(json.load(open('$CATALOG_TMP'))))")
if [[ "$N" -eq 0 ]]; then
  echo -e "${YELLOW}No capabilities found in catalog.${RESET}"
  exit 0
fi

# Show menu only in interactive mode
if [[ -z "$SELECTION" ]]; then
  echo -e "${BOLD}Available capabilities:${RESET}"
  echo ""
  echo -e "  ${DIM}Num  Tier    Name                           Description${RESET}"
  echo -e "  ${DIM}───  ──────  ─────────────────────────────  ──────────────────────────────────────${RESET}"
  python3 -c "
import json
caps = json.load(open('$CATALOG_TMP'))
for i, c in enumerate(caps, 1):
    tier = c.get('tier','?')
    name = c.get('name','?')
    desc = ' '.join(c.get('description','').split())[:55]
    deps = c.get('dependencies', [])
    tier_color = '\033[0;32m' if tier == 'stable' else '\033[1;33m'
    reset = '\033[0m'
    dep_str = f' \033[2m[uses: {chr(44).join(deps)}]\033[0m' if deps else ''
    print(f'  {i:3}  {tier_color}{tier:<6}{reset}  {name:<29}  {desc}...{dep_str}')
"
  echo ""
  echo -e "  ${DIM}Type numbers separated by spaces, or:${RESET}"
  echo -e "  ${CYAN}all${RESET}  — install all agents (stable + beta) and all skills"
  echo -e "  ${CYAN}q${RESET}    — quit"
  echo ""
  read -rp "  Selection: " SELECTION
fi

if [[ "$SELECTION" == "q" || -z "$SELECTION" ]]; then
  echo "Aborted."
  exit 0
fi

mkdir -p "$AGENTS_DIR"
INSTALLED=()

install_capability() {
  local name="$1" tier="$2" is_dep="${3:-}"
  local src

  # Resolve the source path from catalog.json's `file` field (single source of
  # truth — no path inference needed). Files may live in topic subfolders, e.g.
  # `beta/indexing/foo.md` or `skills/frontend/angular/bar.md`.
  local relpath
  relpath=$(python3 - "$CATALOG" "$name" <<'PYEOF'
import json, sys
catalog = json.load(open(sys.argv[1]))
name = sys.argv[2]
for cap in catalog.get("capabilities", []):
    if cap.get("name") == name:
        print(cap.get("file", ""))
        break
PYEOF
)
  if [[ -n "$relpath" ]]; then
    src="$MARKETPLACE_ROOT/$relpath"
  else
    # Backward-compatible fallback for entries that somehow lack a `file` field
    if [[ "$tier" == "skill" ]]; then
      src="$MARKETPLACE_ROOT/skills/$name.md"
    else
      src="$MARKETPLACE_ROOT/$tier/$name.md"
    fi
  fi

  local dst="$AGENTS_DIR/$name.md"

  if [[ ! -f "$src" ]]; then
    echo -e "  ${RED}✗${RESET} $name — source file not found ($src)"
    return 1
  fi

  if [[ -f "$dst" ]]; then
    [[ -z "$is_dep" ]] && echo -e "  ${YELLOW}↺${RESET} $name — already present, overwritten"
  else
    if [[ -n "$is_dep" ]]; then
      echo -e "  ${CYAN}↳${RESET} $name ${DIM}[skill — dependency]${RESET}"
    else
      echo -e "  ${GREEN}✓${RESET} $name ${DIM}[$tier]${RESET}"
    fi
  fi

  cp "$src" "$dst"
  INSTALLED+=("$name")

  # Resolve and install dependencies
  while IFS='|' read -r dep_name dep_tier; do
    [[ -z "$dep_name" ]] && continue
    if [[ ! -f "$AGENTS_DIR/$dep_name.md" ]]; then
      install_capability "$dep_name" "$dep_tier" "dep"
    fi
  done < <(python3 - "$name" "$CATALOG" <<'DEPEOF'
import json, sys
name = sys.argv[1]
all_caps = json.load(open(sys.argv[2])).get('capabilities', [])
cap = next((c for c in all_caps if c.get('name') == name), None)
if cap:
    for dep in cap.get('dependencies', []):
        dep_cap = next((c for c in all_caps if c.get('name') == dep), None)
        if dep_cap:
            t = 'skill' if dep_cap.get('type') == 'skill' else dep_cap.get('tier', 'beta')
            print(f"{dep}|{t}")
DEPEOF
)
}

install_all_skills() {
  echo -e "  ${DIM}— skills —${RESET}"
  while IFS='|' read -r name tier; do
    [[ -z "$name" ]] && continue
    if [[ ! -f "$AGENTS_DIR/$name.md" ]]; then
      install_capability "$name" "$tier"
    fi
  done < <(python3 -c "
import json
all_caps = json.load(open('$CATALOG')).get('capabilities', [])
for c in all_caps:
    if not any(k.startswith('_') for k in c) and c.get('type') == 'skill':
        print(c['name'] + '|skill')
")
}

echo ""
echo -e "${BOLD}Installing:${RESET}"
echo ""

if [[ "$SELECTION" == "all" ]]; then
  # Install all agents (stable + beta)
  while IFS='|' read -r name tier; do
    install_capability "$name" "$tier"
  done < <(python3 -c "
import json
caps = json.load(open('$CATALOG_TMP'))
for c in caps:
    print(c['name'] + '|' + c['tier'])
")
  # Install all skills not already pulled in as dependencies
  install_all_skills
else
  CAPMAP_TMP=$(mktemp /tmp/claude-capmap-XXXXXX.sh)
  python3 -c "
import json
caps = json.load(open('$CATALOG_TMP'))
for i, c in enumerate(caps, 1):
    name = c['name'].replace(\"'\", '')
    tier = c['tier'].replace(\"'\", '')
    print(f\"CAP_{i}_NAME='{name}'\")
    print(f\"CAP_{i}_TIER='{tier}'\")
print(f'CAP_TOTAL={len(caps)}')
" > "$CAPMAP_TMP"
  # shellcheck source=/dev/null
  source "$CAPMAP_TMP"
  rm -f "$CAPMAP_TMP"

  for num in $SELECTION; do
    name_var="CAP_${num}_NAME"
    tier_var="CAP_${num}_TIER"
    if [[ -n "${!name_var:-}" ]]; then
      install_capability "${!name_var}" "${!tier_var}"
    else
      echo -e "  ${RED}✗${RESET} Invalid number: $num (max: $CAP_TOTAL)"
    fi
  done
fi

# Update settings.json with Agent permissions
if [[ ${#INSTALLED[@]} -gt 0 ]]; then
  echo ""
  echo -e "${BOLD}Updating settings.json:${RESET}"

  python3 - "$SETTINGS_FILE" "${INSTALLED[@]}" <<'PYEOF'
import json, sys
from pathlib import Path

settings_path = Path(sys.argv[1])
new_agents = sys.argv[2:]

settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
perms = settings.setdefault("permissions", {})
allow = perms.setdefault("allow", [])

added = []
for agent in new_agents:
    rule = f"Agent({agent})"
    if rule not in allow:
        allow.append(rule)
        added.append(rule)

settings_path.parent.mkdir(parents=True, exist_ok=True)
settings_path.write_text(json.dumps(settings, indent=2) + "\n")

if added:
    print(f"  Added {len(added)} Agent rules to settings.json")
else:
    print("  settings.json already up to date")
PYEOF
fi

echo ""
echo -e "${BOLD}${GREEN}══════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${GREEN}  Done: ${#INSTALLED[@]} capabilities installed${RESET}"
echo -e "${BOLD}${GREEN}══════════════════════════════════════════════${RESET}"
echo ""
echo -e "  Directory: ${CYAN}$AGENTS_DIR${RESET}"
echo ""

if $GLOBAL; then
  echo -e "  Capabilities are now available in ${BOLD}all${RESET} Claude Code sessions."
  echo -e "  Verify with ${CYAN}/agents${RESET} in Claude Code."
else
  echo -e "  Next steps:"
  echo -e "  1. Commit to your project:"
  echo -e "     ${DIM}git add .claude/ && git commit -m 'add: claude capabilities'${RESET}"
  echo -e "  2. Verify with ${CYAN}/agents${RESET} in Claude Code."
fi
echo ""
