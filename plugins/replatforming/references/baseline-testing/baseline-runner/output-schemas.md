# Baseline runner — output schemas

> Reference doc for `baseline-runner`. Read at runtime when writing the
> AS-IS bugs registry, the baseline report, the oracle JSON files, or the
> reporting block returned to the supervisor.

## File 1 — `docs/analysis/03-baseline/_meta/as-is-bugs-found.md`

```markdown
---
agent: baseline-runner
generated: <ISO-8601>
sources: [pytest output, Phase 1, Phase 2 risk register]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# AS-IS bugs surfaced during baseline construction

This file records bugs in the AS-IS code discovered while building the
regression suite. Per Phase 3 policy, the AS-IS source is NEVER
modified; bugs are documented and tests are marked xfail / skip.

## Summary
- Critical (escalated): <N>
- High (escalated): <N>
- Medium (xfail): <N>
- Low (xfail): <N>
- Flaky (skip): <N>

## Bugs

### BUG-01 — <one-line>
- **Severity**: critical | high | medium | low | flaky
- **Test**: `tests/baseline/test_uc_NN_<slug>.py::test_uc_NN_alt_<X>`
- **Disposition**: escalated | xfail | skip
- **AS-IS location** (suspected): `<repo>/<path>:<line>` (function `<name>`)
- **UC ref**: UC-NN
- **Risk ref** (Phase 2): RISK-NN (if applicable)
- **Symptom**: <what the assertion expected vs what was returned>
- **Hypothesis**: <one-paragraph guess at root cause; "to be confirmed
  by debugger / developer-python in fix cycle">
- **Fix scope**: out of Phase 3 scope; for Phase 4 / fix-cycle attention

### BUG-02 — ...
```

If no bugs found or write-only mode: write the frontmatter + a single
note ("no bugs surfaced" or "deferred to manual execution") and an empty
`## Bugs` section.

---

## File 2 — `docs/analysis/03-baseline/baseline-report.md`

```markdown
---
agent: baseline-runner
generated: <ISO-8601>
sources:
  - tests/baseline/  (entire suite)
  - /tmp/baseline-functional.json
  - docs/analysis/03-baseline/_meta/benchmark-baseline.json
  - docs/analysis/03-baseline/_meta/test-coverage.json
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# Baseline report

## Execution mode
<write+execute | write-only>

## Test execution

| Stage | Result | Duration |
|---|---|---|
| Functional + integration | <N passed>, <N xfail>, <N skipped>, <N failed> | <duration> |
| Benchmarks | <N passed>, <N skipped> | <duration> |
| Postman (newman) | <N passed>, <N failed> (or "skipped — newman unavailable") | <duration> |
| **Total** | <pass count>/<total>, <duration> |

(If write-only: replace this section with: "Execution deferred to manual
run. Suite structure validated only. Run command: `pytest tests/baseline -v`")

## Coverage by use case

| UC-NN | Test file | Tests | Pass | xfail | skip | fail |
|---|---|---|---|---|---|---|
| UC-01 | test_uc_01_*.py | 3 | 3 | 0 | 0 | 0 |
| ... |

## Benchmarks (key numbers)

(Pull from `_meta/benchmark-baseline.json` — list mean / p95 for each
named benchmark. This is the AS-IS oracle Phase 5 will gate against.)

| Benchmark | Mean (s) | p95 (s) | StdDev |
|---|---|---|---|
| bench_uc_03_realistic | 0.234 | 0.289 | 0.012 |
| ... |

## AS-IS bugs surfaced
- Critical (escalated): <N>
- High (escalated): <N>
- Medium (xfail): <N>
- Low (xfail): <N>
- Flaky (skip): <N>

(See `_meta/as-is-bugs-found.md` for details.)

## Per-stage timing

| Stage | Started | Completed | Duration |
|---|---|---|---|
| Test execution Stage A | <ISO> | <ISO> | <duration> |
| Test execution Stage B | <ISO> | <ISO> | <duration> |
| Test execution Stage C | <ISO> | <ISO> | <duration> |
| Snapshot capture | <ISO> | <ISO> | <duration> |
| **Total** | <ISO> | <ISO> | <duration> |

## Recommendation

<one-paragraph: state of the baseline; whether it can serve as oracle
for Phase 5; any blocking items requiring user attention>

## Open questions

- ...
```

---

## Files 3 & 4 — oracle JSON files

| Path | Generator | Write-only-mode shape |
|---|---|---|
| `docs/analysis/03-baseline/_meta/benchmark-baseline.json` | `pytest-benchmark --benchmark-json=<path>` | `{ "benchmarks": [], "note": "to be populated by manual run" }` |
| `docs/analysis/03-baseline/_meta/test-coverage.json` | `pytest-cov --cov-report=json:<path>` | `{ "totals": null, "files": {}, "note": "to be populated by manual run" }` |

## File 5 — snapshot directory

`tests/baseline/snapshot/` — populated automatically by `pytest-regressions`
on first run. The runner does not write here directly; it only verifies the
directory exists with the expected file count after the run.

---

## Reporting block (text response to supervisor)

```markdown
## Execution mode
<write+execute | write-only>

## Files written / modified
- docs/analysis/03-baseline/baseline-report.md
- docs/analysis/03-baseline/_meta/as-is-bugs-found.md
- docs/analysis/03-baseline/_meta/benchmark-baseline.json
- docs/analysis/03-baseline/_meta/test-coverage.json
- tests/baseline/snapshot/<files>  (if pytest ran)
- tests/baseline/test_uc_NN_*.py  (xfail markers added on N tests)

## Test results
- Passed: <N>
- xfail: <N>  (medium / low — auto-marked)
- Skipped: <N>  (flaky / env)
- Failed (unresolved): <N>  (critical / high — escalated)

## AS-IS bugs surfaced
- Critical: <N>  (escalated)
- High: <N>  (escalated)
- Medium: <N>  (xfail applied)
- Low: <N>  (xfail applied)

## Confidence
high | medium | low

## Duration (wall-clock)
<seconds>

## Open questions / escalations
- <BUG-NN: critical, escalation context>
- ...
```

If you escalated any critical/high bugs, the supervisor will not declare
Phase 3 complete. Be explicit about each.
