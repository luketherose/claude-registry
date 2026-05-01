# Phase 3 — Execution, failure, service-detection & dispatch-mode policies

> Reference doc for `baseline-testing-supervisor`. Read at runtime when answering Q1 (execution policy), Q2 (failure policy), the service-detection gate, or the dispatch-mode decision.

## Q1 — Execution policy (adaptive)

The supervisor decides whether to **write only** or **write + execute** during bootstrap.

```
1. Did the user pass --execute on/off?
   -> Yes: use it.
   -> No: continue.

2. Detect environment:
   - python3 available?            (Bash: command -v python3)
   - python version >= 3.10?       (Bash: python3 --version)
   - pytest installed?             (Bash: python3 -m pytest --version)
   - pytest-benchmark installed?
   - pytest-regressions installed?
   - is the project installable?   (look for pyproject.toml / setup.py / requirements.txt
                                    and check if a venv exists at .venv/)
   - is Streamlit installed?       (only matters for AppTest)

3. Decision:
   - all checks pass        -> --execute on    (run pytest at W2)
   - python OK, pytest absent -> --execute off (write-only, instruct user
                                                to install: pip install pytest
                                                pytest-benchmark pytest-regressions)
   - python missing         -> --execute off + warning + ask if user wants to
                               proceed with write-only
```

Surface the detection result and chosen policy explicitly in the bootstrap brief. The user can override.

## Q2 — Failure policy (strict critical/high, xfail medium/low)

Baseline tests can fail because:
- the test is wrong → the worker must fix the test (acceptable; the AS-IS source is read-only)
- the AS-IS code has a latent bug → **never fix the AS-IS code**

When `baseline-runner` reports a failure, classify the failure by **impact severity** (this is severity of the underlying behavior bug, not test-flakiness severity):

| Impact severity | Action |
|---|---|
| `critical` (data loss, security, billing, irreversible) | **Stop**, do not declare Phase 3 complete; surface to the user with full context; record in `_meta/as-is-bugs-found.md`; ask whether to proceed with the bug documented or pause for fix-cycle (the fix cycle is OUT OF SCOPE for Phase 3 — the user goes elsewhere to fix it) |
| `high` (incorrect output in a primary user flow) | **Escalate** to user; default proposal: mark `xfail` with explicit bug note + record in `_meta/as-is-bugs-found.md`; user confirms or pauses |
| `medium` (incorrect output in alternative or rare flow) | Mark `xfail` with `reason="AS-IS bug found in <function>; see _meta/as-is-bugs-found.md#BUG-NN"`; continue; record |
| `low` (cosmetic, edge case, non-functional) | Mark `xfail` with reason; continue |
| flaky / non-deterministic / env issue | Mark `skip` with reason; flag in `_meta/as-is-bugs-found.md` as "flaky test (not a bug)"; continue |

Severity is inferred from:
- which UC the failing test covers (UC severity from Phase 1 if available)
- which technical risk it touches (Phase 2 risk register if available)
- the test's own assertion semantics (data-loss assertion vs cosmetic)

If unclear, default to `high` and escalate.

`as-is-bugs-found.md` is the canonical record of bugs surfaced during baseline construction. Every entry has an ID `BUG-NN`, severity, location, description, the test that found it, and the disposition (xfail / skip / escalated).

## Service detection (gate for `service-collection-builder`)

In bootstrap, decide whether to dispatch `service-collection-builder`:

```
Read docs/analysis/02-technical/05-integrations/integration-map.md.
If it lists at least one INBOUND or BIDIRECTIONAL integration owned by
the AS-IS application (i.e., the app exposes endpoints to consumers,
not just calls external systems), then:
   service-collection-builder ON
Else:
   service-collection-builder OFF
   Note in bootstrap: "no exposed services detected — Postman collection
   skipped"
```

Common positive signals (from Phase 2):
- FastAPI / Flask / Django REST endpoints in the same repo
- Streamlit pages that import a co-located REST library
- Webhook receivers, message-queue consumers exposed as HTTP

Common negative signals:
- Pure Streamlit app with only outbound HTTP to external services
- CLI / batch jobs with no HTTP surface

If ambiguous, ask the user.

## Dispatch mode decision (parallel / batched / sequential)

The supervisor decides the dispatch mode for **Wave 1 only**. Wave 0 is always sequential (single agent), Wave 2 is always sequential, Wave 3 is always sequential.

```
1. --mode esplicito? Use it. Skip the rest.

2. Read inputs:
   - UC count (N) from docs/analysis/01-functional/06-use-cases/
   - integration count (I) from docs/analysis/02-technical/05-integrations/
   - service detection result (S = on | off)
   - performance hotspot count (P) from Phase 2

3. Workers in W1:
   - usecase-test-writer × N (one per UC)
   - integration-test-writer × 1
   - benchmark-writer × 1
   - service-collection-builder × {0, 1}  (conditional)

   Total = N + 2 + S

4. Apply rules in order:
   a. If any KB section is partial / needs-review > 30%
      -> sequential
   b. If total <= 6 AND --cheap not set
      -> parallel (single tool call)
   c. If total <= 16
      -> batched (groups of 4)
   d. Else
      -> sequential (or batched of 4 if user agrees on a longer run)
```

### Batching plan (used in `batched` mode only)

Group UCs by domain affinity (cluster from Phase 1 feature map) so each batch shares similar fixtures. Always include `integration-test-writer`, `benchmark-writer`, and `service-collection-builder` (if on) in the FIRST batch (they don't depend on per-UC artifacts and benefit from early completion).

### Mode confirmation

Before dispatching Wave 1, post the chosen mode with rationale:

```
=== Phase 3 Wave 1 dispatch plan ===

UCs:                <N>   (from Phase 1)
Integrations:       <I>
Performance hotspots: <P>
Services exposed:   <yes / no>
Execution policy:   write+execute | write-only

Workers in Wave 1 ({total}):
  - usecase-test-writer × <N>
  - integration-test-writer
  - benchmark-writer
  - service-collection-builder           # only if services detected

Chosen mode:    parallel | batched | sequential
Rationale:      <one line>

Confirm: proceed with this plan? [yes / change to <X> / stop]
```
