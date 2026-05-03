# Pre-phase schematics

> Reference doc for `refactoring-supervisor`. Read at runtime when posting the
> pre-phase brief in Step A of the per-phase protocol — and again when posting
> the next-phase preview at the end of the post-phase recap (Step E).

These schematics MUST be shown to the user verbatim in the pre-phase
confirmation. Pick the schematic for the phase about to start, paste it into
the brief, and proceed with Step A.

## Phase 0 — Indexing

```
indexing-supervisor   (opus)
        |
        +-- PHASE 1 - Structural (parallel) ---------------+
        |   +-- codebase-mapper          -> structure, LOC, packages
        |   +-- dependency-analyzer      -> external + internal deps
        |   +-- streamlit-analyzer       -> Streamlit specifics (if detected)
        |
        +-- PHASE 2 - Modules (parallel fan-out) ----------+
        |   +-- module-documenter (xN)   -> one invocation per package
        |
        +-- PHASE 3 - Cross-cutting (parallel) ------------+
        |   +-- data-flow-analyst        -> DB, APIs, files, env vars
        |   +-- business-logic-analyst   -> domain, rules, state machines
        |
        +-- PHASE 4 - Synthesis (sequential) --------------+
            +-- synthesizer              -> overview, contexts, hotspots, index
```

## Phase 1 — AS-IS Functional Analysis

```
functional-analysis-supervisor   (opus)
        |
        +-- BOOTSTRAP -------------------------------------+
        |   +-- check existing exports under _exports/ -> ask overwrite
        |
        +-- WAVE 1 (parallel) -----------------------------+
        |   +-- actor-feature-mapper     -> actors, features
        |   +-- ui-surface-analyst       -> screens, UI map, components
        |   +-- io-catalog-analyst       -> inputs, outputs, transformations
        |
        +-- WAVE 2 (parallel, after W1) -------------------+
        |   +-- user-flow-analyst        -> use cases, flows, sequences
        |   +-- implicit-logic-analyst   -> hidden rules, state machines
        |
        +-- WAVE 3 (sequential) ---------------------------+
        |   +-- (supervisor)             -> traceability, unresolved Q, README
        |   +-- functional-analysis-challenger (opt-in)  -> adversarial review
        |
        +-- EXPORT WAVE (parallel, always ON) -------------+
            +-- document-creator         -> _exports/01-functional-report.pdf
            +-- presentation-creator     -> _exports/01-functional-deck.pptx
```

## Phase 2 — AS-IS Technical Analysis

```
technical-analysis-supervisor   (opus)
        |
        +-- BOOTSTRAP -------------------------------------+
        |   +-- read .indexing-kb manifest, decide dispatch mode:
        |       parallel | batched | sequential (auto by KB size)
        |   +-- check for existing exports -> ask overwrite if found
        |
        +-- WAVE 1 — 8 workers (mode-dependent dispatch) --+
        |   +-- code-quality-analyst         -> structure, duplication, hotspots
        |   +-- state-runtime-analyst        -> session_state, globals, side effects
        |   +-- dependency-security-analyst  -> deps inventory, CVEs, SBOM-lite
        |   +-- data-access-analyst          -> data flow, DB/file/cache patterns
        |   +-- integration-analyst          -> external APIs, auth, retry
        |   +-- performance-analyst          -> static perf hypotheses
        |   +-- resilience-analyst           -> error handling, logging, fallbacks
        |   +-- security-analyst             -> OWASP Top 10, threat model
        |
        +-- WAVE 2 (sequential, after W1) -----------------+
        |   +-- risk-synthesizer             -> risk register MD/JSON/CSV,
        |                                       severity matrix, remediation backlog
        |
        +-- WAVE 3 (always ON) ----------------------------+
        |   +-- technical-analysis-challenger -> adversarial review:
        |                                        gaps, contradictions,
        |                                        AS-IS violations, Streamlit risks
        |
        +-- EXPORT WAVE (parallel, always ON) -------------+
            +-- document-creator             -> _exports/02-technical-report.pdf
            +-- presentation-creator         -> _exports/02-technical-deck.pptx
```

## Phase 3 — AS-IS Baseline Testing

