# Phase 3 — Wave overview, sub-agents matrix, and mode flags

> Reference doc for `baseline-testing-supervisor`. Read at runtime to look
> up the sub-agents available, the mode flags that drive Phase-3 behaviour,
> and the wave-by-wave dispatch plan at a glance. Detailed dispatch
> instructions for each wave live in [`phase-plan.md`](phase-plan.md).

## Sub-agents available

| Sub-agent | Wave | Output target |
|---|---|---|
| `fixture-builder` | W0 | `tests/baseline/fixtures/`, `tests/baseline/conftest.py` |
| `usecase-test-writer` | W1 (fan-out per UC) | `tests/baseline/test_uc_<NN>_<slug>.py` |
| `integration-test-writer` | W1 | `tests/baseline/test_integration_<system>.py` |
| `benchmark-writer` | W1 | `tests/baseline/benchmark/` |
| `service-collection-builder` | W1 (conditional) | `tests/baseline/postman/` |
| `baseline-runner` | W2 | `tests/baseline/snapshot/`, `_meta/benchmark-baseline.json`, `_meta/test-coverage.json` |
| `baseline-challenger` | W3 (always ON) | `_meta/challenger-report.md` |

`service-collection-builder` is dispatched only if the bootstrap detects
exposed services (REST/HTTP endpoints owned by the AS-IS app, from the
Phase 2 integration map). See [`policies.md`](policies.md#service-detection-gate-for-service-collection-builder)
for the detection algorithm.

## Mode flags (Q1–Q2)

Two mode flags drive Phase-3 behaviour. Default values are tuned for the
common case; switch to non-defaults only with explicit user request.

| Flag | Default | Alternatives | What it controls |
|---|---|---|---|
| `--execute` (Q1) | `auto` | `on`, `off` | Whether to run pytest at W2 (write+execute) or write-only |
| `--mode` (Wave-1 dispatch) | `auto` | `parallel`, `batched`, `sequential` | How the W1 fan-out is dispatched |
| Failure policy (Q2) | strict critical/high; xfail medium/low | — | What happens when a baseline test fails |
| Service detection | adaptive | force on/off via user override | Whether `service-collection-builder` runs in W1 |

For the full description of each mode, the bootstrap detection heuristics,
the failure-severity matrix, and the dispatch decision algorithm, see
[`policies.md`](policies.md).

## Phase plan (overview)

| Step | Wave | Mode | Dispatched agents | Blocks |
|---|---|---|---|---|
| Phase 0 | Bootstrap | supervisor only | — | all waves until confirmed |
| W0 | Fixtures | sequential, single | `fixture-builder` | W1 |
| W1 | Test authoring | per `--mode` (parallel / batched / sequential) | `usecase-test-writer` × N + `integration-test-writer` + `benchmark-writer` + `service-collection-builder` (conditional) | W2 |
| W2 | Execution & oracle | sequential, single | `baseline-runner` (per `--execute`) | W3 |
| W3 | Challenger | always ON, sequential | `baseline-challenger` | completion |
| Recap | — | supervisor only | — | end |

For the full per-wave dispatch instructions (HITL prompts, escalation
conditions per wave, install steps for `--execute on`), see
[`phase-plan.md`](phase-plan.md).

For the per-wave mini-recap and the closing-report schemas, see
[`recap-templates.md`](recap-templates.md).

For the worker prompt boilerplate, see
[`dispatch-prompt-template.md`](dispatch-prompt-template.md).
