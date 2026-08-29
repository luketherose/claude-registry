# Phase 5 — Execution, failure & dispatch-mode policies

> Reference doc for `tobe-testing-supervisor`. Read at runtime when answering the execution policy, applying the failure-severity matrix, or deciding the W1 dispatch mode.

## Execution policy (adaptive)

The supervisor decides whether to run the test suites or just write them. Mirrors the Phase 3 baseline-testing-supervisor pattern.

### Detection (run during bootstrap)

1. `mvn --version` exits 0? → backend execution candidate
2. `cd backend && mvn -q -DskipTests dependency:resolve` succeeds in < 60s? → backend buildable
3. `cd frontend && npm install --prefer-offline` exits 0? → frontend buildable
4. `cd frontend && npx playwright --version` exits 0? → E2E candidate
5. Any docker daemon running? → Testcontainers candidate

### Decision tree

```
if (mvn OK && backend buildable && docker OK) AND
   (npm OK && playwright OK):
  execute_policy = on (full execute: mvn test + ng test + playwright)
elif backend OK only:
  execute_policy = backend-only (write FE tests, execute BE only)
elif frontend OK only:
  execute_policy = frontend-only (write BE tests, execute FE only)
else:
  execute_policy = off (write all tests, execute none — author-only mode)

User can override with --execute on | off | auto
```

In `off` mode, all workers still write tests (the suites must exist for go-live), but `tobe-test-runner` validates structure-only and the equivalence-synthesizer marks the report `status: partial — pending execution` with explicit instructions for the user to run the suite in a CI-equivalent environment.

## Failure policy

When tests are executed (W3) and fail, apply this matrix:

| Severity | Examples | Disposition |
|---|---|---|
| critical | functional regression on a critical UC, security hole (auth bypass), perf p95 > +10%, contract test fail vs OpenAPI | **escalate immediately**; do NOT proceed to W4; mark `01-equivalence-report.md` blocked |
| high | functional regression on a non-critical UC, OWASP Top-10 finding (high), missing endpoint vs OpenAPI | **escalate at W3 end**; record in `06-tobe-bug-registry.md` as `severity: high`; PO must accept or block |
| medium | minor visual diff, non-load-bearing perf delta < +10%, low-severity OWASP finding | record in `06-tobe-bug-registry.md` as `severity: medium`; mark test `xfail` with reason; do NOT fix in this phase |
| low | flaky test (env), formatting diff in non-load-bearing snapshot | record as `severity: low`; mark `xfail`/`skip` with reason |

**No fixes are applied in this phase.** Fixes belong to a Phase 4 hardening loop. The supervisor can recommend a return to Phase 4 in the final report, but it does not modify TO-BE source code itself.

## Dispatch mode decision (parallel / batched / sequential)

The supervisor decides the dispatch mode for **Wave 1 only** (4 workers — note the fan-out for `equivalence-test-writer` is per-UC and is its own concurrency story). Wave 2 onward is sequential by design.

### Decision tree

```
1. Did the user pass --mode <X>?
   -> Yes: use it.
   -> No:  continue.

2. Compute UC count N (from Phase 1 06-use-cases/) and
         BC count B (from Phase 4 .refactoring-kb/00-decomposition/).

3. Apply rules:
   a. If any prior phase manifest reports `partial`
      -> sequential (quality over speed)
   b. If N <= 20 AND B <= 5
      -> parallel (single tool call: 4 W1 workers + N parallel
         equivalence-test-writer fan-outs, batched at 4 concurrent)
   c. If N <= 60 OR B <= 12
      -> batched (3 batches: [equivalence + backend], [frontend],
         [security])
   d. Else
      -> sequential (4 workers one at a time, with equivalence-test-writer
         fan-out batched at 4 concurrent inside its slot)
```

### Mode confirmation

Before dispatching Wave 1, post the chosen mode to the user with the rationale. The user may override.

```
=== Phase 5 — Wave 1 dispatch plan ===

UC count:        <N>
Bounded contexts: <B>
Execute policy:  on | backend-only | frontend-only | off
Dispatch mode:   parallel | batched | sequential
Rationale:       <one line>

Workers (4 + per-UC fan-out):
  - equivalence-test-writer (xN, batched at 4 concurrent)
  - backend-test-writer
  - frontend-test-writer
  - security-test-writer

Confirm: proceed with this mode? [yes / change to <X> / stop]
```

Do not dispatch without explicit confirmation.
