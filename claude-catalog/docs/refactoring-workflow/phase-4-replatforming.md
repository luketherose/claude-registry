# Phase 4 — Application Replatforming (the rewriting phase, REDESIGNED in v3.0.0)

> Reference doc for `refactoring-supervisor`. Read at runtime when Phase 4 is
> about to start (Bootstrap detect at "current_step": 0..6) or when describing
> Phase 4 in pre-phase brief / activation responses.

## Goal

Produce a fully built, fully runnable, fully tested TO-BE Spring Boot 3
backend + Angular frontend application through a **progressive,
incremental, test-driven, continuously validated** rewriting model.

Replaces the previous big-bang Phase 4 (TO-BE Refactoring with
`scaffold-todo`) AND the previous separate Phase 5 (TO-BE Testing &
Equivalence Verification) — both are absorbed into this single iterative
phase. The application is **always in a working state** throughout this
phase. No big-bang rewrites. No late-stage failures. No non-runnable
intermediate states. Final validation is Step 6 of this phase, not a
separate phase.

## Driver

The Workflow Supervisor (this agent) drives the 7-step loop directly
via fine-grained sub-agents. There is no monolithic Phase 4
sub-supervisor; the per-step / per-feature gating cannot be delegated
as a black box. The legacy `refactoring-tobe-supervisor` and
`tobe-testing-supervisor` files remain on disk for backward
compatibility but are NOT invoked in the canonical Phase 4 path.

## Sub-agents directly orchestrated

- `developer-java` — backend code
- `developer-frontend` — Angular code
- `test-writer` — unit + integration + E2E test authoring
- `debugger` — root-cause on any build/runtime/functional failure
- `code-reviewer` — per-feature review at end of Step 2 inner loop
- `api-designer` — OpenAPI evolution as features are added
- `software-architect` — ADRs when architecturally significant
  decisions arise during the feature loop

## Inputs

| Source | Purpose |
|---|---|
| `<repo>/.indexing-kb/` (Phase 0) | Codebase knowledge base |
| `<repo>/docs/analysis/01-functional/` (Phase 1) | Source of truth for the feature backlog driving Step 2 |
| `<repo>/docs/analysis/02-technical/` (Phase 2) | Stack assumptions and risk register |
| `<repo>/tests/baseline/` and `<repo>/docs/analysis/03-baseline/` (Phase 3) | AS-IS oracle that every feature is validated against in Step 2.7 and Step 6 |

All four are required.

## Output roots

- `<repo>/.refactoring-kb/` — TO-BE knowledge base (feature-by-feature
  progress log, per-step gate evidence, ADR backlog)
- `<repo>/docs/refactoring/` — ADRs, decomposition, OpenAPI, hardening
  notes, replatforming report
- `<repo>/<backend-dir>/` — Spring Boot 3 Maven project (default
  `<repo>/backend/`)
- `<repo>/<frontend-dir>/` — Angular workspace (default
  `<repo>/frontend/`)
- `<repo>/<backend-dir>/src/test/...` — JUnit 5 + Mockito +
  Testcontainers (authored INSIDE Step 2 per-feature loop, not at the end)
- `<repo>/<frontend-dir>/src/app/**/*.spec.ts` — Jest (same)
- `<repo>/e2e/` — Playwright (added incrementally in Step 2 for UCs that
  need cross-page flows; expanded in Step 5 for hardening; consolidated
  in Step 6 for final business-flow validation)
- `<repo>/docs/adr/` — ADR-001 to ADR-N (added as decisions arise, not
  all up-front)

## Entry point file

`docs/refactoring/README.md`

## Manifest file

`docs/refactoring/_meta/manifest.json` — tracks current step (0–6),
feature loop progress (which UC is in flight, which are done, which
are failing), pass-rate trend, hard-gate evidence per step, and the
per-step duration record.

## Step structure (replaces the old W1–W6 wave model)

### Step 0 — Bootstrap (HARD GATE)

Create target project structure (Maven/Gradle for backend, Angular
workspace for frontend), configure build system, ensure project builds
AND application starts. If startup fails: fix configuration
(dependencies, profiles, ports, env vars) and retry.

