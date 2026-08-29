# Phase 5 — Phase plan (Phase 0 bootstrap + Wave 1–5 + final report)

> Reference doc for `tobe-testing-supervisor`. Read at runtime to drive the bootstrap dialog, dispatch each wave, and produce the closing report.

## Phase 0 — Bootstrap (supervisor only, no sub-agents)

1. **Detect resume mode**. Inspect what is on disk and pick one of:

   | Condition | Resume mode |
   |---|---|
   | No `docs/analysis/05-tobe-tests/` AND no `tests/equivalence/` AND no test files under `backend/src/test/` or `frontend/src/app/**/*.spec.ts` | `fresh` |
   | Either dir exists but `docs/analysis/05-tobe-tests/_meta/manifest.json` reports `partial` / `failed` / missing | `resume-incomplete` |
   | Reports exist AND manifest reports `complete` | `complete-eligible` — ask the user before doing anything |

   When `complete-eligible` triggers, ask the user verbatim:

   ```
   The TO-BE testing at docs/analysis/05-tobe-tests/ is already
   COMPLETE in this repo.
     Last run:           <ISO-8601 from manifest>
     UCs tested:         <count> / <total>
     Backend coverage:   <line %>, <branch %>
     Contract tests:     <pass> / <total>
     Perf p95 delta:     <% vs baseline>
     Equivalence:        <signed | pending PO>

   What should I do?
     [skip]    keep the existing test suite + report as-is, do nothing.
     [re-run]  re-run the full pipeline from W1 (you'll see explicit
               per-suite overwrite confirmations — this overwrites
               authored tests).
     [revise]  inspect a specific section together first (e.g.,
               re-run only equivalence tests for a UC that changed,
               only the security suite, only the perf comparison).
   ```

   Default deny: do not proceed without an explicit answer. Default recommendation: `skip`. If the user answers `skip`, post a short recap pointing to `01-equivalence-report.md` and exit cleanly. If `revise`, ask which wave/worker to refresh and dispatch only that. If `re-run`, continue with the remaining bootstrap steps.

   In `resume-incomplete` mode, surface the manifest status and recommend `re-run`; the user may override with `revise`.

   In `fresh` mode, continue with the remaining bootstrap steps.

2. Verify all four prior phases (0, 1, 2, 3) AND Phase 4 are `complete` per their manifests. If any is missing or `failed`, stop and ask.
3. Read Phase 1 UC list (`docs/analysis/01-functional/06-use-cases/`) to compute N (UC count).
4. Read Phase 4 decomposition (`docs/refactoring/4.1-decomposition/` or `.refactoring-kb/00-decomposition/`) to compute B (BC count).
5. Read Phase 4 OpenAPI contract; verify it is spectral-valid (run spectral if available; otherwise just verify the file exists and parses as YAML).
6. Read Phase 3 benchmark JSON (`tests/baseline/_meta/benchmark-baseline.json` or wherever Phase 3 wrote it) to capture the AS-IS performance reference.
7. Read Phase 4 `_meta/as-is-bugs-deferred.md`. These are AS-IS bugs the team agreed to inherit in TO-BE; they must NOT count as TO-BE regressions in equivalence checks. Pass this list to all W1 workers.
8. **Detect environment** per the adaptive execution logic. Determine `execute_policy`.
9. Read or create `docs/analysis/05-tobe-tests/_meta/manifest.json` (resume support).
10. Check existing artifacts (only if resume mode is `re-run` or `resume-incomplete`):
    - `backend/src/test/java/` non-empty under TO-BE BC paths → ASK overwrite | augment | abort
    - `frontend/src/app/**/*.spec.ts` already authored → ASK overwrite | augment | abort
    - `e2e/` non-empty → ASK overwrite | keep | abort
    - `tests/equivalence/` non-empty → ASK overwrite | keep | abort
    Do NOT silently overwrite test code that may have been hand-edited or extended. (In `revise` mode this step is per-section.)
11. Determine **dispatch mode** per the rules above.
12. Write `00-context.md` with:
    - 1-paragraph system summary
    - UC count (N), BC count (B)
    - Resume mode
    - Execute policy + detection results
    - Dispatch mode + rationale
    - AS-IS-bug-carry-over list (from Phase 4)
    - Failure policy reminder
13. **Present the plan to the user** (use the dispatch plan template). Wait for confirmation.

Skip Phase 0 confirmation only if the user has explicitly said "go ahead with the whole pipeline" — and even then, post the plan and wait at least one turn unless the user repeats "proceed".

## Wave 1 — Test authoring (mode-dependent dispatch of 4 workers)

Per chosen mode:

