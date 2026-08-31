# Gemini CLI commands, hooks and policies

Verified against `google-gemini/gemini-cli` at tag `v0.57.0`.

## Contents

- [Custom commands](#custom-commands)
- [Argument handling](#argument-handling)
- [Injection order](#injection-order)
- [Hooks](#hooks)
  - [Hook environment](#hook-environment)
  - [Hook trust and fingerprinting](#hook-trust-and-fingerprinting)
- [Hook events](#hook-events)
- [Policies](#policies)

## Custom commands

TOML files, discovered from `~/.gemini/commands/` (user), `<project>/.gemini/commands/`
(project) and an extension's `commands/`. Project beats user; extension loses to both.

The file path becomes the command name, with subdirectories producing a colon namespace:

| File | Command |
|---|---|
| `commands/test.toml` | `/test` |
| `commands/git/commit.toml` | `/git:commit` |

```toml
description = "Generates a Conventional Commit message from the staged diff."
prompt = """
Generate a Conventional Commit message for this diff:

!{git diff --staged}
"""
```

`prompt` is the only required field. `description` is optional and shows in `/help`;
without it the CLI generates one from the filename, which is always worse.

`/commands list` shows the files. `/commands reload` picks up edits without restarting,
which is the one part of the extension surface that does not need a session restart.

## Argument handling

`{{args}}` is replaced with whatever the user typed after the command.

- **Outside** a `!{...}` block, arguments are inserted raw.
- **Inside** a `!{...}` block, they are shell-escaped automatically.

Both happen in the same prompt when both forms appear, so a single invocation can show
the user's phrase verbatim in the instructions and pass it safely to a shell in the same
breath:

```toml
prompt = """
Summarise findings for pattern `{{args}}`.

!{grep -rn {{args}} .}
"""
```

When `{{args}}` does not appear anywhere in the prompt, the CLI falls back to default
argument handling. Three details, all of which the docs are explicit about:

1. It appends **the full command you typed**, including the leading slash and the command
   name, not just the arguments. `/changelog 1.2.0 added "New feature"` appends that entire
   string. A prompt that says "parse the version from the user's input" has to expect the
   command name in front of it.
2. The separator is **two newlines**, which is one blank line, not two.
3. When no arguments are supplied at all, for example a bare `/mycommand`, **nothing is
   appended**. The prompt is sent exactly as written. A prompt whose instructions assume
   trailing input will read as truncated in that case, so give it a no-argument branch.

This is the mode to use when the command should parse a structured invocation itself, and
the reason a prompt in this mode should state where the input will appear, as the upstream
`changelog.toml` example does with a line telling the model the raw command is appended
below the instructions.

## Injection order

1. `@{path}` file content injection
2. `!{command}` shell execution
3. `{{args}}` substitution

`@{...}` respects `.gitignore` and `.geminiignore`, traverses directories recursively,
and supports multimodal files. Braces must balance in both forms; the parser handles
nesting but not an unmatched brace.

The CLI runs a security check on the fully resolved shell command and asks the user to
confirm it. A command whose `!{...}` block is dynamic will prompt on every invocation.

## Hooks

Hooks live in `hooks/hooks.json` in an extension, or under a `hooks` key in
`settings.json`. They are never declared in `gemini-extension.json`.

```json
{
  "BeforeTool": [
    {
      "matcher": "run_shell_command",
      "sequential": true,
      "hooks": [
        { "type": "command", "name": "shell-safety", "command": "${extensionPath}/hooks/safety.sh", "timeout": 5000 }
      ]
    }
  ]
}
```

| Field | Level | Notes |
|---|---|---|
| `matcher` | definition | regex for tool events, exact string for lifecycle events |
| `sequential` | definition | `false` runs the group in parallel |
| `type` | configuration | only `"command"` today |
| `command` | configuration | the shell command |
| `name` | configuration | shown in logs and CLI listings |
| `timeout` | configuration | **milliseconds**, default 60000 |
| `description` | configuration | free text |

Protocol: JSON on stdin, JSON on stdout, logs on stderr. Exit `0` means the stdout JSON
is applied; exit `2` blocks the action and stderr becomes the reason; any other code is
a non-fatal warning. **Nothing but the final JSON may go to stdout.**

Every hook receives `session_id`, `transcript_path`, `cwd`, `hook_event_name` and
`timestamp`. Common output fields are `systemMessage`, `suppressOutput`, `continue`,
`stopReason`, `decision` and `reason`.

`BeforeTool` additionally accepts `hookSpecificOutput.tool_input`, which merges into and
overrides the model's arguments before the tool runs. `decision: "deny"` blocks the tool
and sends `reason` to the agent as a tool error, so the turn continues; `continue: false`
kills the whole agent loop.

### Hook environment

The environment is sanitized down to five variables:

| Variable | Contents |
|---|---|
| `GEMINI_PROJECT_DIR` | absolute path to the project root |
| `GEMINI_PLANS_DIR` | absolute path to the plans directory |
| `GEMINI_SESSION_ID` | unique ID for the current session |
| `GEMINI_CWD` | current working directory |
| `CLAUDE_PROJECT_DIR` | alias of the project root, provided for compatibility |

Anything else a hook script expects from the user's shell is absent. Declare what the
extension needs through the manifest `settings` array, the same allowlist that governs MCP
servers.

### Hook trust and fingerprinting

Hooks run arbitrary code with the user's privileges, and project-level hooks are the risky
case when a repository is not trusted. Gemini **fingerprints** project hooks: if a hook's
`name` or `command` changes, for example after a `git pull`, it is treated as a new and
untrusted hook and the user is warned again before it executes.

That has a practical consequence for an extension author. Renaming a hook, or refactoring
its command line, costs every existing user a fresh trust prompt. Keep `name` and `command`
stable across releases and put the churn inside the script the command points at, which is
not fingerprinted.

There is also an official migration command for this layer,
`gemini hooks migrate --from-claude`, verified against the installed 0.57.0 binary rather
than the docs, where the whole `gemini hooks` group is absent. Use it as the starting point
when porting a Claude Code hooks block, then check the timeout units by hand.

## Hook events

| Event | Fires |
|---|---|
| `BeforeTool` | before a tool is invoked |
| `AfterTool` | after a tool returns |
| `BeforeAgent` | before the agent loop starts on a turn |
| `AfterAgent` | after the agent finishes a turn |
| `BeforeModel` | before a model request |
| `BeforeToolSelection` | before the model picks a tool |
| `AfterModel` | after a model response |
| `SessionStart` | session opens |
| `SessionEnd` | session closes |
| `Notification` | a notification is raised |
| `PreCompress` | before context compression |

## Policies

TOML files in `policies/`, loaded automatically, contributed at tier 2. See the
`gemini-cli-expert` skill's `references/tools-and-policy.md` for the rule schema.

The one rule to remember while authoring: `allow` decisions and `yolo` configuration
coming from an extension are ignored. An extension tightens or it does nothing.
