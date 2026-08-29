# Phase 5 — Sub-agents catalogue

> Reference doc for `tobe-testing-supervisor`. Read at runtime when planning a wave's dispatch — confirms which sub-agent owns which output target and which wave it belongs to.

## Sub-agents available (Sonnet)

| Sub-agent | Wave | Output target |
|---|---|---|
| `equivalence-test-writer` | W1 (fan-out per UC) | `tests/equivalence/test_uc_<id>.py` (or .ts/.java per stack) |
| `backend-test-writer` | W1 | `backend/src/test/java/...` (unit + integration + Spring Cloud Contract) |
| `frontend-test-writer` | W1 | `frontend/src/app/**/*.spec.ts`, `e2e/` (Playwright) |
| `security-test-writer` | W1 | `backend/src/test/.../security/`, `e2e/security/`, `05-security-findings.md` |
| `performance-comparator` | W2 | `e2e/perf/` (Gatling or k6), `04-performance-comparison.md`, `_meta/benchmark-comparison.json` |
| `tobe-test-runner` | W3 | execution results, `02-coverage-report.md`, `03-contract-tests-report.md`, `06-tobe-bug-registry.md`, `_meta/coverage.json` |
| `equivalence-synthesizer` | W4 | `01-equivalence-report.md`, `README.md`, `00-context.md` |
| `tobe-testing-challenger` | W5 (always ON) | `_meta/challenger-report.md`, appends to `14-unresolved-questions.md` |

## External agents (follow-up only — not dispatched inline)

- `code-reviewer` — invoked separately on PRs touching TO-BE test code.
- `debugger` — invoked separately when an equivalence failure has unclear root cause (e.g., snapshot diff that doesn't match any known bug).
