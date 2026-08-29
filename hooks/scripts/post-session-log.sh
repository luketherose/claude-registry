#!/usr/bin/env bash
# post-session-log.sh
# Claude Code Stop hook.
#
# Purpose: Append a session end record to a local audit log.
# This is useful for teams that want a basic record of when Claude Code sessions
# were active on a project (for compliance or awareness purposes).
#
# Behavior: Always exits 0. Never blocks. Failure is silent.
#
# Output: Appends one line to .claude/session-log.txt
# Format: ISO8601 timestamp | working directory | stop reason
#
# Configuration in .claude/settings.json:
#   "Stop": [{"hooks": [{"type": "command", "command": ".claude/hooks/post-session-log.sh"}]}]

set -uo pipefail

# Read JSON input from stdin
input=$(cat 2>/dev/null || echo "{}")

# Extract stop reason
stop_reason=$(echo "$input" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('stop_reason', 'unknown'))
except Exception:
    print('unknown')
" 2>/dev/null || echo "unknown")

# Create .claude directory if it doesn't exist
mkdir -p ".claude" 2>/dev/null || true

# Append to session log
{
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | $(pwd) | stop_reason=${stop_reason}"
} >> ".claude/session-log.txt" 2>/dev/null || true

# Always exit 0 — this hook must never block Claude Code
exit 0
