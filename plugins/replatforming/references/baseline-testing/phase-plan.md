# Phase 3 — Phase plan

> Reference doc for `baseline-testing-supervisor`. Read at runtime to drive the bootstrap dialog, dispatch each wave, write the phase verification report, and (on `iterate`) re-dispatch affected test writers.
>
> **Iteration loop.** Phase 3 ends with the HITL iteration loop documented in [`../refactoring-workflow/iteration-loop.md`](../refactoring-workflow/iteration-loop.md). After Wave 3b the supervisor returns control to `refactoring-supervisor`, which presents `approve / iterate / stop`. On `iterate`, this supervisor is re-dispatched with `Resume mode: iterate` and a structured delta — see § "Wave 4 — Iteration handling" below.
 (Phase 0 bootstrap + Wave 0–3)

> Reference doc for `baseline-testing-supervisor`. Read at runtime to drive the bootstrap dialog and dispatch each wave. The supervisor body keeps only the wave dependency chain and HITL checkpoints; the per-wave details live here.

## Phase 0 — Bootstrap (supervisor only)

1. **Detect resume mode**. Inspect what is on disk and pick one of:

   | Condition | Resume mode |
   |---|---|
   | No `tests/baseline/` AND no `docs/analysis/03-baseline/` | `fresh` |
   | Either dir exists but `docs/analysis/03-baseline/_meta/manifest.json` reports `partial` / `failed` / missing | `resume-incomplete` |
   | Both dirs exist AND manifest reports `complete` | `complete-eligible` — ask the user before doing anything |

   When `complete-eligible` triggers, ask the user verbatim:

   ```
   The AS-IS baseline at tests/baseline/ + docs/analysis/03-baseline/
   is already COMPLETE in this repo.
     Last run:    <ISO-8601 from manifest>
     Tests:       <authored count> authored, <executed count> executed
     Snapshots:   <count> captured
     Benchmarks:  <count> recorded
     Postman:     <present | not applicable>

   What should I do?
     [skip]    keep the existing baseline as-is, do nothing.
     [re-run]  re-run the full pipeline from W0 (you'll see explicit
               per-artifact overwrite confirmations for snapshots and
               benchmark JSON — these are the AS-IS oracle for Phase 5
               and overwriting them resets the equivalence reference).
     [revise]  inspect a specific section together first (e.g.,
               regenerate only one UC test, refresh benchmarks only).
   ```

   Default deny: do not proceed without an explicit answer. Default recommendation: `skip` (the oracle is precious — re-running it without reason will reset the equivalence reference for Phase 5).
   If the user answers `skip`, post a short recap pointing to `docs/analysis/03-baseline/README.md` and exit cleanly. If `revise`, ask which section(s) to refresh and dispatch only those workers. If `re-run`, continue with the remaining bootstrap steps.

   In `resume-incomplete` mode, surface the manifest status to the user and recommend `re-run` (do not auto-resume from broken state); the user may override with `revise`.

   In `fresh` mode, continue with the remaining bootstrap steps.

2. Verify `.indexing-kb/`, `docs/analysis/01-functional/`, `docs/analysis/02-technical/` exist and have `status: complete` in their respective manifests.
3. Read Phase 1 use cases to compute N (UC count).
4. Read Phase 2 integrations to compute I and detect services (S).
5. Read Phase 2 performance hotspots to compute P.
6. **Detect environment** per Q1 adaptive logic. Determine `--execute on | off`.
7. Read or create `docs/analysis/03-baseline/_meta/manifest.json` (resume support).
8. Check existing artifacts (only if resume mode is `re-run` or `resume-incomplete`):
   - `tests/baseline/` non-empty → ASK overwrite | augment | abort
   - `tests/baseline/snapshot/` non-empty → ASK overwrite | keep
   - `_meta/benchmark-baseline.json` exists → ASK overwrite | keep
   Do NOT silently overwrite oracle artifacts. (In `revise` mode this step is per-section, not global.)
9. Determine **dispatch mode** per the rules above.
10. Write `00-context.md` with:
    - 1-paragraph system summary
    - Scope (which UCs / integrations are in)
    - Stack mode (Streamlit / generic)
    - Resume mode
    - Execution policy (write+execute / write-only) + detection results
    - Service detection result (Postman collection on / off)
    - Dispatch mode + rationale
    - Failure policy reminder (Q2)
11. **Present the plan to the user** (use the dispatch plan template). Wait for confirmation.

Skip Phase 0 confirmation only if the user has explicitly said "go ahead with the whole pipeline" — and even then, post the plan and wait at least one turn unless the user repeats "proceed".

## Wave 0 — Fixture preparation (sequential, one agent)

Dispatch `fixture-builder`. Records `started_at` / `completed_at` in manifest. After completion, read the produced fixtures + conftest.py. Verify they exist and the conftest.py defines the expected pytest plugins (seed fix, time mock, network mock).

If the user passed `--execute on`, install the test deps before proceeding (Bash: `pip install pytest pytest-benchmark pytest-regressions pytest-cov`). If the install fails, fall back to `--execute off` and warn.

**Mini-recap (you to user)** — see `recap-templates.md`.

## Wave 1 — Test authoring (mode-dependent dispatch)

Per chosen mode:
- **parallel**: single message with all Agent calls
- **batched**: 1 message per batch, batches sequential
- **sequential**: 1 message per worker

For `usecase-test-writer` fan-out, pass each invocation:
- the UC-NN it owns
- the path to its `06-use-cases/UC-NN-*.md`
- the path to fixtures under `tests/baseline/fixtures/`
- the relevant Phase 2 risk findings touching that UC

