# Phase 3 — Output layout & frontmatter contract

> Reference doc for `baseline-testing-supervisor`. Read at runtime when planning where workers write their outputs and what frontmatter / docstring every artefact must carry.

## Output roots

All outputs go under two roots:
- **Test artifacts**: `<repo>/tests/baseline/`
- **Documentation**: `<repo>/docs/analysis/03-baseline/`

```
tests/baseline/
├── conftest.py                          (fixture-builder — pytest config)
├── fixtures/                            (fixture-builder)
│   ├── minimal/                         (smallest valid datasets)
│   ├── realistic/                       (representative datasets)
│   └── edge/                            (boundary / error datasets)
├── test_uc_<NN>_<slug>.py               (usecase-test-writer — fan-out)
├── test_integration_<system>.py         (integration-test-writer)
├── benchmark/                           (benchmark-writer)
│   ├── bench_uc_<NN>.py
│   ├── bench_memory.py
│   └── bench_throughput.py              (only where applicable)
├── postman/                             (service-collection-builder — conditional)
│   ├── <service>.postman_collection.json
│   └── <service>.postman_environment.json
└── snapshot/                            (baseline-runner — captured at runtime)
    └── ...

docs/analysis/03-baseline/
├── README.md                            (you — index/navigation)
├── 00-context.md                        (you — system summary, scope, env, mode)
├── baseline-report.md                   (you / baseline-runner — pass/fail summary,
                                          coverage, timings, AS-IS bugs found)
├── _meta/
│   ├── manifest.json                    (you — run history with per-wave timings)
│   ├── benchmark-baseline.json          (baseline-runner — Phase 5 perf oracle)
│   ├── test-coverage.json               (baseline-runner — coverage by UC)
│   ├── as-is-bugs-found.md              (you — bugs surfaced during baseline)
│   └── challenger-report.md             (baseline-challenger)
└── unresolved-baseline.md               (you — aggregated)
```

Workers must not write outside these two roots. Verify after each dispatch by listing modified files.

## Frontmatter contract (markdown)

Every markdown file under `docs/analysis/03-baseline/` written by workers has YAML frontmatter:

```yaml
---
agent: <worker-name>
generated: <ISO-8601 timestamp>
sources:
  - .indexing-kb/<path>
  - docs/analysis/01-functional/<path>
  - docs/analysis/02-technical/<path>
  - <repo>/<source-path>:<line>     # only for narrowly scoped reads
confidence: high | medium | low
status: complete | partial | needs-review | blocked
duration_seconds: <int>             # NEW — execution timing
---
```

## Module-docstring contract (Python tests)

Python test files do not require YAML frontmatter, but each file MUST include a module docstring with:
- the UC-NN(s) covered (or "infrastructure: integration / benchmark / postman")
- source: which Phase 1 / Phase 2 artifacts justified the test
- determinism notes: seed value, time mock, network mock policy
