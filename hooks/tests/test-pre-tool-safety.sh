#!/usr/bin/env bash
# Regression matrix for hooks/scripts/pre-tool-safety.sh.
#
# The rows that matter most are the ones that used to be wrong: the hook once
# matched the literal substring "rm -rf /", so every flag respelling of a
# filesystem wipe went through while an ordinary scratch-directory cleanup was
# blocked. Both directions are asserted here.

set -uo pipefail
HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/scripts/pre-tool-safety.sh"
pass=0 fail=0

check() { # $1 = command, $2 = blocked|allowed
  local rc
  python3 -c 'import json,sys;print(json.dumps({"tool_input":{"command":sys.argv[1]}}))' "$1" \
    | bash "$HOOK" >/dev/null 2>&1
  rc=$?
  local got=allowed; [ "$rc" = "2" ] && got=blocked
  if [ "$got" = "$2" ]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    printf 'FAIL  %-44s expected %s, got %s\n' "$1" "$2" "$got"
  fi
}

# Filesystem wipes: every flag spelling must be caught, not just "-rf".
check 'rm -rf /'                          blocked
check 'rm -fr /'                          blocked
check 'rm -r -f /'                        blocked
check 'rm -Rf /'                          blocked
check 'rm --recursive --force /'          blocked
check 'rm -rf --no-preserve-root /'       blocked
check 'rm --no-preserve-root -rf /'       blocked
check 'rm -rf -- /'                       blocked
check 'sudo rm -rf /*'                    blocked
check '/bin/rm -rf /'                     blocked
check 'echo ok && rm -rf /'               blocked
check 'rm -rf ~'                          blocked
check 'rm -rf $HOME'                      blocked
check 'rm -rf /usr'                       blocked

# Ordinary development work must not be blocked, or the team disables the hook.
check 'rm -rf /tmp/scratch'               allowed
check 'rm -rf ./build'                    allowed
check 'rm -rf node_modules'               allowed
check 'rm -rf ~/dev/claude-registry/tmp'  allowed
check 'rm file.txt'                       allowed
check 'echo "rm -rf /" >> notes.md'       allowed
check 'grep -r "rm -rf /" .'              allowed
check 'echo hi'                           allowed

# Non-rm patterns retained from the original hook.
check ':(){ :|:& };:'                     blocked
check 'dd if=/dev/zero of=/dev/sda'       blocked

printf '\n%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