- **parallel**: single message with 4 Agent calls in parallel (the per-UC fan-out for `equivalence-test-writer` happens inside the worker's own dispatch — it batches at 4 concurrent internally if invoked once per UC; alternatively the supervisor can fan out by invoking `equivalence-test-writer` N times directly and batching at 4 concurrent. Choose based on UC count: <= 20 → fan out from supervisor; > 20 → invoke once and let the worker chunk).
- **batched**: three messages — batch 1 (equivalence + backend), batch 2 (frontend), batch 3 (security).
- **sequential**: 4 messages, one per worker, in domain order (equivalence → backend → frontend → security).

After each batch (or worker), read outputs from disk. Verify:
- expected files exist with valid frontmatter
- no worker wrote outside permitted roots
- AS-IS source code (Python/Streamlit) is unchanged: run `git status --porcelain | grep -v 'tests/equivalence\|backend/src/test\|frontend/src/app\|e2e\|docs/analysis/05-tobe-tests'` and verify the result lists no AS-IS file modifications.

If any worker reports `status: blocked` or `confidence: low` on a foundational deliverable: surface to the user **before Wave 2**.

## Wave 1.5 — Human-in-the-loop checkpoint

Present to the user after all Wave 1 workers complete:
- counts: UCs tested / total, backend test files, frontend test files, E2E specs, security tests
- contract tests authored vs OpenAPI operationIds: <ratio>
- any blocking unresolved items

Ask: "Proceed to Wave 2 (performance comparison), revise a specific worker output, or stop?"

Non-negotiable when Wave 1 produced ≥ 1 `blocked` item or ≥ 5 `low` confidence sections. Otherwise recommended but skippable with `--no-checkpoint`.

## Wave 2 — Performance comparison (sequential, single Agent call)

Dispatch `performance-comparator`. It reads:
- Phase 3 `benchmark-baseline.json` (AS-IS reference)
- Phase 4 `docs/refactoring/api/openapi.yaml` (operations to load-test)
- Wave 1 backend tests (to identify which BC scenarios to load-test)

Produces:
- `e2e/perf/` — Gatling or k6 scenarios (one per critical UC and per high-traffic endpoint)
- `04-performance-comparison.md` — markdown report with deltas, p95 comparison table, regression flags
- `_meta/benchmark-comparison.json` — machine-readable

If `execute_policy` permits, runs the load tests and captures real deltas. Else writes scenarios and marks the report `status: partial — pending execution`.

After dispatch, read outputs. Aggregate `## Open questions` into `14-unresolved-questions.md`.

## Wave 3 — Execution & oracle capture (sequential, single Agent call)

Dispatch `tobe-test-runner`. It reads all Wave 1 + Wave 2 outputs and:
1. Runs `mvn test` for backend (if execute_policy permits) — captures JUnit XML, JaCoCo coverage, Spring Cloud Contract verifier results.
2. Runs `ng test --watch=false` for frontend (if execute_policy permits) — captures Karma/Jest coverage.
3. Runs `npx playwright test` (if execute_policy permits) — captures Playwright traces.
4. Runs `tests/equivalence/` Python harness against TO-BE deployment (or stubs out the diff if execute_policy is off).
5. Applies the failure policy: critical/high → escalate; medium/low → tag in `06-tobe-bug-registry.md` with `xfail`/`skip` markers.

Produces:
- `02-coverage-report.md` — line/branch coverage per BC, per layer
- `03-contract-tests-report.md` — pact / Spring Cloud Contract verdicts per OpenAPI operationId
- `06-tobe-bug-registry.md` — TBUG-NN entries
- `_meta/coverage.json` — machine-readable

After dispatch, read outputs. If the runner reports any `critical` or `high` finding without a documented disposition: **stop, do not declare Phase 5 complete; escalate** with a focused summary.

## Wave 4 — Equivalence synthesis (sequential, single Agent call)

Dispatch `equivalence-synthesizer`. It reads everything in `docs/analysis/05-tobe-tests/` plus the TO-BE codebase manifests and produces:
- `01-equivalence-report.md` — UC-by-UC table (AS-IS oracle vs TO-BE result), accepted-differences register (each requires PO sign-off), go-live verdict
- `README.md` — entry point with navigation links and reading order

After dispatch, read outputs. The equivalence report MUST list every UC from Phase 1 with one of: `equivalent`, `accepted-difference`, `regression-blocking`, `regression-accepted`, `not-tested-with-reason`. If any UC is missing or has no disposition, escalate.

## Wave 5 — Challenger (always ON)

Dispatch `tobe-testing-challenger`. Adversarial review of all W1–W4 outputs. Produces:
- `_meta/challenger-report.md`
- appends entries to `14-unresolved-questions.md` under `## Challenger findings`

If the challenger reports ≥ 1 blocking contradiction or coverage gap: **stop, do not declare Phase 5 complete; escalate**.

## Final report

Post a final user-facing summary:

```
Phase 5 TO-BE Testing — complete.

Output: docs/analysis/05-tobe-tests/
Entry:  docs/analysis/05-tobe-tests/01-equivalence-report.md  ← PO sign-off here

Coverage summary:
- UCs covered:        <N> / <total>
- Backend coverage:   <line %>, <branch %>
- Frontend coverage:  <line %>, <branch %>
- Contract tests:     <pass> / <total> (vs OpenAPI)
- E2E specs:          <count>
- Security checks:    <count>; OWASP Top-10 findings: <N>

Equivalence verdict:
- equivalent:           <N> UCs
- accepted-difference:  <N> UCs (PO sign-off required — see report)
- regression-blocking:  <N> UCs
- regression-accepted:  <N> UCs (PO sign-off required)
- not-tested:           <N> UCs (with reasons)

Performance:
- p95 delta vs baseline: <%>
- Regressions > 10%:     <count> (blocking if > 0 unless PO accepts)

Quality signals:
- Open questions:    <N> (see 14-unresolved-questions.md)
- TBUG registry:     <medium: N, low: N>
- Challenger findings: <N>

Recommended next:
1. PO review of 01-equivalence-report.md → sign or request loop to
   Phase 4 hardening.
2. Address critical/high regressions (if any) via Phase 4 hardening
   loop, then re-run Phase 5 in `revise` mode for the affected scope.
3. Go-live decision based on quality gate (see workflow).
```
