#!/usr/bin/env bash
# End-to-end check that install-local.sh produces a working install on a machine
# that has never seen this registry. Runs against a throwaway CLAUDE_CONFIG_DIR,
# so it never touches the caller's real ~/.claude.
#
# What it asserts, in the order the failures actually bit us:
#   1. every installed agent's frontmatter still parses as YAML
#   2. no ${CLAUDE_PLUGIN_ROOT} survives, since it does not expand outside a plugin
#   3. every absolute reference path an installed file names actually exists
#   4. every relative references/ link resolves from its own directory
#   5. an agent whose body invokes skills carries the Skill tool
#   6. --uninstall removes exactly what it created

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
export CLAUDE_CONFIG_DIR="$TMP/claude"
mkdir -p "$CLAUDE_CONFIG_DIR"
fail=0
note() { printf '%-52s %s\n' "$1" "$2"; }

bash "$ROOT/scripts/install-local.sh" --all >"$TMP/install.log" 2>&1 || { cat "$TMP/install.log"; exit 1; }
tail -1 "$TMP/install.log" >/dev/null
note "install --all" "$(grep -o 'Installed.*' "$TMP/install.log" | head -1)"

python3 - "$CLAUDE_CONFIG_DIR" "$ROOT" <<'PY'
import glob, os, re, sys, yaml
root, repo = sys.argv[1], sys.argv[2]
agents = glob.glob(os.path.join(root, "agents", "*.md"))
skills = glob.glob(os.path.join(root, "skills", "*", "SKILL.md"))
bad = []

for p in agents + skills:
    text = open(p, encoding="utf-8").read()
    if text.startswith("---"):
        end = text.find("\n---", 3)
        try:
            fm = yaml.safe_load(text[3:end])
            if not isinstance(fm, dict):
                bad.append(("frontmatter not a mapping", p))
        except Exception as exc:
            bad.append(("frontmatter unparseable: %s" % str(exc).split("\n")[0], p))
    # Agents are the only class install-local.sh rewrites, so a surviving token
    # there means the rewrite missed it. A skill is copied verbatim, so the token
    # is only broken when it is used AS A PATH; a skill documenting the variable
    # (gemini-interop does) is correct content. validate_registry.py draws the
    # same line, and two gates disagreeing about it is worse than either rule.
    is_agent = os.path.dirname(p).endswith("agents")
    if "${CLAUDE_PLUGIN_ROOT}" in text and (
            is_agent or "${CLAUDE_PLUGIN_ROOT}/" in text):
        bad.append(("unexpanded ${CLAUDE_PLUGIN_ROOT}", p))
    # Anchoring this on /Users/ meant it never matched: the harness installs
    # into mktemp -d, which is /var/folders on macOS and /tmp in CI.
    for m in re.finditer(re.escape(root) + r"[^\s)`'\"]*", text):
        if not os.path.exists(m.group(0)):
            bad.append(("dangling absolute reference %s" % m.group(0), p))
    for m in re.finditer(r"[`(]\.?/?(references/[A-Za-z0-9._/-]+\.md)[`)]", text):
        if os.path.exists(os.path.join(os.path.dirname(p), m.group(1))):
            continue
        # A file owned by another plugin cannot be reached by a relative path.
        # It is only acceptable when the same line says whose plugin it is, so a
        # reader can find it; a bare path there would be unresolvable either way.
        line = next((l for l in text.splitlines() if m.group(1) in l), "")
        if re.search(r"the `[a-z0-9-]+` plugin", line):
            continue
        bad.append(("dangling relative reference %s" % m.group(1), p))

for p in agents:
    text = open(p, encoding="utf-8").read()
    end = text.find("\n---", 3)
    fm = {}
    try:
        fm = yaml.safe_load(text[3:end]) or {}
    except Exception:
        continue
    body = text[end:]
    tools = [t.strip() for t in str(fm.get("tools", "")).split(",")]
    if re.search(r"`Skill`|Skill tool|[Ii]nvoke the [^\n]{0,40}skill", body) and \
            fm.get("tools") and "Skill" not in tools:
        bad.append(("invokes skills without the Skill tool", p))

# Without this the harness is green on an empty install: it only checks
# properties of what it finds, so an installer that copies nothing passes.
want_agents = len(glob.glob(os.path.join(repo, "plugins/*/agents/**/*.md"), recursive=True))
want_skills = len(glob.glob(os.path.join(repo, "plugins/*/skills/*/SKILL.md")))
# Comparing installed against the tree is not enough on its own: with both
# empty the counts agree and the harness goes green. These floors are sanity
# bounds, well below the current 86 and 46, not exact expectations.
MIN_AGENTS, MIN_SKILLS = 50, 30
if want_agents < MIN_AGENTS or want_skills < MIN_SKILLS:
    bad.append(("the tree itself has only %d agents and %d skills, below the "
                "%d and %d floor: the harness would pass vacuously"
                % (want_agents, want_skills, MIN_AGENTS, MIN_SKILLS), "--all"))
if len(agents) != want_agents:
    bad.append(("installed %d agents, the tree has %d" % (len(agents), want_agents), "--all"))
if len(skills) != want_skills:
    bad.append(("installed %d skills, the tree has %d" % (len(skills), want_skills), "--all"))

print("checked %d agents, %d skills (tree has %d, %d)"
      % (len(agents), len(skills), want_agents, want_skills))
for reason, path in bad:
    print("  FAIL %s: %s" % (os.path.basename(path), reason))
sys.exit(1 if bad else 0)
PY
[ $? -eq 0 ] || fail=1

before=$(find "$CLAUDE_CONFIG_DIR" -type f | wc -l | tr -d ' ')
bash "$ROOT/scripts/install-local.sh" --uninstall >"$TMP/uninstall.log" 2>&1
left=$(find "$CLAUDE_CONFIG_DIR/agents" "$CLAUDE_CONFIG_DIR/skills" "$CLAUDE_CONFIG_DIR/registry-references" -type f 2>/dev/null | wc -l | tr -d ' ')
note "uninstall leaves nothing behind" "$before installed, $left left"
[ "$left" = "0" ] || fail=1

if [ "$fail" -eq 0 ]; then echo "clean-install check passed"; else echo "clean-install check FAILED"; fi
exit "$fail"
