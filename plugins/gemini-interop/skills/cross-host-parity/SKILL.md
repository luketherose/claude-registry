---
name: cross-host-parity
description: "This skill should be used when translating a capability between Claude Code and Gemini CLI in either direction, or when deciding whether something can be translated at all: mapping plugins to extensions, agent frontmatter fields, tool names, hook events, path variables, command formats and eval harnesses. Trigger phrases: \"port this to gemini\", \"gemini equivalent\", \"does this work in gemini cli\", \"twin registry\", \"parity\", \"mirror this capability\", \"convert the plugin to an extension\". Covers the mapping and the four structures that have no counterpart. It does not cover the mechanical mirroring procedure itself (that is `capability-parity-sync`)."
---

# Claude Code and Gemini CLI parity

Both hosts are terminal agents with plugins, skills, sub-agents, hooks, MCP servers and
context files. The overlap is large enough that most material is portable and small
enough that four structures are not. Know which is which before starting.

Verified against `google-gemini/gemini-cli` at tag `v0.57.0`.

## The one thing that is already identical

**Agent Skills are the same standard on both hosts.** Both implement agentskills.io: a
directory containing `SKILL.md` with `name` and `description` frontmatter, plus optional
`references/`, `scripts/` and `assets/`. Gemini CLI additionally honours `.agents/skills/`
as an explicitly cross-tool discovery path.

A skill in this registry needs at most two mechanical edits to run on Gemini CLI:

1. `${CLAUDE_PLUGIN_ROOT}` becomes a plain relative path. It cannot become
   `${extensionPath}`: Gemini substitutes that only inside `gemini-extension.json`
   and `hooks/hooks.json`, never in a skill body.
2. Claude Code tool names in prose become Gemini tool names.

Everything else about a skill travels unchanged. This is why the skill layer is the right
place to hold shared knowledge and the agent layer is not.

## The four things that do not map

### 1. Sub-agents cannot dispatch sub-agents

Gemini CLI blocks it by design, even for an agent holding the `*` tool wildcard. Every
supervisor in this registry that fans work out to workers loses its dispatch mechanism.

The fix is structural, not textual: promote the supervisor's protocol into a **skill**
that the main agent loads, so the main agent performs the dispatch, or drive the phases
from a **custom command**. A supervisor ported as a sub-agent will read correctly, run,
and quietly do the work itself in one context instead of fanning out.

### 2. One repository publishes one extension

Claude Code's marketplace holds many plugins in one repository. The Gemini gallery
crawls repositories tagged `gemini-cli-extension` and requires `gemini-extension.json`
at the repository root, and `gemini extensions install` takes a repository or a local
path with no documented sub-directory selector. A six-plugin monorepo does not become
six installable extensions from one URL.

Three ways out, in order of preference: one repository per extension; a monorepo
installed by local path after a clone; or a build step that publishes each extension
directory to its own repository.

### 3. Skill activation is consented, not silent

Consent is step 3 of **every** activation in `docs/cli/skills.md`, not a first-run grant
the CLI remembers. The prompt names the skill, its purpose and the directory it gains read
access to. A Claude Code agent that pulls in six skills per run becomes six prompts, on
every run. Consolidate on the Gemini side or preload the content through the extension's
`GEMINI.md`, which needs no consent.

### 4. An extension cannot widen permissions

Gemini ignores `allow` decisions and `yolo` configuration in extension-contributed
policy. Deny rules port; allow rules do not, and they fail silently. Carry the intent
into the extension's `GEMINI.md` as a note to the user instead.

## Mapping at a glance

| Concept | Claude Code | Gemini CLI |
|---|---|---|
| Distribution unit | plugin, `.claude-plugin/plugin.json` | extension, `gemini-extension.json` |
| Aggregator | `marketplace.json`, many plugins per repo | gallery crawl of the `gemini-cli-extension` topic, one per repo |
| Path variable | `${CLAUDE_PLUGIN_ROOT}` | `${extensionPath}`, `${workspacePath}`, `${/}` |
| Context file | `CLAUDE.md` | `GEMINI.md`, filename configurable via `context.fileName` |
| Skills | `skills/<name>/SKILL.md` | identical |
| Sub-agents | `agents/**/*.md` | `agents/*.md`, preview |
| Commands | `commands/<name>.md`, markdown | `commands/<name>.toml`, TOML |
| Hooks | `settings.json`, seconds | `hooks/hooks.json`, milliseconds |
| Permissions | `permissions` allow / ask / deny | `excludeTools` plus Policy Engine TOML |
| Evals | `claude plugin eval`, `triggers.json` and `evals.json` | EDK, `evals/*.eval.ts` under vitest |
| Validate the unit | `claude plugin validate <path>` | `gemini extensions validate <path>` |
| Migrate hooks | none | `gemini hooks migrate --from-claude` |

Field-level tables for agent frontmatter, tool names, hook events, models and command
syntax are in [references/field-by-field.md](references/field-by-field.md).

## Direction matters

**Claude Code to Gemini CLI** loses `effort`, `color`, `background` and
`experimental.cacheTtl`, and gains `temperature`, `max_turns`, `timeout_mins` and
per-agent `mcpServers`. The lossy fields are presentation and scheduling hints, so
dropping them changes cost and latency, not behaviour. The gained fields have no source
value, so they must be chosen deliberately rather than defaulted.

**Gemini CLI to Claude Code** is the harder direction. A Gemini agent with
`max_turns: 10` has a hard stop that Claude Code cannot express, and a per-agent
`mcpServers` block has to become a plugin-level `.mcp.json` shared by every agent in the
plugin, which widens the blast radius. State both in the port rather than silently
dropping them.

## Deciding whether to port at all

Ask in this order. A "no" ends it.

1. Is it a skill? Port it. This is the cheap, high-value case.
2. Does it dispatch other agents? Do not port it as an agent. Restructure first.
3. Does it depend on a tool with no Gemini counterpart, `NotebookEdit` or a Claude Code
   MCP surface? Establish the substitute before porting, not after.
4. Does it widen permissions to work? It will fail silently. Redesign it.
5. Does it name Claude Code, Anthropic or a Claude model in a way that reaches the user
   or a produced artefact? Rewrite those strings, do not translate them.
