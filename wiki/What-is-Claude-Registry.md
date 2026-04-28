<!--
audience: mixed
diataxis: explanation
last-verified: 2026-04-28
verified-against: 1e9445a
-->

# What is Claude Registry

This page explains what the Claude Registry is, what problem it solves, and
how its pieces fit together. For installation steps see
[Quick start](Quick-start); for the full file layout see
[Architecture](Architecture).

## TL;DR

The registry is a **versioned catalog of Claude Code subagents** — small
Markdown files with a YAML front-matter that tell Claude how to behave for a
specific role (architect, reviewer, developer, refactoring supervisor, …).
Teams maintain it like a shared library: each capability is reviewed via PR,
versioned, and distributed through a manifest (`catalog.json`).

A user installs the capabilities they want into their own project (or
globally for every Claude Code session) and from then on Claude knows when
to delegate to which specialist without further prompting.

## The problem it solves

Without a shared catalog every project re-invents its prompts: the Java team
on project A writes one Spring Boot prompt, project B writes another,
they drift apart, and the prompt with the best ideas is never reused.
Worse, prompts are usually buried inside individual chat threads, so
nobody can review them, version them, or audit what changed.

The registry treats prompts as code:

- A capability lives in a `.md` file checked into git.
- A PR introduces or modifies it.
- CI validates the file's structure (frontmatter, system prompt, tools).
- A reviewer approves.
- A `name@MAJOR.MINOR.PATCH` tag pins a release.
- A separate "marketplace" tier (`stable` / `beta`) controls what gets
  distributed.
- A setup script installs and resolves dependencies (skills) for a project
  or globally.

## Two kinds of capability

| Type | Purpose | Model | Tools | Where it runs |
|---|---|---|---|---|
| **Agent** | Performs a role: analyses, writes code, designs, reviews. Has behaviour and tool access. | `sonnet` (default), `opus` for orchestrators | Role-appropriate set | `.claude/agents/` in the consuming project |
| **Skill** | Provides knowledge: standards, conventions, brand rules. Read-only knowledge retrieval. | `haiku` | `Read` only | Same `.claude/agents/` directory; invoked by agents |

Skills are not visible to end users directly — they are loaded by agents
that depend on them. When you install an agent, the setup script
auto-installs every skill it depends on.

## Two repository areas

The repository has **two areas with distinct responsibilities**:

| Area | Purpose | Who edits |
|---|---|---|
| `claude-catalog/` | Development source — capabilities are written, reviewed, and versioned here | Authors, in PRs |
| `claude-marketplace/` | Distribution — contains only approved capabilities, copied from the catalog | The publish script, never by hand |

The fundamental rule: **a capability is not "available" until it has been
published from `claude-catalog/` to `claude-marketplace/`.** Modifying only
the catalog does not affect consumers.

```
claude-catalog/agents/foo.md         publish        claude-marketplace/beta/foo.md
                                  ─────────►       claude-marketplace/catalog.json (manifest)
```

## Two CI gates

Every PR goes through two gates in sequence — the second only starts if
the first is green:

1. **`validate-catalog`** — checks files in `claude-catalog/`:
   - valid YAML frontmatter (`name`, `description`, `tools`, `model`)
   - system prompt present with `## Role`
   - skills do not include forbidden tools (`Edit`, `Write`, `Bash`, `Agent`)
   - `CHANGELOG.md` has an `[Unreleased]` entry
   - every catalog agent / skill has a corresponding entry in
     `claude-marketplace/catalog.json` (this is what blocks PRs that add a
     capability without publishing it)

2. **`validate-marketplace`** — checks distribution:
   - `catalog.json` is valid (semver, tier, status, required fields)
   - every referenced file exists on disk
   - file frontmatter `name` matches the catalog entry name
   - path conventions enforced (`{tier}/{name}.md` or `skills/{name}.md`)
   - no orphan files in `stable/`, `beta/`, `skills/`

If a PR adds capabilities to the catalog without publishing them to the
marketplace, the first gate blocks it before the second even starts. See
[Governance](Governance) for the full lifecycle.

## What it is not

- **Not an LLM evaluation framework.** The `evals/` directory contains
  scenario fixtures for human review of capability behaviour, not an
  automated benchmark suite.
- **Not a prompt-engineering playground.** Every prompt that lands here is
  expected to be production-grade and reviewed.
- **Not a replacement for project-specific subagents.** Project-specific
  knowledge (data models, internal libraries, naming conventions) belongs in
  the project's own `.claude/agents/`, optionally as a thin overlay on a
  catalog capability.
- **Not a vendor lock-in.** The `.md` + frontmatter format is the official
  Claude Code standard; the registry just adds governance around it.

## Who it is for

- **Engineering teams** that have multiple projects using Claude Code and
  want consistent expert behaviour across them.
- **Tech leads** who want to encode their architectural standards (Spring
  Boot conventions, Angular smart/dumb pattern, REST API design) once and
  see them applied everywhere.
- **Architects** running large modernization or migration programmes who
  need a coherent multi-phase pipeline (indexing, functional analysis,
  technical analysis, baseline testing, refactoring, equivalence
  verification — see [Architecture](Architecture)).

## Related

- [Quick start](Quick-start) — install the capabilities and try one
- [Capability catalog](Capability-catalog) — the full list of agents and
  skills currently shipped
- [Architecture](Architecture) — how the catalog/marketplace separation
  and the multi-phase refactoring pipelines fit together
- [Governance](Governance) — versioning, lifecycle, decision rules
