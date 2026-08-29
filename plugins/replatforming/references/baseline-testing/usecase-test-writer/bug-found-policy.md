# Usecase-test-writer — AS-IS bug-found policy

> Reference doc for `usecase-test-writer`. Read at runtime when the writer
> detects a divergence between AS-IS behaviour and the UC spec (Method §7).

## Rule

If, while writing a test, you discover that the AS-IS behaviour diverges
from what `UC-NN-<slug>.md` says, you MUST NOT change the test to match
the broken behaviour.

## Procedure

1. **Write the test against the SPEC** — assert what the UC says, not what
   the source currently does.
2. **Add a marker comment** above the test:

   ```python
   # AS-IS-BUG: this test currently fails because <function> returns X
   # instead of Y per UC-NN spec. See docs/analysis/03-baseline/_meta/
   # as-is-bugs-found.md (BUG-NN to be assigned by baseline-runner).
   # Severity inferred: <critical|high|medium|low>.
   ```

3. **Surface in `## Open questions`** of your supervisor reply so the
   supervisor can route it to the failure-policy decision.

## Hard invariants

- NEVER fix the AS-IS source.
- NEVER lower the test bar (loosen assertions, mark `xfail` to hide it,
  switch to `skip` without a reason) to make a failing test pass.
- The bug ID is assigned later by `baseline-runner` after first execution;
  the writer leaves the `BUG-NN` placeholder.

## Severity heuristic (for the inferred severity in the marker)

| Inferred severity | When to use |
|---|---|
| critical | UC outcome is silently wrong (data corruption, financial impact) |
| high | UC outcome is wrong but visible (error, exception, missing screen) |
| medium | Alternative or edge flow diverges; happy path correct |
| low | Cosmetic / non-functional divergence (label, ordering) |

`baseline-runner` may upgrade or downgrade the severity once the suite
runs and the actual failure manifests.
