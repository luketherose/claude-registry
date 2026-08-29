# Baseline runner — execution stages

> Reference doc for `baseline-runner`. Read at runtime when invoking
> pytest in stages, capturing snapshots, or running in write-only mode.

## Write-only mode (policy = `off`)

When the supervisor's bootstrap policy is `off`:

- Do NOT invoke pytest.
- Validate suite structure:
  - all expected files exist (compare against manifest from W1)
  - Python files compile (Bash: `python3 -m py_compile <file>` for each
    test file; collect errors but do not fail catastrophically)
  - fixture references resolve (grep for fixture names used in tests
    and verify they're defined in `conftest.py` / `factories.py`)
  - Postman JSON validates as JSON (Bash: `python3 -c "import json;
    json.load(open(<file>))"`)
- Write `baseline-report.md` marking the `Test execution` section as
  "deferred — execution policy = off".
- Write empty `_meta/as-is-bugs-found.md` with note "deferred to manual
  execution".
- Write empty `_meta/benchmark-baseline.json` and `_meta/test-coverage.json`
  with `null` values and note "to be populated by manual run".
- Status: `partial` (because the oracle is not captured yet).

## Write+execute mode (policy = `on`) — preflight

- Verify deps installed (Bash: `python3 -m pytest --version` etc.). If
  missing, attempt install (Bash: `pip install pytest pytest-benchmark
  pytest-regressions pytest-cov responses respx freezegun`). On failure,
  fall back to write-only and surface to supervisor.
- Run pytest in stages (below).
- Capture oracle artifacts.
- Apply failure policy to red tests.
- Write the report.

## Pytest invocation — staged

Run in stages so failures in one stage don't block recording for the
others.

### Stage A — Functional + integration (no benchmark)

```bash
python3 -m pytest tests/baseline/ \
  --ignore=tests/baseline/benchmark \
  -v \
  --tb=short \
  --json-report --json-report-file=/tmp/baseline-functional.json \
  --cov=<repo_pkg> \
  --cov-report=json:docs/analysis/03-baseline/_meta/test-coverage.json
```

If `pytest-json-report` is not installed, fall back to parsing pytest's
text output line by line; less robust but works.

### Stage B — Benchmarks

```bash
python3 -m pytest tests/baseline/benchmark/ \
  -v \
  --benchmark-json=docs/analysis/03-baseline/_meta/benchmark-baseline.json \
  --benchmark-only
```

### Stage C — Postman (if collection generated)

If `tests/baseline/postman/` exists and `newman` is available:

```bash
newman run tests/baseline/postman/<service>.postman_collection.json \
       -e tests/baseline/postman/<service>.postman_environment.json \
       --reporters cli,json \
       --reporter-json-export /tmp/baseline-newman-<service>.json
```

If `newman` is not available, skip Postman execution and document this
in the report. The collection file remains valid; the user can run it
manually.

**NOTE on Postman execution**: it requires the AS-IS service to be
RUNNING at the env's `base_url`. If the user has not started the service,
expect connection errors — these are env issues, not AS-IS bugs. The
runner detects them by checking error category (connection refused vs.
4xx/5xx response) and flags as env failure, not as code failure.

## Snapshot capture

`pytest-regressions` writes snapshots automatically on first run if the
reference file doesn't exist. The runner verifies:

- a snapshot directory now exists at `tests/baseline/snapshot/` (or the
  configured location)
- it contains the expected number of snapshot files (one per
  `data_regression` / `dataframe_regression` / `image_regression` call)

Before running pytest the first time, ensure the snapshot dir is empty
or non-existent (otherwise pytest-regressions will compare against
existing snapshots and may report failures that are actually fresh
captures). The supervisor's bootstrap already prompted the user about
this — by the time you run, the policy is set.