**Do NOT proceed to Step 1 until both build and startup are green.**

### Step 1 — Minimal Runnable Skeleton

Empty controllers / routes, basic service stubs, minimal frontend
(blank pages OK), security temporarily simplified or disabled (e.g.,
`permitAll`, no auth), no business logic yet. Verify build green + app
starts.

### Step 2 — Incremental Feature Loop

For EACH feature / UC drawn from Phase 1's functional analysis:

1. select ONE feature
2. implement minimal working logic across the BE+FE vertical slice
3. add or adapt tests (unit + integration covering the feature's
   branches; per-feature E2E only when the UC requires it)
4. build the project
5. run tests
6. start the application
7. validate behavior against the Phase 3 baseline oracle

Any failure at any sub-step triggers the Step 3 sub-loop. The next
feature is NOT picked until the current one passes all seven sub-steps.

### Step 3 — Mandatory Validation Loop (sub-loop)

Triggered automatically on any build failure, runtime failure, or
functional issue (HTTP 401, wrong response, missing field, baseline diff).

Steps:

1. identify root cause (delegate to `debugger`)
2. apply a minimal fix at the root cause level (no surrounding cleanup,
   no premature abstraction)
3. re-run build + tests + application startup. Repeat until resolved.

**Do NOT advance forward progress until the system is fully working again.**

### Step 4 — Progressive System Construction

Continue the Step 2 loop across the remaining features. Prefer
**vertical slices** (API → service → integration → frontend) over
horizontal layers (don't build all controllers, then all services, then
all repos — instead, finish UC-1 end-to-end, then UC-2 end-to-end, etc.).
Maintain the invariant: the application is always **buildable, runnable,
and testable**. Promote shared abstractions (utilities, DTOs, mappers)
only after a third feature has needed them — never up-front.

### Step 5 — Hardening

Once core features are implemented, reintroduce and properly configure:

- Spring Security 6 baseline (JWT or session per ADR)
- environment configurations (profiles `local` / `dev` / `prod`,
  env vars, secrets)
- error handling (RFC 7807 ProblemDetail global handler)
- JSON logging with correlation-id (Micrometer + Prometheus)
- CSP and security headers on the frontend

Re-validate: build + startup + full test suite green after each
hardening change. Any regression triggers the Step 3 sub-loop.

### Step 6 — Final Validation (DELIVERABLE)

- full test suite execution (backend + frontend + E2E)
- business-flow validation against the Phase 3 baseline oracle (every
  UC from Phase 1 must pass)
- TODO sweep (no pending TODOs in delivered code; any remaining must be
  ADR-resolved or explicitly accepted by the user)
- produce the **deliverable replatforming report** at
  `docs/refactoring/01-replatforming-report.md` with: feature coverage
  matrix vs Phase 1, baseline equivalence verdict per UC vs Phase 3,
  performance summary, security baseline confirmation, and any accepted
  differences. PO sign-off captured in this report (replaces the old
  Phase 5 `01-equivalence-report.md`).

## Hard gates (non-negotiable per-step)

| Step | Gate | Blocks |
|---|---|---|
| 0 | build green + app starts | Step 1 entry |
| 1 | build green + app starts | Step 2 entry |
| 2 (per feature) | all 7 sub-steps green | the next feature's start |
| 3 | convergence (build + tests + startup all green) | resumes the calling step |
| 5 | build + startup + full test suite green | Step 6 |
| 6 | full test suite + business-flow validation green AND PO sign-off captured | terminates Phase 4 |

The Workflow Supervisor surfaces a per-feature pass/fail confirmation in
the Step 2 recap — the user decides whether to advance.

## What is NOT in this phase (intentional non-goals)

- no big-bang scaffold-then-fill model
- no separate post-Phase-4 testing phase
- no `scaffold-todo` mode (TODOs are forbidden in delivered Step 6 code
  unless ADR-resolved)
- no out-of-tree code generation
- no skipping of the Step 3 sub-loop on transient failures
