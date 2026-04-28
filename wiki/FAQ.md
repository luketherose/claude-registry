<!--
audience: mixed
diataxis: reference
last-verified: 2026-04-28
verified-against: 1e9445a
-->

# FAQ

Common questions and gotchas. If you don't find your answer here, check
[Usage](Usage), [Installation](Installation), or open an issue on the
[repository](https://github.com/luketherose/claude-registry/issues).

## What is this, in one sentence?

A versioned catalog of Claude Code subagents (`.md` files with YAML
frontmatter) that any project on the team can install with one command,
giving Claude consistent expert behaviour across projects.

## Do I need this if I already have my own custom subagents?

You need it when:
- More than one project on your team uses Claude Code.
- You want those projects to share the same expert behaviour (Java/Spring
  conventions, code-review style, refactoring pipelines).
- You want a review process (PR + CI) for prompt changes rather than
  silent edits.

You don't need it if you're a single developer on a single project — a
local `.claude/agents/` is enough.

## What's the difference between an agent and a skill?

| | Agent | Skill |
|---|---|---|
| Purpose | Performs a role | Provides knowledge |
| Model | `sonnet` (default), `opus` for orchestrators | `haiku` |
| Tools | Role-appropriate | `Read` only |
| Invoked by | Claude (auto-delegation) or user | Other agents |
| Visible in `/agents` | Yes | No |

See [What is Claude Registry](What-is-Claude-Registry#two-kinds-of-capability)
for the full table.

## Why two repository areas (`claude-catalog/` and `claude-marketplace/`)?

Separation of concerns. The catalog is where work happens — branches,
PRs, in-progress drafts, scaffolding. The marketplace is what
consumers install — only files that have passed review and been
explicitly published. The two CI gates enforce the boundary.

If a capability is only in the catalog, it cannot be installed. That's
deliberate — work-in-progress shouldn't accidentally ship.

## Why are some agents `model: opus`?

Eight capabilities use `opus`:
- `orchestrator`
- `refactoring-supervisor`
- the six phase-specific supervisors
  (`indexing-supervisor`, `functional-analysis-supervisor`,
  `technical-analysis-supervisor`, `baseline-testing-supervisor`,
  `refactoring-tobe-supervisor`, `tobe-testing-supervisor`)

These are orchestrators — they decompose tasks, choose dispatch modes,
reason about cross-phase consistency, and drive HITL checkpoints. The
reasoning depth justifies the cost. Wave-1 workers stay on `sonnet`.

The validation script flags every `opus` agent for justification in
the PR description so this stays a deliberate choice, not the default.

## Can I run a single phase of the refactoring pipeline?

Yes. Each phase supervisor (`indexing-supervisor`,
`functional-analysis-supervisor`, etc.) is a single entrypoint and runs
independently. Use `refactoring-supervisor` only when you want all
phases sequentially with HITL between them.

## I see a directory `tests/baseline/` and `docs/analysis/` — are these
input or output?

Output. The refactoring pipelines write here. Their inputs are:

| Phase | Reads | Writes |
|---|---|---|
| 0 — Indexing | repo source code | `.indexing-kb/` |
| 1 — Functional analysis | `.indexing-kb/` | `docs/analysis/01-functional/` |
| 2 — Technical analysis | `.indexing-kb/` + Phase 1 (optional) | `docs/analysis/02-technical/` |
| 3 — Baseline testing | Phases 0/1/2 | `tests/baseline/` + `docs/analysis/03-baseline/` |
| 4 — TO-BE refactoring | Phases 0–3 | `backend/`, `frontend/`, ADRs |
| 5 — TO-BE testing | Phases 0/1/2/3 + TO-BE codebase | `01-equivalence-report.md` |

## Is there an `exports-only` mode if I just need the PDF/PPTX?

Yes, for Phases 1 and 2. If the analysis is complete but the
Accenture-branded PDF or PPTX export is missing, the supervisor offers
to regenerate just the missing exports without re-running the analysis
pipeline. Default recommendation when triggered.

## Does the registry support languages other than Python (input) and
Java/Spring + Angular (output)?

The refactoring pipelines today are AS-IS Python (with optional
Streamlit) and TO-BE Spring Boot 3 + Angular 17+. The top-level role
agents (`developer-java-spring`, `developer-python`,
`developer-frontend` covering Angular/React/Vue/Qwik/Vanilla) work
across general projects. Additional `developer-*` agents for more
languages are tracked under "Roadmap" — see open issues on the repo.

## I added a capability to `claude-catalog/` and CI says "no entry in
catalog.json". Why?

The first CI gate enforces that every catalog file is published. Add
the entry to `claude-marketplace/catalog.json` and copy the file to
`claude-marketplace/{tier}/`. See [Contributing](Contributing) for the
mechanical workflow.

## I edited a `.md` file in `claude-marketplace/` directly. CI says
"frontmatter name doesn't match". Why?

Don't edit the marketplace directly. The flow is: edit
`claude-catalog/`, then publish to `claude-marketplace/`. The publish
script (or a manual `cp`) keeps them in sync. The CI gate exists to
catch direct marketplace edits, which would silently drift from the
catalog source.

## What are these "Mermaid garbage files in my repo root"?

You're seeing the symptom of a bug fixed on 2026-04-28: a Phase 2
sub-agent (`state-runtime-analyst`) used `Bash` heredocs to write
Mermaid diagrams, and Mermaid syntax (`A[label]`, `B{cond?}`,
`A --> B`) contains shell metacharacters that the shell misinterpreted
under Git Bash on Windows. Result: 48 accidental zero-byte files plus
one file containing the output of an unrelated `store` command.

Fix: every agent that writes content now has a non-negotiable
**File-writing rule** mandating `Write`/`Edit` and forbidding shell-based
content generation. The fix was applied to all phase pipelines.
See [Changelog](Changelog) for the entry.

If you have these files in your project, delete them — they are zero
bytes (or, for the one named `return`, a Microsoft Store CLI banner)
and harmless.

## How do I add a project-specific overlay without modifying the
catalog?

Create a file in your project's `.claude/agents/` with a **distinct
name** (so it doesn't shadow a catalog file):

```markdown
---
name: developer-java-spring-payments
description: Use when working on the payments service. Follows
  developer-java-spring conventions, additionally requires every
  payment write to flow through the IdempotencyKey filter.
tools: Read, Edit, Write, Bash, Grep, Glob
model: sonnet
---

[system prompt with project-specific additions]
```

Reference (don't duplicate) the catalog capability's behaviour. When
the overlay proves widely useful, promote it to the catalog with a PR.

## How do I update?

```bash
cd claude-registry
git pull origin main
./claude-catalog/scripts/setup-capabilities.sh /path/to/your-project all
```

Restart Claude Code to pick up the new versions.

## Where's the Italian operational guide?

`guida-operativa.pdf` in the repository root. It mirrors the wiki
content as a single PDF for offline reading.

## Can I run the wiki content locally?

Sort of. GitHub wikis are rendered server-side, so the closest local
preview is to check out the `<repo>.wiki.git` clone and view the `.md`
files in your editor's Markdown preview. Internal links use page slugs
(no `.md` extension) which won't resolve outside GitHub.

## Where do I file bugs?

[GitHub issues](https://github.com/luketherose/claude-registry/issues).
Include the capability name, version, and (if possible) a minimal
reproduction.

## Related

- [Quick start](Quick-start)
- [Usage](Usage)
- [Capability catalog](Capability-catalog)
- [Changelog](Changelog)
