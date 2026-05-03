# Baseline runner — failure policy

> Reference doc for `baseline-runner`. Read at runtime when classifying
> a failing test (severity inference) and applying the policy
> (escalate / xfail / skip).

## Severity inference rules

Apply in order; first match wins. If unclear after all rules, default to
`high` and escalate.

1. If the test's docstring mentions a specific UC-NN, look up that UC's
   severity in Phase 1 (use case priority) → mirror it.
2. If the test's docstring mentions a RISK-NN from Phase 2, look up
   that risk's severity → mirror it.
3. If the assertion mentions security-relevant terms (auth, password,
   secret, injection, leak): severity = `critical`.
4. If the assertion mentions data-loss-relevant terms (delete, lost,
   corrupt, overwrite): severity = `critical`.
5. If the test name contains `happy_path`: severity = `high` (a primary
   flow is broken).
6. If the test name contains `alternative` or `alt`: severity = `medium`.
7. If the test name contains `edge`: severity = `low` (default), but
   override to `medium` if the assertion is about validation correctness.
8. Default: `medium`.

## Failure-policy matrix

| Severity | Action | Who decides |
|---|---|---|
| `critical` | escalate (do NOT mark) | supervisor |
| `high` | escalate (default proposal: xfail with bug note) | supervisor confirms |
| `medium` | mark `xfail` in source test file | runner (auto) |
| `low` | mark `xfail` in source test file | runner (auto) |
| `flaky` | mark `skip` in source test file | runner (auto) |

## Marker pattern

To mark a test as `xfail` / `skip`, **edit the test file** (this is the
only write authorization the runner has on test files):

Replace:
```python
def test_uc_03_alt_partial_refund(...):
    ...
```

With:
```python
@pytest.mark.xfail(
    reason="AS-IS bug found: partial refund discount calc returns net "
           "instead of gross. See _meta/as-is-bugs-found.md#BUG-04.",
    strict=True,  # if it starts passing later, alert
)
def test_uc_03_alt_partial_refund(...):
    ...
```

`strict=True` means the test reports XPASS (and fails the suite) if it
unexpectedly passes — this catches AS-IS bugs that get fixed out-of-band
so the test doesn't silently lie.

## Strictness rules

The runner is the ONLY worker that modifies test files (to add `xfail`
markers). It must NEVER:

- modify AS-IS source code
- modify fixture files (those are owned by `fixture-builder`)
- modify `conftest.py` (same)
- modify Postman collections (those are owned by
  `service-collection-builder`)
- silently downgrade severity to avoid escalation
- pretend a critical/high failure is medium

If the runner cannot determine severity confidently, escalate as `high`
and let the user decide.

## Classification loop (pseudo)

```
For each test in the report:
  if status == "passed":           record_passed()
  elif status == "skipped":        record_skipped(reason)
  elif status == "xfailed":        record_xfail(reason)
  elif status == "failed":
      severity = infer_severity(test_path, test_name, assertion_message)
      apply_failure_policy(test, severity)
```