After each batch (or each worker in sequential mode), read outputs:
- expected files exist
- module docstrings present
- AS-IS purity check (no Java/Spring/Angular tokens)
- worker not writing outside the two roots

If any worker reports `status: blocked`: surface to user before W2.

**Mini-recap after Wave 1** with per-worker durations.

## Wave 2 — Execution & oracle capture (sequential)

Dispatch `baseline-runner`. Pass:
- the execution policy (`on` / `off`)
- the failure policy from Q2
- the path to all Wave 1 outputs

If `--execute on`:
- runner runs pytest, captures snapshots + benchmarks + coverage
- on failure: applies the failure policy (escalates critical/high; xfails medium/low); writes `_meta/as-is-bugs-found.md`

If `--execute off`:
- runner only validates the structure of the suite (file existence, imports valid, no dead refs to fixtures); does not run pytest
- snapshots and benchmarks remain to be captured by the user later
- writes `_meta/as-is-bugs-found.md` empty with note "deferred to manual execution"

**Mini-recap after Wave 2** with execution time per pytest module + total.

If runner reports `critical` or `high` failures unresolved by the failure policy: STOP. Do not proceed to W3. Escalate.

## Wave 3 — Challenger (always ON, sequential)

Dispatch `baseline-challenger`. It performs adversarial review of all W0/W1/W2 outputs. Output: `_meta/challenger-report.md` plus appends to `unresolved-baseline.md`.

If challenger reports `≥ 1 blocking` issue: do not declare Phase 3 complete; escalate.

**Mini-recap after Wave 3.**

## Wave 3b — Phase verification report (supervisor only)

After Wave 3 (challenger) and before the iteration loop, the
supervisor writes `_meta/phase-verification-report.md` per the
canonical structure in
[`../refactoring-workflow/phase-verification-report.md`](../refactoring-workflow/phase-verification-report.md).

Phase-3 customization of the canonical structure:

| Section | Phase 3 source |
|---|---|
| 1. Executive summary | Manifest counts (UCs covered, tests written, pass/fail/xfail/skip) + bug register + challenger verdict. 2–3 paragraphs. |
| 2. What was produced | `tests/baseline/` (count of tests by category), `oracle/snapshot/`, benchmark JSON, optional Postman collection, `as-is-bugs-found.md`, `baseline-report.md`. |
| 3. What changed since iteration N-1 | `_meta/iteration-log.jsonl` latest entry. Omit on iteration 1. |
| 4. Open questions and gaps | Open-questions register + outstanding items in `baseline-report.md` + AS-IS bugs left as xfail. |
| 5. Audit verdicts | `_meta/baseline-challenger-report.md` (if ran) + per-UC test-outcome register (pass/xfail/skip with reasons). |
| 6. AS-IS purity check | Verify no test references target-tech tokens; drift scan over `tests/baseline/`. |
| 7. What to verify | At minimum: review every xfail with `severity: high` AS-IS bug note; review per-UC coverage gaps; confirm the oracle snapshot is the intended baseline. |
| 8. Recommendation | `approve` only if all verdicts PASS and no blocking issues (e.g., critical baseline failures); `iterate` otherwise. |

The verification report is mandatory. The iteration loop cannot start
without this file on disk.

## Wave 4 — Iteration handling (supervisor only)

After Wave 3b the supervisor returns control to
`refactoring-supervisor` for the HITL prompt. On user choice:

- **`approve`** → manifest entry's `approved_at: <ISO-8601>`;
  workflow advances. (Phase 3 has no PDF/PPTX exports to regenerate.)
- **`iterate`** → re-dispatched with `Resume mode: iterate` and a
  delta path. The supervisor:
  1. Reads the delta from `_meta/iteration-log.jsonl` (latest).
  2. Snapshots prior outputs to `_meta/snapshots/iter-<K>/`.
  3. Re-dispatches sub-agents per this mapping:

     | Adjustment target | Sub-agents to re-dispatch |
     |---|---|
     | UC test coverage (UC-NN) | usecase-test-writer for the affected UCs → baseline-runner |
     | integration test scope (I-NN) | integration-test-writer → baseline-runner |
     | fixtures / inputs | fixture-builder → all affected test writers → baseline-runner |
     | service collection | service-collection-builder → integration-test-writer → baseline-runner |
     | benchmark suite | benchmark-writer → baseline-runner |
     | test disposition dispute (xfail / blocking?) | route to deliberative-decision-engine first; re-decide; then update `as-is-bugs-found.md` |
     | oracle snapshot regeneration | baseline-runner only (re-capture oracle) |

  4. Always re-runs Wave 2 (baseline-runner) and Wave 3b
     (verification report). Wave 3 (challenger) re-runs if requested
     or if > 30% of artifacts changed.
- **`stop`** → manifest `status: partial`; end.

### Manifest update for iterations

Every iteration appends to `_meta/manifest.json` `runs[]`:

```json
{
  "run_id": "<ISO-8601>",
  "iteration": <K>,
  "trigger": "fresh | iterate | full-rerun",
  "delta_ref": "_meta/iteration-log.jsonl#<line>",
  "waves": [ ... ],
  "deliberation_traces": ["<trace-id>", ...],
  "status": "complete | partial | failed",
  "approved_at": null | "<ISO-8601>"
}
```

`approved_at` is set only on `approve` — it is the lock signal that
the baseline is final and ready to serve as the Phase 4 oracle.

## Final report (legacy compatibility)

The "Phase 3 — complete" free-text closing block is superseded by the
verification report's section 1 ("Executive summary"). The
recap-templates.md final-report block is retained only for backward
compatibility with the older recap pipeline and is no longer the
primary HITL surface.
