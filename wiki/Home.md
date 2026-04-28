<!--
audience: mixed
diataxis: explanation
last-verified: 2026-04-28
verified-against: 1e9445a
-->

# Claude Registry

Governance infrastructure for shared Claude Code capabilities across a team.

The registry lets you define, review, version, and distribute specialised
subagents — exactly like a shared code library, but for Claude's behaviour.
Teams write capabilities once and consume them everywhere their projects run
Claude Code.

## TL;DR

- **What it is** — a catalog of versioned, reviewed Claude Code subagents
  (agents and skills) that any project on the team can install with a
  single command.
- **What it gives you** — consistent expert behaviour (Java/Spring,
  Angular, Python, refactoring pipelines, documentation, security review,
  …) without each project re-inventing prompts.
- **How you use it** — run `setup-capabilities.sh` from your project to
  install agents into `.claude/agents/`, or `--global` to install them
  for every Claude Code session.
- **How you contribute** — open a PR adding a `.md` file under
  `claude-catalog/`, pass two CI gates (catalog + marketplace), get one
  reviewer approval, merge.

## Where to go next

| You want to… | Read |
|---|---|
| Install capabilities in your project right now | [Quick start](Quick-start) |
| Understand what this thing actually is | [What is Claude Registry](What-is-Claude-Registry) |
| See the full list of available capabilities | [Capability catalog](Capability-catalog) |
| Add your own capability | [Contributing](Contributing) |
| Understand the architecture | [Architecture](Architecture) |
| Look up a specific concept or field | [Reference](Reference) |
| Read about the review and release process | [Governance](Governance) |
| Find out why something works the way it does | [FAQ](FAQ) |

## Status

Beta capabilities are production-usable today; promotion to `stable` requires
two projects in active use and 30 days without critical issues
([Governance](Governance)). The catalog ships with **59 agents** and a
catalogue of skills covering backend (Java/Spring, Python), frontend (Angular,
React, Vue, Qwik, Vanilla), database (PostgreSQL), and cross-cutting concerns
(testing, REST API design, refactoring, branded documentation).

## Quick links

- Source repository — [github.com/luketherose/claude-registry](https://github.com/luketherose/claude-registry)
- Operational guide (PDF) — `guida-operativa.pdf` in repo root
- Catalog development docs — [`claude-catalog/`](https://github.com/luketherose/claude-registry/tree/main/claude-catalog)
- Distribution manifest — [`claude-marketplace/catalog.json`](https://github.com/luketherose/claude-registry/blob/main/claude-marketplace/catalog.json)