```
baseline-testing-supervisor   (opus)
        |
        +-- BOOTSTRAP -------------------------------------+
        |   +-- read Phase 1 + Phase 2 manifests
        |   +-- detect env: python+pytest+plugins available?
        |       -> execution policy: on (write+execute) | off (write-only)
        |   +-- detect exposed services (Phase 2 inbound INT-NN)?
        |       -> service-collection-builder ON or OFF
        |   +-- check existing tests/baseline/ + oracle -> ASK overwrite
        |   +-- decide dispatch mode: parallel | batched | sequential
        |
        +-- WAVE 0 (sequential) ---------------------------+
        |   +-- fixture-builder        -> conftest.py, fixtures/
        |
        +-- WAVE 1 (mode-dependent) -----------------------+
        |   +-- usecase-test-writer (xN) -> per-UC fan-out
        |   +-- integration-test-writer  -> DB, FS, outbound APIs (mocked)
        |   +-- benchmark-writer         -> pytest-benchmark, memory
        |   +-- service-collection-builder (conditional) -> Postman 2.1
        |
        +-- WAVE 2 (sequential) ---------------------------+
        |   +-- baseline-runner          -> pytest run | structure-only,
        |                                    snapshot capture, benchmark
        |                                    JSON, coverage JSON, AS-IS
        |                                    bug registry, failure-policy
        |                                    application (xfail/skip/escalate)
        |
        +-- WAVE 3 (always ON) ----------------------------+
            +-- baseline-challenger      -> 7 checks: coverage gaps,
                                            AS-IS source modifications,
                                            determinism risks, oracle
                                            integrity, severity-mismatch,
                                            Streamlit risks, Postman
                                            integrity
```

## Phase 4 — Application Replatforming (the rewriting phase, REDESIGNED)

The Workflow Supervisor drives this phase directly through 7 sequential
steps. Each step has a HARD GATE: forward progress is blocked until the
gate passes. Step 3 is a sub-loop triggered automatically on any
failure during Steps 0, 1, 2, 4, 5, or 6 — it converges before the
calling step resumes.

