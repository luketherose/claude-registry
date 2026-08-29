# Phase 4 — Phase plan (Phase 0 bootstrap + Wave 1–6 + Export wave)

> Reference doc for `refactoring-tobe-supervisor`. Read at runtime to drive the bootstrap dialog, dispatch each wave, and produce the closing report. The supervisor body keeps only the wave dependency chain and HITL checkpoints; the per-wave details and dispatch instructions live here.

## Phase 0 — Bootstrap (supervisor only)

1. **Detect resume mode**. Inspect what is on disk and pick one of:

   | Condition | Resume mode |
   |---|---|
   | No `.refactoring-kb/` AND no `docs/refactoring/` AND backend/frontend dirs absent | `fresh` |
   | Any of the above exist but `docs/refactoring/_meta/manifest.json` reports `partial` / `failed` / `in-progress` / missing | `resume-incomplete` |
   | All TO-BE roots exist AND manifest reports `complete` | `complete-eligible` — ask the user before doing anything |

   When `complete-eligible` triggers, ask the user verbatim:

   ```
   The TO-BE refactoring at .refactoring-kb/ + docs/refactoring/ +
   backend/ + frontend/ is already COMPLETE in this repo.
     Last run:           <ISO-8601 from manifest>
     Bounded contexts:   <count>
     Backend:            <maven build pass | fail | skipped>
     Frontend:           <ng build pass | fail | skipped>
     ADRs:               <count produced>
     OpenAPI version:    <version>
     Roadmap:            <produced | n/a>

   What should I do?
     [skip]    keep the existing TO-BE artifacts as-is, do nothing.
     [re-run]  re-run the full pipeline from W1 (you'll see explicit
               per-artifact overwrite confirmations for `.refactoring-kb/`,
               backend/, and frontend/ — this overwrites generated code).
     [revise]  inspect a specific section together first (e.g.,
               re-run only the OpenAPI design, only the Angular FE,
               only the migration roadmap).
   ```

   Default deny: do not proceed without an explicit answer. Default recommendation: `skip` (re-running overwrites generated code that may have been hand-edited; if the user explicitly wants a refresh, they should choose `re-run` or `revise` knowingly).
   If the user answers `skip`, post a short recap pointing to `docs/refactoring/README.md` and exit cleanly. If `revise`, ask which wave/worker to refresh and dispatch only that. If `re-run`, continue with the remaining bootstrap steps.

   In `resume-incomplete` mode, surface the manifest status and recommend `re-run` (do not auto-resume from broken state); the user may override with `revise`.

   In `fresh` mode, continue with the remaining bootstrap steps.

2. Verify all four prior phases (0, 1, 2, 3) are `complete` per their manifests. If any is missing or `failed`, stop and ask.
3. Read Phase 3 `_meta/as-is-bugs-found.md`. If any `critical` bug is not yet resolved, stop and ask: defer to Phase 5 as documented limitation, or pause Phase 4.
4. Read Phase 1 `bounded-contexts` hint, count BCs (N).
5. Read all manifests to compute total UC count (M) for fan-out estimation.
6. Detect environment per Q3 logic.
7. Read or create `<repo>/.refactoring-kb/_meta/manifest.json` and `<repo>/docs/refactoring/_meta/manifest.json` (resume support).
8. Check existing artifacts (only if resume mode is `re-run` or `resume-incomplete`):
   - `.refactoring-kb/` non-empty → ASK overwrite | augment | abort
   - `backend/` or `frontend/` non-empty → ASK overwrite | rename | abort
   Do NOT silently overwrite generated code. (In `revise` mode this step is per-section, not global.)
9. Recommend iteration model A or B based on BC count and total LOC estimate.
10. Write `00-context.md` with:
    - 1-paragraph system summary
    - BC count (N), UC count (M)
    - Resume mode
    - Iteration model (A | B)
    - Code scope (full | scaffold-todo | structural)
    - Verify policy (on | off)
    - Review mode (background | sync | off)
    - Export setting (on | off)
    - Target backend / frontend dirs
    - **AS-IS bug carry-over list** (any unresolved Phase 3 critical bugs that the user agreed to defer to Phase 5)
11. **Present the plan** to the user with the dispatch overview. Wait for confirmation.

Skip Phase 0 confirmation only on explicit user authorization for the full pipeline — and even then, post the plan and wait at least one turn.

## Wave 1 — Decomposition (sequential, single agent, BLOCKS all)

Dispatch `decomposition-architect`. It produces:
- `bounded-contexts.md` (DDD-style with context map)
- `module-decomposition.md` — explicit AS-IS module → TO-BE BC mapping table (every Phase 0 module appears, every BC has at least one source module)
- `aggregate-design.md` — aggregates per BC, invariants
- `ADR-001-architecture-style.md` (modular monolith vs microservices — Nygard format)
- `ADR-002-target-stack.md` (Spring Boot version, Java version, Angular version, target DB, build tool)

**HITL CHECKPOINT 1**: present ADR-001 and ADR-002 to user with summary. User must confirm before W2.

If user revises ADRs: re-run decomposition-architect with revision notes; do not silently apply user edits.

## Wave 2 — API Contract (sequential, single agent, BLOCKS W3)

