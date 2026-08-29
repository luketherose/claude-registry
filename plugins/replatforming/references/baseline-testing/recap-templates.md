# Phase 3 — Step recap & final phase recap templates

> Reference doc for `baseline-testing-supervisor`. Read at runtime when posting the per-wave mini-recap or the closing report.

## Step recap template (after every wave / after every agent dispatch)

After each wave (or each agent in sequential mode), post a concise recap. Keep it tight — 6–10 lines, never verbose.

```
=== Wave <N>: <name> — completed ===

Duration:  <human-readable, e.g., "2m 14s">
Agents:    <N> (parallel | batched | sequential)
Outputs:   <count> files written

Per-agent timings:
- <agent-1>:  <duration>   [status]
- <agent-2>:  <duration>   [status]
- ...

Notes:     <one-line, e.g., "all green" or "1 worker partial — see ...">

Next:      <what comes next>
```

Compute durations from the manifest's `started_at` / `completed_at` fields (ISO-8601). The supervisor records timestamps on dispatch and on result.

When workers run in parallel, the per-agent timing is the worker's self-reported wall time; the wave duration is the longest among them (the parallel envelope), not the sum.

## Final phase recap template

```
Phase 3 Baseline Testing — complete.

Output (tests):  tests/baseline/
Output (docs):   docs/analysis/03-baseline/
Entry point:     docs/analysis/03-baseline/README.md

Coverage:
- Use cases tested:        <covered>/<total>  (<pct>%)
- Integration boundaries:  <N>
- Benchmarks captured:     <N>
- Postman collection:      <yes / no>

Test execution (if --execute on):
- Total pytest run time:   <duration>
- Passed:                  <N>
- xfail (AS-IS bugs):      <N>  (see _meta/as-is-bugs-found.md)
- Skipped (env / flaky):   <N>
- Failed (unresolved):     <N>  (must be 0 for status: complete)

Per-wave timings:
- Wave 0 (fixtures):       <duration>
- Wave 1 (authoring):      <duration>   (<mode>)
- Wave 2 (execution):      <duration>
- Wave 3 (challenger):     <duration>
- Total:                   <duration>

Quality:
- Open questions:           <N>  (see unresolved-baseline.md)
- Low-confidence sections:  <N>
- Challenger findings:      <N>  (blocking | needs-review | nice-to-have)
- AS-IS bugs surfaced:      <N>  (critical | high | medium | low)

Recommended next: review _meta/as-is-bugs-found.md and unresolved-baseline.md
before proceeding to Phase 4.
```
