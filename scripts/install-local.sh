#!/usr/bin/env bash
# install-local.sh
# Installs the registry into ~/.claude/ without the plugin marketplace.
#
# Use this when enterprise policy (strictKnownMarketplaces) blocks the marketplace
# source. Agents go to ~/.claude/agents/, skills to ~/.claude/skills/ (where the
# Skill tool finds them), and bundled reference material to
# ~/.claude/registry-references/<plugin>/ with every ${CLAUDE_PLUGIN_ROOT} rewritten
# to that absolute path, because the variable only expands inside a real plugin.
#
# Usage:
#   ./scripts/install-local.sh                        # install the default set
#   ./scripts/install-local.sh dev-standards docs-branding
#   ./scripts/install-local.sh --all
#   ./scripts/install-local.sh --list
#   ./scripts/install-local.sh --uninstall

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
RED='\033[0;31m'; BOLD='\033[1m'; RESET='\033[0m'

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
AGENTS="$CLAUDE_DIR/agents"
SKILLS="$CLAUDE_DIR/skills"
REFS="$CLAUDE_DIR/registry-references"
MANIFEST="$CLAUDE_DIR/.registry-install-manifest"

# Enabling every plugin at once puts ~12000 tokens of subagent descriptions into the
# delegation budget, against a 15000 ceiling. The default set is the day-to-day one.
DEFAULT_SET=(dev-standards analysis-architecture docs-branding)

cd "$ROOT"
ALL_PLUGINS=$(find plugins -maxdepth 1 -mindepth 1 -type d -exec basename {} \; | sort)

usage() { sed -n '2,16p' "$0"; }

list_plugins() {
  printf "${BOLD}%-24s %6s %6s  %s${RESET}\n" PLUGIN AGENTS SKILLS "DESCRIPTION"
  for p in $ALL_PLUGINS; do
    a=$( { find "plugins/$p/agents" -name '*.md' 2>/dev/null || true; } | wc -l | tr -d ' ')
    s=$( { find "plugins/$p/skills" -name 'SKILL.md' 2>/dev/null || true; } | wc -l | tr -d ' ')
    d=$(python3 -c "import json;print(json.load(open('plugins/$p/.claude-plugin/plugin.json'))['description'][:60])" 2>/dev/null)
    printf "%-24s %6s %6s  %s...\n" "$p" "$a" "$s" "$d"
  done
}

uninstall() {
  if [[ ! -f "$MANIFEST" ]]; then
    echo -e "${YELLOW}No install manifest at $MANIFEST, nothing to remove.${RESET}"; exit 0
  fi
  local n=0
  while IFS= read -r f; do
    [[ -e "$f" ]] && rm -rf "$f" && n=$((n+1))
  done < "$MANIFEST"
  rm -f "$MANIFEST"
  echo -e "${GREEN}Removed $n installed paths.${RESET}"
  exit 0
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  --list) list_plugins; exit 0 ;;
  --uninstall) uninstall ;;
esac

if [[ "${1:-}" == "--all" ]]; then
  SELECTED=($ALL_PLUGINS)
  echo -e "${YELLOW}Installing every plugin. Combined subagent descriptions will be near"
  echo -e "the 15000-token delegation ceiling; expect weaker routing.${RESET}"
elif [[ $# -gt 0 ]]; then
  SELECTED=("$@")
else
  SELECTED=("${DEFAULT_SET[@]}")
fi

for p in "${SELECTED[@]}"; do
  [[ -d "plugins/$p" ]] || { echo -e "${RED}Error:${RESET} unknown plugin '$p'. Run --list."; exit 1; }
done

mkdir -p "$AGENTS" "$SKILLS" "$REFS"
: > "$MANIFEST.tmp"

n_agents=0; n_skills=0; n_refs=0
for p in "${SELECTED[@]}"; do
  # references first, so the rewrite target exists
  if [[ -d "plugins/$p/references" ]]; then
    rm -rf "${REFS:?}/$p"
    cp -R "plugins/$p/references" "$REFS/$p"
    echo "$REFS/$p" >> "$MANIFEST.tmp"
    n_refs=$((n_refs + $( { find "$REFS/$p" -type f 2>/dev/null || true; } | wc -l | tr -d ' ')))
  fi

  while IFS= read -r f; do
    dest="$AGENTS/$(basename "$f")"
    python3 - "$f" "$dest" "$REFS/$p" <<'PY'
import sys, pathlib
src, dest, refroot = sys.argv[1], sys.argv[2], sys.argv[3]
text = pathlib.Path(src).read_text(encoding="utf-8")
# ${CLAUDE_PLUGIN_ROOT} only expands inside an installed plugin. Outside one it is a
# literal string, so every bundled reference would silently fail to open.
text = text.replace("${CLAUDE_PLUGIN_ROOT}/references", refroot)
text = text.replace("${CLAUDE_PLUGIN_ROOT}", refroot.rsplit("/", 1)[0])
pathlib.Path(dest).write_text(text, encoding="utf-8")
PY
    echo "$dest" >> "$MANIFEST.tmp"
    n_agents=$((n_agents+1))
  done < <(find "plugins/$p/agents" -name '*.md' 2>/dev/null || true)

  while IFS= read -r d; do
    name=$(basename "$d")
    rm -rf "${SKILLS:?}/$name"
    cp -R "$d" "$SKILLS/$name"
    echo "$SKILLS/$name" >> "$MANIFEST.tmp"
    n_skills=$((n_skills+1))
  done < <(find "plugins/$p/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null || true)

  if [[ -f "plugins/$p/.mcp.json" ]]; then
    echo -e "${YELLOW}note:${RESET} $p ships an MCP server in plugins/$p/.mcp.json."
    echo "      Merge its mcpServers block into your project .mcp.json by hand;"
    echo "      this install path cannot wire MCP for you."
  fi
done

mv "$MANIFEST.tmp" "$MANIFEST"

echo
echo -e "${GREEN}Installed${RESET} $n_agents agents, $n_skills skills, $n_refs reference files"
echo -e "  agents      $AGENTS"
echo -e "  skills      $SKILLS"
echo -e "  references  $REFS"
echo -e "  manifest    $MANIFEST"
echo
echo -e "${CYAN}Plugins installed:${RESET} ${SELECTED[*]}"
echo
echo "Restart Claude Code for the changes to take effect."
echo "Re-run this script after a git pull; it is idempotent and replaces what it owns."
echo "Remove everything with: ./scripts/install-local.sh --uninstall"