Dispatch `api-contract-designer`. It produces:
- `openapi.yaml` (OpenAPI 3.1, validated with spectral if available)
- `design-rationale.md`
- `postman-tobe.json` (TO-BE Postman collection — mirror of Phase 3 AS-IS Postman collection if one exists)
- `ADR-003-auth-flow.md` (OAuth2 / JWT / mTLS — depending on Phase 2 findings on AS-IS auth)

**HITL CHECKPOINT 2**: present OpenAPI summary (endpoint count, auth scheme, error format) to user. Both BE and FE must agree on the contract before W3 dispatches them in parallel.

## Wave 3 — Implementation (parallel: BE track || FE track)

Two parallel tracks dispatched in a single tool call:

### Backend track (sequential within)

1. `backend-scaffolder` — Maven project, package structure (one package per BC from W1), controller skeletons (signatures from OpenAPI), service skeletons, error handler RFC 7807, security config baseline, Spring config files
2. `data-mapper` — JPA entities for each aggregate from W1, Liquibase YAML changelogs from inferred schema, repository interfaces (Spring Data JPA), test fixtures via @TestEntityManager
3. `logic-translator` (fan-out per UC) — for each UC-NN: translate the AS-IS Python module(s) into Java service methods. Per Q2 mode:
   - `full`: complete translation
   - `scaffold-todo` (default): method signature + happy-path skeleton + TODO markers with cross-references
   - `structural`: empty methods with TODOs only

   Each invocation handles ONE UC (like usecase-test-writer pattern). Multiple invocations can run in parallel within the BE track.

Within the BE track, items 1→2→3 are sequential (data layer must exist before logic uses it).

### Frontend track

`frontend-scaffolder` — Angular workspace (single invocation):
- `angular.json`, `package.json`, `tsconfig.json`
- `src/app/core/` — HTTP interceptors (auth, error, correlation-id), guards, error handler, base API service
- `src/app/shared/` — common components (loader, error display, table, form helpers), pipes, models from OpenAPI schema (use openapi-generator ng outputs)
- `src/app/features/` — one lazy-loaded module per BC: routing, list + detail components, feature service consuming the OpenAPI client
- Per Q2 mode: full content vs scaffold-todo (TODO comments referencing UC-NN and AS-IS source) vs structural

The frontend doesn't have a per-UC fan-out because Angular components are typically organized per-screen / per-feature, not per-UC. The single-invocation frontend-scaffolder reads all UCs and produces all modules in one pass.

After both tracks complete:
- Read all outputs from disk; verify file structure
- Run **adaptive verification** per Q3 (mvn compile, ng build)
- Background dispatch `code-reviewer` per Q4 (review-mode background)

**HITL CHECKPOINT 3**: present verification result + code review summary to user. User decides to proceed to W4 or revise.

## Wave 4 — Hardening (sequential, single agent)

Dispatch `hardening-architect`. It produces:
- updates to `backend/src/main/resources/application.yml` (logging format JSON, correlation-id MDC, Micrometer + Prometheus actuator endpoints, OpenTelemetry config)
- `backend/src/main/java/.../shared/config/SecurityConfig.java` (Spring Security 6 baseline: HTTP security headers, CSRF token strategy per ADR-003, CORS for frontend origin)
- `frontend/src/app/core/interceptors/correlation-id.interceptor.ts` (correlation-id propagation)
- `docs/refactoring/4.7-hardening/` (rationale, runbook hints)
- `docs/adr/ADR-004-observability.md`
- `docs/adr/ADR-005-security-baseline.md`

## Wave 5 — Roadmap (sequential, single agent)

Dispatch `migration-roadmap-builder`. It produces:
- `docs/refactoring/roadmap.md` with:
  - milestones (one per BC if Model B; logical groups if Model A)
  - strangler fig plan: which AS-IS module gets retired when, which routing layer (proxy / API gateway / DNS) handles cutover
  - rollback plan per milestone
  - go-live criteria: equivalence percent, performance delta, security sign-off, stakeholder approval
  - acceptance criteria for each BC

## Wave 6 — Challenger (always ON, sequential)

Dispatch `phase4-challenger`. It performs adversarial review and produces the AS-IS↔TO-BE traceability matrix:
- 7+ checks (see challenger spec): coverage, OpenAPI↔code drift, ADR completeness, AS-IS bug carry-over, performance hypothesis, security regression, equivalence claims, AS-IS-only leak in TO-BE
- `as-is-to-be-matrix.json`: every UC-NN → endpoint(s) → service(s) → Angular component(s) — gaps surfaced

**Output**: `docs/refactoring/_meta/challenger-report.md` and `.refactoring-kb/02-traceability/as-is-to-be-matrix.json`.

If challenger reports `≥ 1 blocking` issue: do not declare Phase 4 complete; escalate.

## Export Wave — Opt-in (parallel, two agents)

Only if `--with-exports` was set in bootstrap:
- `document-creator` → `docs/refactoring/_exports/roadmap.pdf` (Accenture-branded)
- `presentation-creator` → `docs/refactoring/_exports/steering-deck.pptx` (Accenture-branded)

Both read the entire `docs/refactoring/` tree as source. Audience for PDF: technical leadership; audience for PPTX: steering committee (milestones, risks, go-live timeline).

If either fails: do not block Phase 4; mark export as failed in manifest, surface in recap.
