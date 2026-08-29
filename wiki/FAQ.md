<!--
audience: mixed
diataxis: reference
last-verified: 2026-08-30
verified-against: 8670a63
-->

# FAQ

Common questions and the failure modes people actually hit. If your answer is not here,
check [Usage](Usage), [Installation](Installation) or
[open an issue](https://github.com/luketherose/claude-registry/issues).

## What is this, in one sentence?

A Claude Code plugin marketplace holding six plugins, 86 subagents and 46 Agent Skills,
so every project on the team gets the same expert behaviour without re-inventing prompts.

## Do I need it if I already have my own subagents?

You need it when more than one project on your team uses Claude Code, you want those
projects to behave consistently, and you want prompt changes to go through review rather
than being edited silently. A single developer on a single project is fine with a local
`.claude/agents/`.

## What is the difference between an agent and a skill?

| | Agent | Skill |
|---|---|---|
| What it is | An autonomous worker with its own context window and tools | Knowledge and procedure loaded into the current context |
| Invoked by | Claude delegating, or you naming it | Claude, with the `Skill` tool; or preloaded via `skills:` |
| Listed in `/agents` | Yes | No |
| Frontmatter | `name`, `description`, plus optional fields | Exactly `name` and `description` |

The authoring decision rule: work that needs its own context window and tools is an
agent; knowledge the current agent should apply itself is a skill.

## Why can I not add the marketplace?

Your Claude Code configuration restricts which marketplaces a session may add, through
`strictKnownMarketplaces`. That is a policy decision made outside this repository. Use
[the local install path](Installation#path-2-local-install-without-the-marketplace),
which delivers the same material.

## Why does an install script exist at all, if plugins install themselves?

For exactly that case. `scripts/install-local.sh` copies agents, skills and reference
material into `~/.claude/` and rewrites `${CLAUDE_PLUGIN_ROOT}` to absolute paths,
because that variable only expands inside a real plugin. You give up background updates,
per-project enabling, and automatic MCP wiring.

## Why should I not just enable every plugin?

Every enabled subagent's `description` is loaded at session start and they all share a
15000-token ceiling. All six plugins together cost roughly 11900 tokens, leaving almost
nothing for plugins from other marketplaces, and routing gets vaguer as Claude has to
discriminate between more similar descriptions. `dev-standards` alone costs about 1700.

## Why are some agents pinned to `opus`?

24 of the 86 are, and they all carry `effort: high`: the supervisors, the challengers,
the auditors, `orchestrator`, `registry-auditor` and the seven deliberation personas.
These do cross-cutting reasoning where a missed failure mode is expensive. 19 user-facing
agents use `inherit`, so they run on whatever you are running and never silently
downgrade an Opus session. The remaining 43 are fan-out pipeline workers on `sonnet`.

## Where did the old two-directory layout go?

The registry used to keep a development area and a separate distribution area, with a
hand-maintained JSON manifest, per-capability tiers, and a bash installer. All of it was
retired on 2026-08-29 in favour of the official plugin marketplace format. See
[Changelog](Changelog) for the full list of what changed.

## Can I run a single phase of the replatforming pipeline?

Yes for Phases 0 to 3. Each has a supervisor that runs standalone:

```
@technical-analysis-supervisor run Phase 2
```

Phase 4 does not run standalone; it requires Phases 0 to 3 complete. Use
`refactoring-supervisor` when you want the phases in sequence with a gate between each.

## Are `docs/analysis/` and `tests/baseline/` inputs or outputs?

Outputs. The pipeline writes them.

| Phase | Reads | Writes |
|---|---|---|
| 0, indexing | The repository source | `.indexing-kb/` |
| 1, functional analysis | `.indexing-kb/` | `docs/analysis/01-functional/` |
| 2, technical analysis | `.indexing-kb/`, optionally Phase 1 | `docs/analysis/02-technical/` |
| 3, baseline testing | Phases 0, 1 and 2 | `tests/baseline/` |
| 4, replatforming | Phases 0 to 3 | `backend/`, `frontend/`, `docs/refactoring/`, `e2e/` |

## Is there a mode that regenerates just the PDF or PPTX?

Yes, for Phases 1 and 2. When the analysis is complete but the branded export is missing,
the supervisor offers `exports-only` and regenerates the export without re-running the
analysis.

## What happened to Phase 5?

It was absorbed into Phase 4 Step 6. `refactoring-supervisor` now drives five phases,
with the final validation and the equivalence check inside Phase 4. The `tobe-testing`
agent cluster and `refactoring-tobe-supervisor` remain in the plugin for backward
compatibility, and their own descriptions still use the older numbering. See
[Capability catalog](Capability-catalog#to-be-testing-and-equivalence-verification).

## Does the pipeline support anything other than Python to Java and Angular?

The pipeline's AS-IS side is language-agnostic for indexing and analysis:
`codebase-mapper`, `dependency-analyzer` and `business-logic-analyst` all state that they
work in any language, with `streamlit-analyzer` as the one stack-specific worker. The
TO-BE side targets Spring Boot 3 and Angular. The migration skills are explicitly Python
to Java, Angular or React.

Outside the pipeline, `dev-standards` covers nine languages and five frontend frameworks.

## CI failed on a capability name I only mentioned in prose. Why?

Because that name is retired. The validator scans `plugins/`, `wiki/`, `docs/`,
`README.md` and `CLAUDE.md` for retired names in backticks and fails the build, so a
removal cannot leave a dangling dispatch instruction behind. The exempt files are the
changelog and the historical design notes, which necessarily name what they record. The
list is in [Reference](Reference#retired-capability-names).

## CI said my frontmatter is not valid YAML, but the agent looked fine. Why does it matter?

Because Claude Code does not error on it. It loads the agent with the name taken from the
filename and drops every other field silently, so the agent runs with no tool list, no
model and no description. An unescaped quote inside a `description` is enough to trigger
it. The gate exists to make that loud.

## CI said my agent invokes skills but is missing the `Skill` tool.

Your body tells the agent to load a skill, but `tools` does not grant `Skill`, so the
instruction is inert. The agent then substitutes its own priors for the team standard and
nothing surfaces the difference. Add `Skill` to the tool list.

## How do I add project-specific knowledge without changing the registry?

Put it in the project's own `CLAUDE.md`, where it applies to every capability at once.
That is preferred over forking a shared agent, because a fork stops receiving updates and
drifts within a release or two. When a project overlay proves useful beyond one project,
promote it here with a pull request.

## What licence is this under?

Every plugin manifest declares `"license": "UNLICENSED"`. There is no `LICENSE` file in
the repository, so treat it as internal to the team.

## Where is the Italian operational guide?

`guida-operativa.pdf` in the repository root, with its LaTeX source alongside it. There is
also `pitch-claude-registry.pptx` for the overview deck.

## Can I preview the wiki locally?

Partly. The pages live in `wiki/` in the main repository, so any Markdown preview shows
the content. Internal links use GitHub wiki page slugs with no `.md` extension, so they
only resolve once published. The sidebar and footer render only on GitHub.

## Where do I file bugs?

[GitHub issues](https://github.com/luketherose/claude-registry/issues). Include the
capability name, the plugin version from its `plugin.json`, and a minimal reproduction.

## Related

- [Quick start](Quick-start)
- [Installation](Installation)
- [Usage](Usage)
- [Capability catalog](Capability-catalog)
