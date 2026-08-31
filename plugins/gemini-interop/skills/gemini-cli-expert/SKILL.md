---
name: gemini-cli-expert
description: "This skill should be used when working with Google's Gemini CLI: configuring `settings.json`, writing `GEMINI.md` context files, choosing and restricting tools, setting approval modes and Policy Engine rules, running headless or in plan mode, wiring MCP servers, or answering \"how does Gemini CLI do X\". Trigger phrases: \"gemini cli\", \"gemini-cli\", \"GEMINI.md\", \"gemini settings.json\", \"gemini extensions\", \"gemini skills\", \"run this with gemini\". Covers the CLI as a host. It does not cover authoring an extension (that is `gemini-extension-authoring`) or translating capabilities between hosts (that is `cross-host-parity`)."
---

# Gemini CLI

Google's Gemini CLI is an open-source terminal agent. It is the host that a Gemini-side
capability registry plugs into, the same way Claude Code hosts this repository's plugins.

All facts below are verified against the released `v0.57.0` tag of
`google-gemini/gemini-cli`, not against `main`.

## Version floor, check it first

Skills, sub-agents, hooks, the Policy Engine and `gemini extensions install` are all
recent. A CLI old enough to lack them fails silently: `gemini extensions --help` prints
the top-level help instead of erroring, so an absent subcommand looks like a usage
mistake.

```bash
gemini --version                    # anything below 0.50 predates most of this
npm view @google/gemini-cli dist-tags
npm install -g @google/gemini-cli@latest
```

Confirm the surface exists before writing anything against it:

```bash
gemini extensions list && gemini skills list --all
```

## Configuration hierarchy

Seven layers, each overriding the ones above it:

1. Default values, hardcoded in the application
2. System defaults file: `/etc/gemini-cli/system-defaults.json`, or `GEMINI_CLI_SYSTEM_DEFAULTS_PATH`
3. User settings file: `~/.gemini/settings.json`
4. Project settings file: `<project>/.gemini/settings.json`
5. **System settings file**: `/etc/gemini-cli/settings.json`, or `GEMINI_CLI_SYSTEM_SETTINGS_PATH`
6. Environment variables, including those loaded from `.env`
7. Command-line arguments

Layer 5 is the one people miss. It is a second system-wide file, distinct from the system
defaults at layer 2, and it sits **above** the user and project files rather than below
them, so it cannot be overridden by anything a user writes. It exists so that an
administrator can enforce settings on a managed workstation. On a managed machine, read it
before concluding a setting is being ignored.

Extensions contribute their own configuration at load time. Where an extension and a
`settings.json` both define an MCP server under the same key, `settings.json` wins.

The full key reference is in [references/settings-reference.md](references/settings-reference.md).

## Context files

`GEMINI.md` is the persistent instruction file, the counterpart of `CLAUDE.md`. The CLI
concatenates every file it finds, in this order:

1. `~/.gemini/GEMINI.md`, global
2. `GEMINI.md` in the workspace directories and their parents
3. Just-in-time: when a tool touches a directory, the CLI scans that directory and its
   ancestors up to a trusted root

Two properties worth knowing:

- **Imports.** `@./components/instructions.md` inside a `GEMINI.md` pulls that file in.
  Relative and absolute paths both work. This is how a long context file gets split.
- **The filename is configurable.** `context.fileName` accepts a list, so a repository
  can be read by both hosts:

  ```json
  { "context": { "fileName": ["AGENTS.md", "GEMINI.md"] } }
  ```

  Point it at a shared `AGENTS.md` when the same repository must brief both CLIs, and
  keep host-specific instructions in the host-specific file.

`/memory show` prints the concatenated result. `/memory reload` re-scans. When an
instruction appears not to apply, print the memory before assuming the model ignored it.

## Tools

Built-in tool names differ from Claude Code's and are snake_case. The ones that matter
when restricting an agent:

| Purpose | Tool |
|---|---|
| Read a file | `read_file` |
| Read several files at once | `read_many_files` |
| Write a file | `write_file` |
| Targeted edit | `replace` |
| Glob | `glob` |
| Content search | `grep_search` (legacy alias `search_file_content`) |
| List a directory | `list_directory` |
| Shell | `run_shell_command` |
| Fetch a URL | `web_fetch` |
| Search the web | `google_web_search` |
| Ask the user | `ask_user` |
| Track subtasks | `write_todos` |
| Load a skill | `activate_skill` |
| Enter and leave plan mode | `enter_plan_mode`, `exit_plan_mode` |

`read_many_files` has no Claude Code equivalent and is the preferred way to pull in a
set of files; Gemini's own behavioural evals assert on it rather than on repeated
`read_file` calls.

