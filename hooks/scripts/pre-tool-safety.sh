#!/usr/bin/env bash
# pre-tool-safety.sh
# Claude Code PreToolUse hook for Bash commands.
#
# Purpose: Block demonstrably destructive commands before they execute.
# Behavior:
#   exit 0  → allow the command to proceed
#   exit 2  → block the command; Claude Code will show the message to the user
#
# Configuration in .claude/settings.json:
#   "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": ".claude/hooks/pre-tool-safety.sh"}]}]
#
# This script is intentionally conservative: it only blocks patterns with no
# legitimate use in normal development. Do not expand this list aggressively —
# overly restrictive hooks will be disabled by the team.

set -euo pipefail

# Read JSON input from stdin
input=$(cat)

# Extract the bash command from the JSON input
# Uses python3 for reliable JSON parsing (available in all target environments)
command=$(echo "$input" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('tool_input', {}).get('command', ''))
except Exception:
    print('')
" 2>/dev/null || echo "")

if [[ -z "$command" ]]; then
  # Could not parse input — allow through (fail open, not closed)
  exit 0
fi

# Patterns that are blocked unconditionally
# These have no legitimate use in normal development sessions
BLOCKED_PATTERNS=(
  "rm -rf /"
  "rm -rf ~"
  "rm -rf \$HOME"
  "> /etc/"
  "dd if=/dev/zero"
  "mkfs\."
  ":(){ :|:& };:"   # fork bomb
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
  if echo "$command" | grep -qiE "$pattern" 2>/dev/null; then
    echo "BLOCKED: This command matches a safety pattern: '$pattern'" >&2
    echo "Command was: $command" >&2
    # Output structured block decision for Claude Code
    echo '{"decision": "block", "reason": "Command matches a destructive pattern that is never permitted in a development session."}'
    exit 2
  fi
done

# Patterns that trigger a warning (logged) but are NOT blocked
# The team chose to warn rather than block because these commands have legitimate uses
WARNING_PATTERNS=(
  "DROP TABLE"
  "DROP DATABASE"
  "TRUNCATE TABLE"
  "DELETE FROM.*WHERE.*1=1"
  "git push.*--force"
  "git reset --hard"
  "git clean -fd"
)

for pattern in "${WARNING_PATTERNS[@]}"; do
  if echo "$command" | grep -qiE "$pattern" 2>/dev/null; then
    echo "WARNING: Potentially destructive command detected: $command" >&2
    # Log to audit file if it exists
    if [[ -d ".claude" ]]; then
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] WARNING: $command" >> ".claude/safety-warnings.log" 2>/dev/null || true
    fi
    # Allow through — just log the warning
    exit 0
  fi
done

# All other commands: allow
exit 0
