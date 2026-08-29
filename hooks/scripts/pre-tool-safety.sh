#!/usr/bin/env bash
# pre-tool-safety.sh
# Claude Code PreToolUse hook for Bash commands.
#
# Purpose: Block demonstrably destructive commands before they execute.
# Behavior:
#   exit 0  → allow the command to proceed
#   exit 2  → block the command; Claude Code shows stderr to the user
#
# Configuration in .claude/settings.json:
#   "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": ".claude/hooks/pre-tool-safety.sh"}]}]
#
# This script is intentionally conservative: it only blocks patterns with no
# legitimate use in normal development. Do not expand this list aggressively —
# overly restrictive hooks will be disabled by the team.
#
# The rm check parses the command instead of substring-matching "rm -rf /".
# That earlier form had an inverted safety profile, measured: it let through
# `rm -fr /`, `rm -r -f /` and `rm --no-preserve-root -rf /` because the flags
# were spelled differently, while blocking `rm -rf /tmp/scratch` because the
# target merely started with a slash. Flag order and spelling must not decide
# whether a filesystem wipe is caught.

set -euo pipefail

input=$(cat)

verdict=$(printf '%s' "$input" | python3 -c '
import json, os, re, shlex, sys

SEP = re.compile(r"\|\||&&|[;\n|&]")
# Wrappers that delegate to the real command; unwrap and keep inspecting.
WRAPPERS = {"sudo", "doas", "env", "nohup", "time", "command", "builtin", "exec"}
HOME = os.path.expanduser("~").rstrip("/")
# Top-level trees whose recursive removal is never routine work.
# /tmp is deliberately absent: it is the scratch area, and blocking paths
# under it is what made the previous version noisy enough to be ignored.
SYSTEM_ROOTS = {
    "/bin", "/boot", "/dev", "/etc", "/home", "/lib", "/lib64", "/opt",
    "/private", "/proc", "/root", "/sbin", "/srv", "/sys", "/usr", "/var",
    "/System", "/Applications", "/Library", "/Users", "/Volumes",
}

def dangerous_target(raw):
    t = raw.strip().strip("\"\x27")
    t = re.sub(r"/\*+$", "", t)          # /* and /** collapse to the parent
    t = os.path.expandvars(t)
    if t in ("~", "$HOME"):
        return True
    if t.startswith("~"):
        t = HOME + t[1:]
    t = t.rstrip("/")
    if t in ("", "/", "*"):               # bare / or a glob standing in for it
        return True
    return t == HOME or t in SYSTEM_ROOTS

def rm_is_destructive(tokens):
    recursive = force = no_preserve = False
    targets, only_targets = [], False
    for tok in tokens[1:]:
        if only_targets or not tok.startswith("-") or tok == "-":
            targets.append(tok)
            continue
        if tok == "--":
            only_targets = True
        elif tok.startswith("--"):
            flag = tok[2:].split("=")[0]
            recursive |= flag in ("recursive", "dir")
            force |= flag == "force"
            no_preserve |= flag == "no-preserve-root"
        else:
            recursive |= bool(set("rR") & set(tok[1:]))
            force |= "f" in tok[1:]
    if no_preserve and recursive:
        return True
    if not recursive:
        return False
    return any(dangerous_target(t) for t in targets)

try:
    command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
except Exception:
    command = ""
if not command:
    print("allow")      # unparseable input fails open, as before
    sys.exit(0)

for segment in SEP.split(command):
    segment = segment.strip()
    if not segment:
        continue
    try:
        tokens = shlex.split(segment)
    except ValueError:
        continue        # unbalanced quotes: the regex pass below still applies
    while tokens and (tokens[0] in WRAPPERS or "=" in tokens[0].split("/")[0]):
        tokens.pop(0)
    if tokens and os.path.basename(tokens[0]) == "rm" and rm_is_destructive(tokens):
        print("block\trecursive rm targeting a system root, the home directory "
              "or / (flag spelling and order do not matter here)")
        sys.exit(0)
print("allow")
' 2>/dev/null || echo "allow")

if [[ "$verdict" == block* ]]; then
  reason="${verdict#block?}"
  echo "BLOCKED: $reason" >&2
  echo "Command was: $(printf '%s' "$input" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)" >&2
  exit 2
fi

command=$(printf '%s' "$input" | python3 -c "
import json, sys
try:
    print(json.load(sys.stdin).get('tool_input', {}).get('command', ''))
except Exception:
    print('')
" 2>/dev/null || echo "")

if [[ -z "$command" ]]; then
  exit 0
fi

# Non-rm patterns with no legitimate use in a development session.
BLOCKED_PATTERNS=(
  "> */etc/"
  "dd +if=/dev/zero"
  "mkfs\."
  ":\(\)\{ *:\|:& *\};:"   # fork bomb
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
  if echo "$command" | grep -qiE "$pattern" 2>/dev/null; then
    echo "BLOCKED: This command matches a safety pattern: '$pattern'" >&2
    echo "Command was: $command" >&2
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
    if [[ -d ".claude" ]]; then
      echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] WARNING: $command" >> ".claude/safety-warnings.log" 2>/dev/null || true
    fi
    exit 0
  fi
done

exit 0
