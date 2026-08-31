# Gemini CLI tools and the Policy Engine

Verified against `google-gemini/gemini-cli` at tag `v0.57.0`.

## Contents

- [Built-in tools](#built-in-tools)
- [Three ways to restrict a tool](#three-ways-to-restrict-a-tool)
- [Policy Engine rule schema](#policy-engine-rule-schema)
- [Priority and tiers](#priority-and-tiers)
- [Why an extension cannot grant itself permission](#why-an-extension-cannot-grant-itself-permission)

## Built-in tools

| Category | Tools |
|---|---|
| Execution | `run_shell_command` |
| File system | `glob`, `grep_search`, `list_directory`, `read_file`, `read_many_files`, `replace`, `write_file` |
| Interaction | `ask_user`, `write_todos` |
| MCP | `list_mcp_resources`, `read_mcp_resource` |
| Memory | `activate_skill`, `get_internal_docs` |
| Planning | `enter_plan_mode`, `exit_plan_mode` |
| Web | `google_web_search`, `web_fetch` |
| System | `complete_task`, available only inside a sub-agent |

`grep_search` carries the legacy alias `search_file_content`. Both resolve; prefer the
current name in new material so a future alias removal does not silently drop a rule.

`read_many_files` is the batching read. Google's own behavioural evals assert that the
model reaches for it instead of issuing sequential `read_file` calls, so a ported agent
body that says "read each file in turn" is working against the host.

`web_fetch` can reach local and private network addresses, including `localhost`. In
plan mode it requires explicit confirmation. Treat it as a network egress point when
writing policy.

## Three ways to restrict a tool

In increasing order of authority:

1. **`excludeTools` in an extension manifest.** Removes the tool from the model's view
   for sessions where the extension is active. Supports argument-level blocks:

   ```json
   { "excludeTools": ["run_shell_command(rm -rf)"] }
   ```

   This is a prefix match on the command, not a shell-aware parse. `rm -rf` does not
   match `rm -fr`, and it does not match `sudo rm -rf`. Use it as one layer, never as
   the only one.

2. **`settings.json`.** Session-level tool configuration, including the sandbox keys.

3. **The Policy Engine.** TOML rules, evaluated highest priority first, first match wins.

## Policy Engine rule schema

```toml
[[rule]]
# A tool name, or an array of names. Wildcards: "*", "mcp_server_*", "mcp_*_toolName".
toolName = "run_shell_command"

# Optional. Restricts the rule to calls made by one named subagent.
# The key is `subagent`. There is no `agentName` key: a misspelling here does not
# error, it produces a rule with no subagent restriction that applies to every caller.
subagent = "codebase_investigator"

# Optional. Restricts the rule to one MCP server.
mcpName = "my_server"

# Optional. Regex tested against a stable JSON rendering of the arguments.
argsPattern = '"command":"git push'

# Sugar for toolName = "run_shell_command" plus an argsPattern.
# commandPrefix = ["git push", "npm publish"]
# commandRegex  = 'rm\s+-[rRf]{2}'

# "allow", "deny" or "ask_user".
decision = "ask_user"

# 0 to 999.
priority = 100
```

Two syntax traps:

- `commandRegex` is tested against the JSON representation, which begins
  `{"command":"`. A leading `^` therefore anchors to the JSON, not to the command. Leave
  it off.
- `commandPrefix` and `commandRegex` are mutually exclusive in one rule.

Safety checkers are declared alongside rules:

```toml
[[safety_checker]]
mcpName = "my_server"
toolName = "write_data"
priority = 200
[safety_checker.checker]
type = "in-process"
name = "allowed-path"
required_context = ["environment"]
```

## Priority and tiers

Rules live in five tiers. Each tier has a base number, and the numeric `priority` inside
the TOML file (0 to 999) orders rules within that tier:

`final_priority = tier_base + (toml_priority / 1000)`

So a tier always beats a lower tier no matter what `priority` the lower tier's rule sets.

| Tier | Base | Source |
|---|---|---|
| Default | 1 | built-in rules shipped with the CLI |
| Extension | 2 | an extension's `policies/*.toml` |
| Workspace | 3 | `$WORKSPACE_ROOT/.gemini/policies/*.toml`, **currently disabled** |
| User | 4 | `~/.gemini/policies/*.toml` |
| Admin | 5 | system policy directories, plus `--admin-policy` and `adminPolicyPaths` |

**The Workspace tier does not work in v0.57.0.** `docs/reference/policy-engine.md` carries
this warning: the Workspace tier is currently non-functional, policies in a workspace's
`.gemini/policies` directory have no effect at all, tracked as issue #18186, and the
documented workaround is to use User or Admin policies instead. A committed project policy
file therefore loads nothing and warns about nothing. Do not ship a capability whose safety
depends on one.

An extension contributes at tier 2, second-lowest. Workspace, user and admin policy all
override it, and it only overrides the built-in defaults.

Two upstream inconsistencies to expect when reading the source doc: the prose above the
table still says "three tiers" while the table lists five, and the worked examples below it
still use the pre-Extension numbering (Workspace 2, User 3, Admin 4) and the system-policy
section still calls Admin "Tier 4". The table and the formula are the normative pair; the
examples are stale.

Admin policy loads from `/etc/gemini-cli/policies` (Linux),
`/Library/Application Support/GeminiCli/policies` (macOS) or
`C:\ProgramData\gemini-cli\policies` (Windows). The standard directory is subject to strict
ownership checks and is ignored outright if they fail: root-owned and not group- or
world-writable on Linux and macOS. Supplemental admin paths given through `--admin-policy`
or the `adminPolicyPaths` setting are exempt from those checks, but are ignored entirely
whenever any `.toml` file already exists in the standard system location.

## Why an extension cannot grant itself permission

Gemini CLI **ignores every `allow` decision and every `yolo` configuration that comes
from an extension policy file**. An extension can only tighten.

This is the security property to preserve when porting from Claude Code. A Claude Code
plugin that ships a permissive `permissions.allow` list to smooth a workflow has no
equivalent on the Gemini side, and attempting one produces a policy file that loads,
reports no error, and does nothing. Port the deny rules; drop the allow rules and say so
in the extension's `GEMINI.md` so the user knows to approve interactively.