```
Workflow Supervisor   (opus) — Phase 4: Application Replatforming
        |
        |  ┌──────────────── INVARIANT ────────────────┐
        |  │  The application is ALWAYS in a working   │
        |  │  state. Build green. App starts. Tests    │
        |  │  pass. Any failure triggers Step 3.       │
        |  └────────────────────────────────────────────┘
        |
        +-- BOOTSTRAP -------------------------------------+
        |   +-- verify Phase 0/1/2/3 complete
        |   +-- detect resume state: which step are we on?
        |       (parse docs/refactoring/_meta/manifest.json
        |        `current_step`, `feature_loop_progress`)
        |   +-- detect env: java/maven, node/ng — REQUIRED
        |       (off-policy NOT supported: Phase 4 needs to
        |        actually build and start the app)
        |   +-- choose target backend/frontend dirs
        |       (default backend/, frontend/)
        |
        +-- STEP 0 — BOOTSTRAP (HARD GATE) ----------------+
        |   +-- create target project structure
        |       (Spring Boot Maven scaffold, Angular workspace)
        |   +-- configure build system, dependencies, profiles
        |   +-- minimal application.yml + main class
        |   +-- mvn clean verify   ← MUST pass
        |   +-- mvn spring-boot:run / ng serve  ← MUST start
        |
        |   On failure: identify config/dep/profile issue, fix,
        |   retry. Do NOT advance to Step 1 until both gates green.
        |
        |          HITL CHECKPOINT 0: build + startup verified
        |
        +-- STEP 1 — MINIMAL RUNNABLE SKELETON -------------+
        |   +-- empty controllers / routes (return 200 / empty body)
        |   +-- basic service stubs (no logic)
        |   +-- minimal frontend (blank pages, router shell)
        |   +-- security temporarily simplified
        |       (permitAll, no auth — will be reintroduced in Step 5)
        |   +-- mvn clean verify  ← MUST pass
        |   +-- app starts        ← MUST start
        |
        |          HITL CHECKPOINT 1: skeleton runs
        |
        +-- STEP 2 — INCREMENTAL FEATURE LOOP --------------+
        |   ┌─── for each FEATURE / UC from Phase 1 ─────────┐
        |   │                                                  │
        |   │  2.1  select ONE feature (next from backlog)    │
        |   │  2.2  implement minimal working logic            │
        |   │       (BE controller→service→repo + FE page;    │
        |   │        delegate to developer-java +              │
        |   │        developer-frontend)                       │
        |   │  2.3  add / adapt tests (unit + integration;    │
        |   │       per-UC E2E only when cross-page flow)      │
        |   │       (delegate to test-writer)                  │
        |   │  2.4  mvn clean verify     ← MUST pass            │
        |   │  2.5  mvn test / ng test   ← MUST pass            │
        |   │  2.6  app starts + smoke   ← MUST start           │
        |   │  2.7  validate behavior vs Phase 3 baseline      │
        |   │       (compare output to oracle snapshot)        │
        |   │                                                  │
        |   │  On ANY sub-step failure → STEP 3 sub-loop      │
        |   │  Only after 2.1–2.7 ALL green: advance to next  │
        |   │  feature. Update manifest feature_loop_progress.│
        |   │                                                  │
        |   └──────────────────────────────────────────────────┘
        |
        +-- STEP 3 — MANDATORY VALIDATION LOOP (sub-loop) --+
        |   Triggered on ANY: build failure | runtime failure |
        |   functional issue (HTTP 401, wrong response, baseline diff)
        |
        |   3.1  identify root cause (delegate to debugger)
        |   3.2  apply minimal fix at root cause
        |   3.3  re-run: mvn clean verify + tests + app start
        |   3.4  if still failing → repeat from 3.1
        |
        |   BLOCKING: do NOT advance forward progress until
        |   build + tests + startup are ALL green. The calling
        |   step (0 / 1 / 2 / 4 / 5 / 6) waits.
        |
        +-- STEP 4 — PROGRESSIVE SYSTEM CONSTRUCTION -------+
        |   Continue Step 2 loop across remaining features.
        |   +-- vertical slices preferred (API → service →
        |       integration → frontend) over horizontal layers
        |   +-- INVARIANT: app always buildable / runnable / testable
        |   +-- promote shared utils/DTOs/mappers only after a
        |       third feature needs them (no premature abstraction)
        |   +-- continuous code-reviewer review per feature
        |       (background or after each Step 2.7 success)
        |
        |          HITL CHECKPOINT 2: feature coverage acceptable
        |          (vs Phase 1 UC list — % covered, % deferred)
        |
        +-- STEP 5 — HARDENING -----------------------------+
        |   Reintroduce production concerns one at a time.
        |   After EACH change: build + tests + startup must stay green.
        |
        |   5.1  Spring Security 6 (JWT or session per ADR)
        |   5.2  environment configs (profiles local/dev/prod,
        |        env vars, secrets externalised)
        |   5.3  RFC 7807 ProblemDetail global error handler
        |   5.4  JSON logging + correlation-id (Micrometer +
        |        Prometheus + OpenTelemetry)
        |   5.5  CSP + security headers (frontend)
        |
        |   After each: mvn clean verify + tests + app starts
        |   Any regression → STEP 3 sub-loop
        |
        |          HITL CHECKPOINT 3: hardening done, system green
        |
        +-- STEP 6 — FINAL VALIDATION (DELIVERABLE) --------+
            6.1  full backend test suite (mvn verify with
                 Testcontainers)
            6.2  full frontend test suite (ng test, all spec.ts)
            6.3  E2E suite (Playwright, full business flows)
            6.4  business-flow validation vs Phase 3 baseline
                 oracle (every Phase 1 UC must pass)
            6.5  TODO sweep — no pending TODOs in delivered
                 code; any residual must be ADR-resolved or
                 explicitly accepted by the user
            6.6  produce 01-replatforming-report.md
                 (DELIVERABLE — replaces the old
                  01-equivalence-report.md):
                   - feature coverage matrix vs Phase 1
                   - per-UC verdict vs Phase 3 oracle
                   - performance summary
                   - security baseline confirmation
                   - accepted-differences register
            6.7  PO sign-off captured in the report
                 (BLOCKED while critical/high failures remain)

            On Step 6 failure → STEP 3 sub-loop, then re-run
            Step 6 from the failing sub-step.
```

When a new phase is added, its schematic goes here and the pre-phase
brief template references it.
