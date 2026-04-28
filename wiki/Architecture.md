<!--
audience: contributor
diataxis: explanation
last-verified: 2026-04-28
verified-against: 1e9445a
-->

# Architecture

This page explains how the registry is organised and how its main flows
work. It targets readers who already know what the registry is (see
[What is Claude Registry](What-is-Claude-Registry)) and want the
mental model needed to contribute or to understand the multi-phase
refactoring pipelines.

## Repository layout

```
claude-registry/
├── claude-catalog/                 ← development source
│   ├── agents/                       subagent .md files
│   │   ├── indexing/                   Phase 0 (8 agents)
│   │   ├── functional-analysis/        Phase 1 (7 agents)
│   │   ├── technical-analysis/         Phase 2 (11 agents)
│   │   ├── baseline-testing/           Phase 3 (8 agents)
│   │   ├── refactoring-tobe/           Phase 4 (10 agents)
│   │   ├── tobe-testing/               Phase 5 (9 agents)
│   │   └── (top-level role agents)
│   ├── skills/                       knowledge providers (read-only)
│   │   ├── orchestrators/
│   │   ├── frontend/
│   │   ├── backend/
│   │   ├── database/
│   │   ├── testing/
│   │   ├── api/
│   │   ├── refactoring/
│   │   ├── documentation/
│   │   ├── analysis/
│   │   ├── python/
│   │   └── utils/
│   ├── examples/
│   ├── evals/
│   ├── hooks/
│   ├── settings/
│   ├── mcp/
│   ├── policies/
│   ├── templates/
│   ├── docs/
│   ├── scripts/
│   │   ├── setup-capabilities.sh    install into a project / global
│   │   └── new-capability.sh        scaffold a new capability + branch
│   ├── how-to-write-a-capability.md
│   ├── CONTRIBUTING.md
│   ├── GOVERNANCE.md
│   └── CHANGELOG.md
│
├── claude-marketplace/             ← distribution (approved files only)
│   ├── stable/                       production-ready capabilities
│   ├── beta/                         new or experimental capabilities
│   ├── skills/                       shared skills (auto-installed)
│   ├── catalog.json                  authoritative manifest
│   └── scripts/
│       └── publish.sh               copies a catalog file to a tier
│
├── README.md
├── guida-operativa.pdf             ← Accenture-branded operational guide
└── pitch-claude-registry.pptx      ← Accenture-branded pitch deck
```