## Restricting what the model can do

Three mechanisms, in increasing order of authority:

- **`excludeTools`** in an extension manifest removes tools from the model's view, and
  supports argument-level blocks: `"excludeTools": ["run_shell_command(rm -rf)"]`.
- **`settings.json` tool configuration** governs the session.
- **The Policy Engine** evaluates `.toml` rules in five tiers: Default 1, Extension 2,
  Workspace 3, User 4, Admin 5. Extension-contributed rules land in tier 2, above the
  built-in defaults and below everything else. The CLI **ignores `allow` decisions and
  `yolo` configuration coming from an extension**, by design, so an extension can tighten
  and never loosen. **The Workspace tier is non-functional in v0.57.0** (issue #18186):
  a `.gemini/policies` directory in a project has no effect whatsoever.

See [references/tools-and-policy.md](references/tools-and-policy.md) for rule syntax and
the tiering rules.

## Skills

Gemini CLI implements the same Agent Skills standard this repository uses: a directory
with `SKILL.md`, `name` and `description` frontmatter, and optional `references/`,
`scripts/` and `assets/`.

Discovery tiers, lowest precedence first: built-in, extension, user
(`~/.gemini/skills/`), workspace (`.gemini/skills/`). Within the user and workspace
tiers, `.agents/skills/` takes precedence over `.gemini/skills/` and is the cross-tool
interoperable path.

One behavioural difference matters when porting: activation is an explicit
`activate_skill` tool call, and consent is **step 3 of every activation**, not a one-time
grant. `docs/cli/skills.md` lists the lifecycle as discovery, activation, consent,
injection, execution, and says nothing about remembering an earlier approval. The prompt
names the skill, its purpose and the directory it gains read access to.

That makes the friction worse than a first-run cost, not better. A pipeline that silently
loads eight skills on Claude Code produces eight prompts here, on every run that touches
them. Design for fewer, larger skills on the Gemini side, or preload the content through
`GEMINI.md` where it needs no consent at all.

```bash
gemini skills list --all
gemini skills install https://github.com/user/repo.git --path skills/my-skill
gemini skills link .                      # local development
```

## Sub-agents

Custom sub-agents are markdown files with YAML frontmatter in `.gemini/agents/` (project)
or `~/.gemini/agents/` (user). They are exposed to the main agent as a tool named after
the agent, and `@agent_name` at the start of a prompt forces one.

**Sub-agents cannot call other sub-agents.** Recursion protection blocks it even when the
agent holds the `*` tool wildcard. Any supervisor-dispatches-workers design has to move
the dispatch up into the main agent.

Built-ins: `codebase_investigator`, `cli_help`, `generalist`, and `browser_agent`
(disabled by default).

**There is no `gemini agents` command.** Verified by running `gemini --help` against the
installed 0.57.0 binary, not from the docs. The top-level command groups are `mcp`,
`extensions`, `skills`, `hooks` and `gemma`, plus `update` and the default `gemini
[query..]`. Sub-agents are file-based only: there is no terminal command that lists,
installs, validates or scaffolds one, so the only way to confirm a sub-agent was
discovered is to start a session and look for its tool.

`gemini hooks` and `gemini gemma` are in the binary but absent from the v0.57.0
`docs/cli/cli-reference.md` command table, which lists only `extensions` and `mcp`. Run
`gemini <group> --help` rather than trusting that table for coverage.

## Commands, plan mode, headless

- **Custom commands** are TOML, not markdown: `.gemini/commands/git/commit.toml` becomes
  `/git:commit`. Arguments are `{{args}}`, shell output is injected with `!{...}` and
  file content with `@{...}`. `/commands reload` picks up edits without a restart.
- **Plan mode** is a real tool pair, `enter_plan_mode` and `exit_plan_mode`, not a client
  mode. `web_fetch` requires explicit confirmation while in plan mode.
- **Headless** runs take `-p/--prompt`, and `-e/--extensions` limits which extensions
  load for that run, which is the cheapest way to isolate a capability under test.

## Diagnosing a capability that will not load

Work down this list before changing the capability itself.

1. `gemini --version`, against the floor above.
2. Restart the session. Extensions, agents and commands load at session start.
3. `/extensions list`, `/skills list`, `/help`. If it is absent, it was never discovered.
4. For an extension, the `name` in `gemini-extension.json` must equal the directory name,
   and the manifest must be at the root of the extension directory.
5. `/memory show` to confirm which context files actually loaded.
6. F12 opens the debug console in an interactive session, which shows tool calls and MCP
   server failures.
