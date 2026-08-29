#!/usr/bin/env bash
# new-capability.sh
# Scaffold a new agent or skill inside a plugin, and create the feature branch.
#
# Usage:
#   ./scripts/new-capability.sh                                  # interactive
#   ./scripts/new-capability.sh --plugin dev-standards my-agent
#   ./scripts/new-capability.sh --plugin dev-standards --type skill my-skill

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
RED='\033[0;31m'; BOLD='\033[1m'; RESET='\033[0m'

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TYPE="agent"; NAME=""; PLUGIN=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --type)   TYPE="$2"; shift 2 ;;
    --plugin) PLUGIN="$2"; shift 2 ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) NAME="$1"; shift ;;
  esac
done

[[ "$TYPE" == "agent" || "$TYPE" == "skill" ]] || {
  echo -e "${RED}Error:${RESET} --type must be 'agent' or 'skill', got '$TYPE'"; exit 1; }

PLUGINS=$(find plugins -maxdepth 1 -mindepth 1 -type d -exec basename {} \; | sort)

if [[ -z "$PLUGIN" ]]; then
  echo -e "${BOLD}Available plugins:${RESET}"
  echo "$PLUGINS" | sed 's/^/  /'
  read -rp "Plugin: " PLUGIN
fi
[[ -d "plugins/$PLUGIN" ]] || { echo -e "${RED}Error:${RESET} unknown plugin '$PLUGIN'"; exit 1; }

if [[ -z "$NAME" ]]; then read -rp "Capability name (lowercase-with-hyphens): " NAME; fi
[[ "$NAME" =~ ^[a-z0-9]([a-z0-9-]*[a-z0-9])?$ ]] || {
  echo -e "${RED}Error:${RESET} name must be lowercase alphanumeric with hyphens"; exit 1; }
[[ "$NAME" == *anthropic* || "$NAME" == *claude* ]] && {
  echo -e "${RED}Error:${RESET} name contains a reserved word"; exit 1; }

BRANCH="feat/${TYPE}-${NAME}"
git rev-parse --verify "$BRANCH" >/dev/null 2>&1 \
  && echo -e "${YELLOW}Branch $BRANCH already exists, staying on it${RESET}" && git checkout "$BRANCH" \
  || git checkout -b "$BRANCH"

if [[ "$TYPE" == "agent" ]]; then
  DEST="plugins/$PLUGIN/agents/$NAME.md"
  [[ -e "$DEST" ]] && { echo -e "${RED}Error:${RESET} $DEST already exists"; exit 1; }
  mkdir -p "$(dirname "$DEST")"
  cat > "$DEST" <<EOF
---
name: $NAME
description: "Use this agent when <trigger condition>. <What it produces.> Do not use it for <adjacent case> (use <sibling-agent> instead)."
tools: Read, Grep, Glob
model: inherit
color: blue
---

## When to invoke

- **<Scenario name>.** <What the situation looks like and what the agent does.>
- **<Scenario name>.** <Same.>

## Role

<One paragraph: who this agent is and what it is authoritative for.>

## What you always do

- <Mandatory behaviour.>

## What you never do

- <Prohibition, with the reason when it is not obvious.>

## Skills

Load the following skills with the \`Skill\` tool when the task touches their domain:

- \`<skill-name>\` for <what it provides>

## Output format

<Exact structure the agent produces.>

## Quality criteria

Before responding, verify: <self-check.>
EOF
else
  DEST="plugins/$PLUGIN/skills/$NAME/SKILL.md"
  [[ -e "$DEST" ]] && { echo -e "${RED}Error:${RESET} $DEST already exists"; exit 1; }
  mkdir -p "$(dirname "$DEST")"
  TITLE=$(echo "$NAME" | tr '-' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')
  cat > "$DEST" <<EOF
---
name: $NAME
description: "This skill should be used when <situation>: <topics it covers>. Do not use it for <adjacent case> (use <sibling-skill> instead)."
---

# $TITLE

<Assume Claude is already smart. Only add what it does not already know.>

## <Topic>

<Rules, with concrete examples rather than abstract description.>

## Detailed references

- **<what is in the file>**: see [references/<file>.md](references/<file>.md)
EOF
  mkdir -p "plugins/$PLUGIN/skills/$NAME/references"
fi

EVALS="plugins/$PLUGIN/evals/$NAME"
mkdir -p "$EVALS"
cat > "$EVALS/evals.json" <<EOF
[
  {
    "skills": ["$NAME"],
    "query": "<a real task a user would ask>",
    "files": [],
    "expected_behavior": [
      "<observable behaviour 1>",
      "<observable behaviour 2>",
      "<observable behaviour 3>"
    ]
  }
]
EOF
cat > "$EVALS/triggers.json" <<EOF
{
  "should_trigger": [
    "<prompt that must activate $NAME>",
    "<another one, phrased differently>"
  ],
  "should_not_trigger": [
    "<near-miss prompt that must NOT activate $NAME>"
  ]
}
EOF

echo
echo -e "${GREEN}Created${RESET} $DEST"
echo -e "${GREEN}Created${RESET} $EVALS/{evals.json,triggers.json}"
echo -e "${CYAN}Branch${RESET}  $BRANCH"
echo
echo "Next:"
echo "  1. Write the evaluations first, then the capability."
echo "  2. Bump plugins/$PLUGIN/.claude-plugin/plugin.json version."
echo "  3. Add a docs/registry/CHANGELOG.md entry."
echo "  4. python3 .github/scripts/validate_registry.py"
