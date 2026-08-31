# Claude Code to Gemini CLI, field by field

Verified against `google-gemini/gemini-cli` at tag `v0.57.0` and against this
repository's own conventions in `CLAUDE.md`.

## Contents

- [Sub-agent frontmatter](#sub-agent-frontmatter)
- [Tool names](#tool-names)
- [Model selection](#model-selection)
- [Hook events](#hook-events)
- [Hook output fields](#hook-output-fields)
- [Hook environment, and the supported migration path](#hook-environment-and-the-supported-migration-path)
- [Custom commands](#custom-commands)
- [Discovery paths](#discovery-paths)
- [Manifest fields](#manifest-fields)
- [Evaluations](#evaluations)
- [Traps that produce no error](#traps-that-produce-no-error)

## Sub-agent frontmatter

| Claude Code | Gemini CLI | Notes |
|---|---|---|
| `name` | `name` | Gemini restricts it to lowercase, digits, hyphens and underscores, and uses it as the tool name |
| `description` | `description` | same role: it is what the parent routes on |
| `tools` | `tools` | different names, see below. Gemini supports `*`, `mcp_*`, `mcp_<server>_*` wildcards |
| `model` | `model` | Gemini defaults to `inherit` when omitted, same as Claude Code |
| `effort` | no equivalent | drop it |
| `color` | no equivalent | drop it |
| `background` | no equivalent | drop it |
| `experimental.cacheTtl` | no equivalent | drop it |
| `skills` (preload) | no equivalent | preload through the extension `GEMINI.md` instead |
| no equivalent | `kind` | `local` or `remote`, defaults to `local` |
| no equivalent | `temperature` | 0.0 to 2.0, defaults to 1 |
| no equivalent | `max_turns` | defaults to 30, a hard stop |
| no equivalent | `timeout_mins` | defaults to 10 |
| no equivalent | `mcpServers` | inline MCP servers isolated to this agent |

Omitting `tools` in Gemini inherits every tool from the parent session, the opposite of
treating an empty list as an empty allowlist. Be explicit.

Nesting differs: this registry stores agents at `agents/<domain>/<name>.md`. Gemini
documents a flat `agents/*.md`. Flatten on port and keep the domain in the name.

## Tool names

| Claude Code | Gemini CLI |
|---|---|
| `Read` | `read_file` |
| `Write` | `write_file` |
| `Edit` | `replace` |
| `Glob` | `glob` |
| `Grep` | `grep_search` |
| `Bash` | `run_shell_command` |
| `WebFetch` | `web_fetch` |
| `WebSearch` | `google_web_search` |
| `TodoWrite` | `write_todos` |
| `AskUserQuestion` | `ask_user` |
| `Skill` | `activate_skill` |
| `ExitPlanMode` | `exit_plan_mode` |
| `Agent` | none, and sub-agents cannot nest |
| `NotebookEdit` | none |
| none | `read_many_files` |
| none | `list_directory` |
| none | `enter_plan_mode` |
| none | `get_internal_docs` |

`read_many_files` is not cosmetic. Google's behavioural evals assert that the model
batches through it rather than issuing sequential `read_file` calls, so an agent body
that instructs "read each file in turn" is fighting the host. Rewrite those instructions
on port.

## Model selection

This registry's policy, in `CLAUDE.md`, maps as follows.

| Class | Claude Code | Gemini CLI |
|---|---|---|
| Supervisors, challengers, auditors, personas | `opus` plus `effort: high` | the strongest available Gemini model, and a raised `max_turns` |
| User-facing agents | `inherit` | omit `model` |
| Pipeline workers in fan-out | `sonnet` | a flash-class model |

There is no `effort` on the Gemini side. Where `effort: high` was carrying the intent
"let this one think", the closest levers are `max_turns` and `temperature`, and neither
is equivalent. Do not pretend the mapping is clean: record in the ported agent that the
effort hint was dropped.

Do not hardcode a Gemini model string in ported material. Model identifiers churn faster
than the rest of the surface; name the class in the body and set the identifier once, in
`settings.json` or `agents.overrides`.

## Hook events

| Claude Code | Gemini CLI |
|---|---|
| `PreToolUse` | `BeforeTool` |
| `PostToolUse` | `AfterTool` |
| `UserPromptSubmit` | `BeforeAgent` |
| `Stop` | `AfterAgent` |
| `PreCompact` | `PreCompress` |
| `SessionStart` | `SessionStart` |
| `SessionEnd` | `SessionEnd` |
| `Notification` | `Notification` |
| `SubagentStop` | no equivalent |
| no equivalent | `BeforeModel`, `AfterModel`, `BeforeToolSelection` |

## Hook output fields

The transport is the same: JSON on stdin, JSON on stdout, logs on stderr, exit `2` to
block with stderr as the reason. The payload differs.

| Purpose | Claude Code | Gemini CLI |
|---|---|---|
| Block the tool | `permissionDecision: "deny"` | `decision: "deny"` (alias `"block"`) |
| Explain the block | `permissionDecisionReason` | `reason` |
| Rewrite the arguments | not available | `hookSpecificOutput.tool_input`, merged over the model's |
| Kill the whole loop | not available | `continue: false` plus `stopReason` |
| Message the user | `systemMessage` | `systemMessage` |
| Timeout unit | **seconds** | **milliseconds** |

The timeout unit is the trap. A `timeout: 5` copied from Claude Code gives a Gemini hook
five milliseconds, which times out before the interpreter starts. A `timeout: 5000`
copied the other way gives Claude Code an eighty-three minute hook. Neither errors.

## Hook environment, and the supported migration path

Hooks run with a sanitized environment. Gemini provides exactly five variables:

| Variable | Contents |
|---|---|
| `GEMINI_PROJECT_DIR` | absolute path to the project root |
| `GEMINI_PLANS_DIR` | absolute path to the plans directory |
| `GEMINI_SESSION_ID` | unique ID for the current session |
| `GEMINI_CWD` | current working directory |
| `CLAUDE_PROJECT_DIR` | **compatibility alias**, documented as such in `docs/hooks/index.md` |

`CLAUDE_PROJECT_DIR` is a deliberate interop affordance, and it is the reason a Claude Code
hook script that resolves paths from it usually runs unmodified on Gemini. Do not rewrite
those references during a port unless the script has other reasons to change. Everything
else about the Claude Code hook environment is absent, so a script reading any other
`CLAUDE_*` variable gets an empty string, not an error.

The hook layer also has an **official migration command**, which the rest of the surface
does not:

```bash
gemini hooks migrate --from-claude
```

Its help text reads "Migrate hooks from Claude Code to Gemini CLI". This is verified by
running `gemini hooks migrate --help` against the installed 0.57.0 binary, not from the
docs: the whole `gemini hooks` command group is absent from the v0.57.0 documentation tree,
including `docs/cli/cli-reference.md`. Run it and diff the result rather than translating a
hooks block by hand, then check the timeout units in the output, because that is the one
conversion whose result looks plausible either way.

A validation counterpart also exists on the extension side, documented at
`docs/cli/cli-reference.md`:

| Purpose | Claude Code | Gemini CLI |
|---|---|---|
| Validate the distribution unit | `claude plugin validate <path>` | `gemini extensions validate <path>` |
| Migrate hooks | none | `gemini hooks migrate --from-claude` (binary only, undocumented) |

## Custom commands

| Aspect | Claude Code | Gemini CLI |
|---|---|---|
| Format | markdown with frontmatter | TOML |
| Body key | the markdown body | `prompt` |
| Help text | `description` frontmatter | `description` key |
| All arguments | `$ARGUMENTS` | `{{args}}` |
| Positional arguments | `$1` to `$9` | none, parse `{{args}}` in the prompt |
| Shell injection | `!` prefixed line with `allowed-tools` | `!{...}` inline, auto shell-escaped |
| File injection | `@path` | `@{path}` |
| Namespacing | directory | directory, colon separated |
| Collision | plugin qualified | extension prefixed with a dot, `/ext.cmd` |
| Reload | restart | `/commands reload` |

Gemini shell-escapes `{{args}}` inside `!{...}` and leaves it raw outside, in the same
prompt. Claude Code has no equivalent split, so a ported command that interpolates user
input into a shell line needs the quoting checked by hand.

## Discovery paths

| Scope | Claude Code | Gemini CLI |
|---|---|---|
| User skills | `~/.claude/skills/` | `~/.gemini/skills/` or `~/.agents/skills/` |
| Workspace skills | `.claude/skills/` | `.gemini/skills/` or `.agents/skills/` |
| User agents | `~/.claude/agents/` | `~/.gemini/agents/` |
| Workspace agents | `.claude/agents/` | `.gemini/agents/` |
| User commands | `~/.claude/commands/` | `~/.gemini/commands/` |
| Settings | `~/.claude/settings.json` | `~/.gemini/settings.json` |
| Installed units | `~/.claude/plugins/` | `~/.gemini/extensions/` |

Skill precedence is inverted between the two layers on the Gemini side: for skills,
workspace beats user beats extension beats built-in. For commands, extension loses to
both user and project.

## Manifest fields

| `plugin.json` | `gemini-extension.json` |
|---|---|
| `name` | `name`, and it must equal the directory name |
| `description` | `description` |
| `version` | `version`, keep equal to the release tag |
| `author` | no equivalent |
| `repository` | no equivalent |
| `license` | no equivalent |
| `keywords` | no equivalent, the gallery indexes the GitHub topic instead |
| `category` | no equivalent |
| MCP wiring | `mcpServers` inline |
| no equivalent | `contextFileName` |
| no equivalent | `excludeTools` |
| no equivalent | `settings[]` for declared env vars and secrets |
| no equivalent | `migratedTo` |
| no equivalent | `themes[]` |
| no equivalent | `plan.directory` |

## Evaluations

The Claude Code column is this repository's own convention, documented in `CLAUDE.md` and
`docs/registry/evals-guide.md`. Both files live at
`plugins/<plugin>/evals/<capability-name>/`, where the directory name is the agent
filename without `.md`, or the skill directory name.

| Aspect | Claude Code | Gemini CLI |
|---|---|---|
| Harness | `claude plugin eval` | EDK, vitest |
| Trigger cases | `triggers.json`, a list of `{query, should_trigger, description}` | no direct equivalent |
| Behavioural cases | `evals.json`, a list of `{agent, query, files, expected_behavior}` | `evals/*.eval.ts` |
| Coverage rule | every agent and every skill carries `triggers.json`; `evals.json` is agents only | one eval file per capability under test |
| Assertion style | `expected_behavior` strings scored by reading the output | `rig.waitForToolCall`, assert on tool calls |
| Validator | `.github/scripts/validate_registry.py`, function `validate_evals()` | `npm run eval:validate` |
| Flake policy | none stated | new evals start `USUALLY_PASSES`, promoted from nightly data |

There are no separate grader files on the Claude side of this registry: the grading
criteria are the `expected_behavior` strings inside `evals.json`, and `description` inside
`triggers.json` restates the query without naming the capability that should win.

The two harnesses do not converge. What does port is the **corpus**: the queries, the
should-trigger flags and the expected behaviours are host-independent facts about the
capability. Keep them in a neutral JSON file and generate both harnesses from it, rather
than maintaining two sets of prompts that drift.

Gemini's rules worth adopting on the Claude side regardless: assert on tool calls rather
than prose, never restrict the default toolset inside an eval, and run a new case three
times before trusting it.

## Traps that produce no error

Ranked by how long each one takes to find.

1. **Hook `timeout` unit**, seconds against milliseconds.
2. **`${extensionPath}` in a `SKILL.md`**. Gemini substitutes it only in
   `gemini-extension.json` and `hooks/hooks.json`. Elsewhere it stays literal.
3. **Extension `name` not equal to the directory name.** The extension does not load and
   nothing points at the manifest.
4. **Omitted `tools` in a Gemini agent.** It inherits everything rather than nothing.
5. **A ported supervisor that dispatches.** It runs, and silently does the work itself.
6. **`allow` rules in an extension policy.** Loaded, ignored, no warning.
7. **An undeclared environment variable.** Empty at runtime, because the extension
   environment is an allowlist.
8. **A skill that shadows another by name.** Higher tier wins with no message.
