# Baseline challenger — output report template

> Reference doc for `baseline-challenger`. Read at runtime when writing
> the challenger report deliverables.

## File 1: `docs/analysis/03-baseline/_meta/challenger-report.md`

```markdown
---
agent: baseline-challenger
generated: <ISO-8601>
sources:
  - tests/baseline/  (full tree)
  - docs/analysis/03-baseline/  (full tree)
  - docs/analysis/01-functional/  (for coverage check)
  - docs/analysis/02-technical/  (for severity cross-ref)
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# Challenger report — Phase 3 Baseline Testing

## Summary
- Blocking issues:    <N>
- Needs-review:       <N>
- Nice-to-have:       <N>

## Findings by check

### 1. Coverage gaps

#### CHL-01 — UC-04 has no test file
- **Type**: gap
- **Where**: `tests/baseline/`
- **Description**: Phase 1 lists UC-04 (User registration) but no
  `test_uc_04_*.py` exists.
- **Suggested fix**: dispatch usecase-test-writer for UC-04 OR
  document in `as-is-bugs-found.md` that UC-04 is unimplemented.
- **Severity**: blocking

### 2. AS-IS source modifications

#### CHL-NN — <title>
- **Type**: source-modified
- **Where**: `<repo>/<path>:<line>`
- **Description**: git status shows `<file>` modified outside the
  permitted output roots.
- **Suggested fix**: revert the change immediately; investigate which
  worker made it; never repeat.
- **Severity**: blocking

### 3. Determinism risks

#### CHL-NN — Raw `requests.get` without mock
- **Type**: determinism-risk
- **Where**: `tests/baseline/test_integration_<X>.py:42`
- **Description**: `requests.get("https://api.real.example/...")` is
  not wrapped in a `@responses.activate` decorator; this test will
  attempt real network on every run.
- **Suggested fix**: add `@responses.activate` and stub the response.
- **Severity**: blocking

### 4. Oracle integrity

#### CHL-NN — Missing benchmark JSON
- **Type**: oracle-integrity
- **Where**: `_meta/benchmark-baseline.json`
- **Description**: file is empty / doesn't exist despite execution
  policy = on.
- **Suggested fix**: re-run baseline-runner Stage B; check pytest-benchmark
  is installed.
- **Severity**: blocking

### 5. Severity-mismatch

#### CHL-NN — Critical bug marked xfail without escalation
- **Type**: severity-mismatch
- **Where**: `tests/baseline/test_uc_07_*.py::test_uc_07_security_check`
- **Description**: assertion involves "secret leaked"; severity should
  be critical, but disposition is xfail (silent).
- **Suggested fix**: re-classify as critical, escalate to user, remove
  xfail marker until user confirms disposition.
- **Severity**: blocking

### 6. Streamlit-specific risks (if applicable)

#### CHL-NN — session_state leak across tests
- **Type**: streamlit-risk
- **Where**: `tests/baseline/test_uc_03_*.py`
- **Description**: directly mutates `st.session_state` without using
  the `reset_session_state` fixture; previous test's state may persist.
- **Suggested fix**: refactor to use `app_test` fixture; remove direct
  session_state mutation.
- **Severity**: needs-review

### 7. Postman collection integrity

#### CHL-NN — Hard-coded token in environment file
- **Type**: oracle-integrity / security
- **Where**: `tests/baseline/postman/payments.postman_environment.json`
- **Description**: `access_token` value is a real-looking token instead
  of `<placeholder>`.
- **Suggested fix**: replace with placeholder; if it's a real token,
  rotate it immediately.
- **Severity**: blocking

## Verdict

```
Blocking issues:  <N>
Phase 3 ready:    <yes | no — see blocking issues above>
```

If `Phase 3 ready: no`: the supervisor must NOT declare Phase 3
complete and must escalate.
```

## File 2: appended section in `docs/analysis/03-baseline/unresolved-baseline.md`

```markdown
## Challenger findings

(Bulleted summary; cross-link by CHL-NN to the detailed report.)

- **CHL-01** [blocking] coverage gap: UC-04 has no test file
- **CHL-02** [blocking] determinism: raw network call in
  test_integration_X.py:42
- ...
```

If `unresolved-baseline.md` does not yet have a `## Challenger findings`
heading, add it. If it does (from a previous run), replace its content
with the latest run's findings.

## Finding shape (per check)

For each check, list every finding with:

- **Type**: gap | contradiction | as-is-violation | source-modified |
  determinism-risk | oracle-integrity | severity-mismatch |
  streamlit-risk | duplicate
- **Where**: which file(s) or test ID
- **Description**: one paragraph
- **Suggested fix**: short, actionable
- **Severity of the meta-finding**: blocking | needs-review |
  nice-to-have
