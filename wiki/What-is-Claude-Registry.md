<!--
audience: mixed
diataxis: explanation
last-verified: 2026-08-30
verified-against: c6c780a
-->

# What is Claude Registry

This page explains what the registry is, what problem it solves, and how its pieces fit
together. For install steps see [Quick start](Quick-start). For the file layout and the
runtime flows see [Architecture](Architecture).

## TL;DR

Claude Registry is a **Claude Code plugin marketplace** kept in one Git repository. The
root manifest `.claude-plugin/marketplace.json` declares six plugins. Each plugin is a
self-contained directory under `plugins/` holding subagents, Agent Skills, bundled
reference material, evaluations and worked examples.

A consumer adds the marketplace once and enables the plugins the project needs. From then
on Claude delegates to the right specialist without further prompting, and plugin updates
arrive in the background when the resolved version changes.

## The problem it solves

Without a shared marketplace every project re-invents its prompts. The Java team on
project A writes one Spring Boot prompt, project B writes another, the two drift, and the
better one is never reused. Worse, prompts usually live inside individual chat threads,
so nobody reviews them, versions them, or audits what changed.

The registry treats prompts as code:

- A capability is a Markdown file committed to Git.
- A pull request introduces or modifies it.
- CI validates manifests, frontmatter, body length, reference links and the delegation
  budget (see [Governance](Governance)).
- A reviewer approves.
- Merging to `main` publishes. Semver on the plugin records the change.

## The two capability types this registry ships

| Type | What it is | Who invokes it | Lives in |
|---|---|---|---|
| **Agent** (subagent) | An autonomous worker with its own context window, tool set and system prompt | Claude delegates to it, or the user mentions it by name | `plugins/<plugin>/agents/**/*.md` |
| **Skill** | Knowledge and procedure loaded into the current context on demand | Claude loads it with the `Skill` tool, or an agent preloads it via the `skills:` frontmatter field | `plugins/<plugin>/skills/<name>/SKILL.md` |

The plugin format also supports slash commands at `plugins/<plugin>/commands/*.md`. This
registry ships none today.

**The decision rule** for authors: work that needs its own context window and its own
tools is an agent. Knowledge or a procedure the current agent should apply itself is a
skill. See
[`docs/registry/how-to-write-a-capability.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/how-to-write-a-capability.md).

## Skills follow the Anthropic Agent Skills standard

A skill is a directory containing `SKILL.md`. Its frontmatter has exactly two fields,
`name` and `description`. `model`, `tools` and `color` are rejected by CI, because they
are not SKILL.md fields.

Content loads progressively:

| Level | Content | Loaded |
|---|---|---|
| 1 | `name` and `description` | Always, at startup, for every installed skill |
| 2 | The `SKILL.md` body (capped at 500 lines) | When Claude decides the skill is relevant |
| 3 | `references/*.md` | Only when the body links to that specific file |

That is why a `SKILL.md` body stays short. Detail moves into `references/`, one level
deep from the body, rather than being compressed into denser prose.

## The distribution unit is the plugin

There is one tier. There is no separate development area and distribution area, and no
per-capability beta or stable flag. A capability is available as soon as its plugin is
installed and enabled.

```
.claude-plugin/marketplace.json      declares the six plugins
plugins/dev-standards/
  .claude-plugin/plugin.json         name, description, version, author, MCP wiring
  agents/                            12 subagents
  skills/<name>/SKILL.md             29 Agent Skills
  references/                        shared reference material for this plugin's agents
  evals/ examples/                   evaluations and worked examples
  .mcp.json                          optional MCP servers, wired from plugin.json
```

**Rule: a capability and the skills it always needs belong to the same plugin.** A skill
in another plugin is only available when the consumer has that plugin enabled too. Where
a cross-plugin reference is unavoidable, the agent body says so and describes what to do
without it.

## Two install paths

| Path | Command | Use when |
|---|---|---|
| Plugin marketplace | `/plugin marketplace add luketherose/claude-registry` | Your Claude Code configuration allows adding this marketplace |
| Local copy | `./scripts/install-local.sh` | Enterprise policy (`strictKnownMarketplaces`) blocks the marketplace source |

Both paths deliver the same material. The differences are in how updates arrive and how
bundled reference paths are resolved. [Installation](Installation) covers both in full.

## What it is not

- **Not an automated evaluation harness.** `plugins/<plugin>/evals/<name>/` holds
  `evals.json` scenarios and `triggers.json` routing cases. They are run by hand.
- **Not a prompt playground.** Everything merged here is expected to be production grade
  and reviewed.
- **Not a replacement for project-specific subagents.** Project knowledge such as data
  models, internal libraries and local naming conventions belongs in the project's own
  `.claude/agents/`.
- **Not a proprietary format.** Plugins, subagents and Agent Skills are the official
  Claude Code formats. The registry adds governance on top.

## Who it is for

- **Engineering teams** running Claude Code on more than one project who want the same
  expert behaviour everywhere.
- **Tech leads** who want their architectural standards encoded once and applied
  consistently.
- **Architects** running modernisation programmes who need the five-phase replatforming
  pipeline described in [Architecture](Architecture).

## Related

- [Quick start](Quick-start): install a plugin and confirm it loaded
- [Capability catalog](Capability-catalog): every agent and skill that ships today
- [Architecture](Architecture): repository layout, CI flow, the replatforming pipeline
- [Governance](Governance): review, versioning and release rules