The `claude-catalog/` and `claude-marketplace/` separation is the
single most important architectural decision. Read
[What is Claude Registry § Two repository areas](What-is-Claude-Registry#two-repository-areas)
for why.

## Flow: contributing a capability

```
author opens a PR adding claude-catalog/agents/foo.md
                   │
                   ▼
   CI Gate 1 — validate-catalog
        │   - YAML frontmatter valid
        │   - skills don't have forbidden tools
        │   - CHANGELOG has [Unreleased] entry
        │   - every catalog file has a marketplace entry  ◄── BLOCKS
        │
        ▼
   CI Gate 2 — validate-marketplace
        │   - catalog.json valid (semver, tier, status)
        │   - referenced files exist on disk
        │   - frontmatter name matches catalog entry name
        │   - path conventions enforced
        │
        ▼
   reviewer applies review-checklist.md
                   │
                   ▼
              merge to main
                   │
                   ▼
         tag: foo@MAJOR.MINOR.PATCH
                   │
                   ▼
            available to consumers
```

The two gates run sequentially: gate 2 only starts if gate 1 is green.
That ordering is deliberate — gate 1 catches the common author mistake
of editing the catalog without publishing the marketplace mirror, before
gate 2 even has a chance to look.

## Flow: installing a capability into a project

```
consumer runs ./claude-catalog/scripts/setup-capabilities.sh
                   │
                   ▼
   reads claude-marketplace/catalog.json
                   │
                   ▼
   prompts: all / stable / beta / select-by-name
                   │
                   ▼
   resolves dependencies (each agent's skills are auto-installed)
                   │
                   ▼
   copies <capability>.md → <project>/.claude/agents/
                   │
                   ▼
   Claude Code session sees the new agents at next restart
```

The script never touches `claude-catalog/`. It reads from
`claude-marketplace/` only.

## The six-phase refactoring pipeline

The registry's flagship use case is end-to-end legacy modernisation. The
top-level entrypoint is `refactoring-supervisor` (model `opus`); it
delegates each phase to a phase-specific supervisor. Each phase has its
own pipeline of sub-agents.

```
   ┌───────────────────────────────────────────────────────────────────────┐
   │                        refactoring-supervisor (opus)                    │
   │                  top-level workflow, HITL between phases                │
   └───────┬───────────┬───────────┬───────────┬───────────┬───────────────┘
           │           │           │           │           │
        Phase 0     Phase 1     Phase 2     Phase 3     Phase 4     Phase 5
           │           │           │           │           │           │
           ▼           ▼           ▼           ▼           ▼           ▼
     indexing-     functional- technical-  baseline-   refactoring- tobe-
     supervisor    analysis-    analysis-   testing-    tobe-        testing-
                   supervisor   supervisor  supervisor  supervisor   supervisor
           │           │           │           │           │           │
           ▼           ▼           ▼           ▼           ▼           ▼
     .indexing-kb  docs/        docs/       tests/      backend/     01-
                  analysis/    analysis/   baseline/   frontend/    equivalence
                  01-          02-                     ADRs         -report.md
                  functional/  technical/                            (PO sign-off)
```

### Phase 0 — Indexing

`indexing-supervisor` reads a legacy Python (and optional Streamlit)
codebase and produces a Markdown knowledge base at `.indexing-kb/`:
structural inventory, dependency graph, module documentation,
data-flow analysis, business-logic extraction, and (for Streamlit)
session-state and widget analysis. Eight sub-agents in four sub-phases.

Outputs feed every subsequent phase.

### Phase 1 — Functional analysis

`functional-analysis-supervisor` reads `.indexing-kb/` and produces a
functional understanding at `docs/analysis/01-functional/`: actors and
roles, UI surface, I/O catalogue, use cases with Mermaid sequence
diagrams, implicit logic. Optionally an adversarial challenger flags
gaps and contradictions. Then exports an Accenture-branded PDF and PPTX
in `_exports/`.

The supervisor supports an `exports-only` resume mode that regenerates
just the missing PDF/PPTX without re-running the analysis.

### Phase 2 — Technical analysis

`technical-analysis-supervisor` reads `.indexing-kb/` and (optionally)
Phase 1, then dispatches eight Wave-1 workers in **parallel, batched, or
sequential** mode (decided adaptively from KB size): code quality,
state-runtime, dependency-security, data-access, integration,
performance, resilience, security. Wave 2 is a synthesizer producing a
unified risk register; Wave 3 is an always-on adversarial challenger.
Same `exports-only` resume mode as Phase 1.

### Phase 3 — Baseline testing

`baseline-testing-supervisor` reads Phases 0/1/2 and authors the AS-IS
regression baseline at `tests/baseline/`: pytest suites, fixtures with
deterministic seed/time/network setup, snapshots, benchmarks, and an
optional Postman collection. Wave 0 (fixtures) → Wave 1 (authoring,
fan-out per use case) → Wave 2 (execution and oracle capture) → Wave 3
(challenger). The baseline is the **AS-IS oracle** consumed by Phase 5
equivalence verification.

### Phase 4 — TO-BE refactoring

`refactoring-tobe-supervisor` is the **first phase with target tech**
(Spring Boot 3 + Angular). Reads Phases 0-3 and produces:

- bounded-context decomposition + foundational ADRs (architecture style,
  target stack, auth flow)
- OpenAPI 3.1 contract (single source of truth)
- Spring Boot 3 backend scaffold (controllers from OpenAPI operationIds,
  DTOs, services with TODO markers, JPA entities, Flyway migrations)
- Angular 17+ frontend scaffold (standalone components, lazy modules per
  bounded context, OpenAPI typed client)
- per-UC translation of Python business logic to Java service methods
- production hardening (observability + security baseline)
- migration roadmap (strangler fig with per-BC milestones)
- challenger producing the AS-IS↔TO-BE traceability matrix

Three HITL checkpoints (post-decomposition, post-API-contract,
post-implementation) gate the workflow.

### Phase 5 — TO-BE testing and equivalence verification

`tobe-testing-supervisor` is the **final go-live gate**. Validates the
TO-BE codebase against the Phase 3 baseline. Backend tests
(JUnit 5 + Mockito + Testcontainers + Spring Cloud Contract), frontend
tests (Jest + Angular Testing Library + Playwright E2E), an equivalence
harness comparing TO-BE outputs against Phase 3 snapshots, security
tests (OWASP Top 10 + Phase 2 SEC-NN regression), and performance
comparison vs Phase 3 benchmarks (p95 ≤ +10% gate). Output is
`01-equivalence-report.md` — the deliverable signed by the Product Owner
before go-live.

## Why opus models for supervisors

Five capabilities use `model: opus` rather than the default `sonnet`:

- `refactoring-supervisor`
- `indexing-supervisor`
- `functional-analysis-supervisor`
- `technical-analysis-supervisor`
- `baseline-testing-supervisor`
- `refactoring-tobe-supervisor`
- `tobe-testing-supervisor`
- `orchestrator`

These are **orchestrators** — they decompose tasks, decide dispatch
modes (parallel / batched / sequential), reason about cross-phase
consistency, and drive HITL checkpoints. The reasoning depth justifies
the cost. Wave-1 workers stay on `sonnet`.

## Conventions

- **Capability filenames**: `kebab-case`, no version in name. Use git
  tags (`name@MAJOR.MINOR.PATCH`) for versioning.
- **Catalog directory layout**: agents and skills MAY be grouped into
  thematic subdirectories (e.g. `agents/indexing/`,
  `skills/orchestrators/`). Validation scans recursively.
- **Marketplace directory layout**: stays **flat** regardless of catalog
  grouping. Files live at `stable/<name>.md`, `beta/<name>.md`, or
  `skills/<name>.md`. The `file` field in `catalog.json` reflects this
  flat path.
- **Skills**: `model: haiku`, `tools: Read` only — they are knowledge
  providers, not autonomous actors.
- **Agents**: `model: sonnet` by default; `opus` only with documented
  justification.

## Related

- [Capability catalog](Capability-catalog) — the full list with what
  each agent does
- [Governance](Governance) — lifecycle, decision rules, SLAs
- [Reference](Reference) — manifest fields, frontmatter contract
