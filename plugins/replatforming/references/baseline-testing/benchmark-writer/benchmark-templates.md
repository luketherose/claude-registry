# Benchmark templates — time, memory, throughput, README

> Reference doc for `benchmark-writer`. Read at runtime when authoring the
> per-UC time / memory / throughput benchmark modules and the suite README
> (Method §2, §3, §4 and Outputs).

## Goal

Provide the canonical shape of every benchmark file the writer emits under
`tests/baseline/benchmark/`, plus the per-suite `README.md`. Selection logic,
determinism rules, and stop conditions stay in the agent body — only the
fenced-block templates live here.

## Time benchmark module — `bench_uc_<NN>.py`

```python
"""
Baseline time benchmark for UC-NN — <human title>.

Phase 5 oracle: TO-BE p95 must not exceed 110% of AS-IS p95.
Source: docs/analysis/02-technical/06-performance/performance-bottleneck-report.md
        (PERF-NN: <reference if applicable>)

Determinism: seed=42, time frozen, network mocked. The benchmark
measures CPU + I/O within mocks; external network is not measured.
"""

import pytest

# from <repo_pkg>.<module> import <function_under_test>


@pytest.fixture
def realistic_input(realistic_orders):
    return realistic_orders


def test_bench_uc_NN_realistic(benchmark, realistic_input):
    """UC-NN realistic-scale time benchmark."""
    result = benchmark(target_function, realistic_input)
    # Optional functional assertion to ensure we didn't regress to a no-op
    assert result is not None


def test_bench_uc_NN_minimal(benchmark, minimal_input):
    """UC-NN minimal-scale time benchmark — establishes overhead floor."""
    benchmark(target_function, minimal_input)
```

Conventions:
- Use the **realistic** fixture for the primary p95 number; this is what
  Phase 5 will gate against.
- Use the **minimal** fixture for an "overhead floor" — useful to detect
  regressions in cold-path / startup costs.
- Do NOT benchmark with the **edge** fixture — edge cases are not
  representative of normal performance.
- pytest-benchmark groups: tag each benchmark with
  `@pytest.mark.benchmark(group="uc-NN")` so reports cluster cleanly.
- Histogram disabled in CI but recorded JSON: invoke pytest with
  `--benchmark-json=docs/analysis/03-baseline/_meta/benchmark-baseline.json`
  (the supervisor's W2 baseline-runner does this).

## Memory benchmark module — `bench_memory.py`

```python
"""
Baseline memory benchmark.

Uses tracemalloc for peak / current measurement (no external deps).
Source: Phase 2 performance-bottleneck-report.md (PERF-NN where
memory was flagged).
"""

import tracemalloc
import pytest


def measure_memory(callable_, *args, **kwargs):
    tracemalloc.start()
    callable_(*args, **kwargs)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current, peak


def test_memory_uc_NN_realistic(realistic_orders):
    """Peak memory for UC-NN with realistic data must be recorded."""
    current, peak = measure_memory(target_function, realistic_orders)
    # Record only — Phase 5 reads this baseline; no assertion here.
    pytest.skip(f"Baseline recorded: peak={peak} bytes, current={current} bytes")
    # NOTE: we use skip(reason=...) as a recording channel since
    # pytest-benchmark doesn't natively track memory. The reason
    # string carries the metric; baseline-runner parses it into the
    # benchmark JSON.
```

Alternative: if the project already pins `memory-profiler`, prefer its
`@profile` decorator and run with `python -m memory_profiler`. Document
the choice in the module docstring.

## Throughput benchmark module — `bench_throughput.py` (optional)

```python
def test_throughput_uc_NN(benchmark):
    """Throughput: items/sec for UC-NN batch processor."""
    items = generate_items(1000)
    benchmark.pedantic(
        target_function,
        args=(items,),
        rounds=3,
        iterations=1,
    )
    # benchmark.stats holds wall time; throughput = len(items)/mean
```

If no throughput-relevant endpoint exists in the AS-IS, skip this file
entirely.

## Suite `README.md`

```markdown
---
agent: benchmark-writer
generated: <ISO-8601>
sources: [...]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# Baseline benchmarks

## Selection rationale

Selected UCs (with rationale):
- UC-03: PERF-02 (high) — N+1 query in profile lookup
- UC-07: realistic data > 10k rows; representative of typical load
- ...

Skipped UCs (with rationale):
- UC-12: pure UI rendering, no logic to benchmark

## Determinism

Seed: 42 (inherited from conftest)
Time: frozen
Network: mocked
Environment caveat: numbers are environment-dependent; the Phase 5
gate is RELATIVE (TO-BE p95 ≤ 110% of AS-IS p95), not absolute.

## Run command

\`\`\`
pytest tests/baseline/benchmark/ \
  --benchmark-json=docs/analysis/03-baseline/_meta/benchmark-baseline.json
\`\`\`

(Run by baseline-runner in W2 if --execute on.)

## Open questions
- ...
```

## Output

| Path | Schema | Owner |
|---|---|---|
| `tests/baseline/benchmark/bench_uc_<NN>.py` (×N) | time benchmark module | this agent |
| `tests/baseline/benchmark/bench_memory.py` | memory benchmark module | this agent |
| `tests/baseline/benchmark/bench_throughput.py` | throughput benchmark module (optional) | this agent |
| `tests/baseline/benchmark/README.md` | suite manifest | this agent |
