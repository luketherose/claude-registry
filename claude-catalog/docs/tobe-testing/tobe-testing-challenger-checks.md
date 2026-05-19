# The 8 checks — `tobe-testing-challenger`

> Reference doc for `tobe-testing-challenger`. Extracted from the
> agent body to keep it under the 10 000-char rubric ceiling.
> Read at runtime when the agent is dispatched.

## The 8 checks

Run all checks. Each finding gets a stable ID `CHL-NN` and a severity:

| Severity | Meaning | Effect on Phase 5 |
|---|---|---|
| blocking | Phase 5 cannot declare complete | Stop, escalate |
| high | PO must accept or fix before go-live | Recommend Phase 4 loop |
| medium | Defect in test or report; should be fixed before next run | Note |
| low | Cosmetic / nice-to-have | Note |

### Check 1 — UC coverage gap

For each UC in `phase1_uc_root`:
- Is there a corresponding equivalence test under
  `tests/equivalence/test_uc_<id>_*.py`?
- Is the UC referenced in `01-equivalence-report.md` § Verdict per UC?
- If UC priority is `critical` or `high` AND there is no test:
  → CHL with severity `blocking`.
- If UC priority is `medium` or `low` AND there is no test:
  → CHL with severity `high` (unless explicitly `not-tested-with-reason`
  in the report).

### Check 2 — OpenAPI ↔ TO-BE drift

For each `operationId` in OpenAPI:
- Is there a Spring Cloud Contract verifier test in
  `backend/src/test/.../contract/`?
- Is the operationId referenced in `03-contract-tests-report.md`?
- Did the runner record `verdict: pass`?
- If any operationId is missing a contract test:
  → CHL with severity `blocking`.
- If any operationId failed verification (drift):
  → CHL with severity `blocking`.

For each backend controller method:
- Is its mapping covered by an OpenAPI operationId?
- Methods with no OpenAPI counterpart are reverse-drift:
  → CHL with severity `high` (unless explicitly internal-only in
  Phase 4 hardening config).

### Check 3 — AS-IS source modifications (forbidden)

```bash
git status --porcelain
```

Filter to anything outside the writable Phase 5 paths:
- `tests/equivalence/`
- `backend/src/test/`
- `frontend/src/app/**/*.spec.ts`
- `frontend/src/test/`
- `e2e/`
- `docs/analysis/05-tobe-tests/`
- (markers added by the runner: `@Disabled`, `test.skip`, `xfail`
  in test files only)

Anything outside this list is a violation. The most serious case is
modification of AS-IS source code (Python/Streamlit), which is
**absolutely forbidden** in Phase 5.

→ CHL severity:
- AS-IS source modification: `blocking`
- TO-BE production source modification: `blocking`
- Other unexpected modification (e.g., docs outside Phase 5 root):
  `high`

### Check 4 — Mocked-when-shouldn't

Grep through Phase 5 tests for prohibited mock patterns:

```bash
# Equivalence harness must NOT mock the TO-BE deployment
grep -RE "(mock|stub|fake|MagicMock)" tests/equivalence/ | grep -vE "_helpers/|/conftest"

# E2E must NOT mock the backend
grep -RE "(MockBackend|nock\(|page\.route\()" e2e/ | grep -vE "test-utils/"
```

For each match:
- Equivalence harness using mocks: `blocking` (defeats the purpose).
- E2E `page.route()` overriding production endpoints: `high` unless
  scoped to a specific test that justifies it (e.g., webhook
  callback simulation).

### Check 5 — Equivalence claim integrity

For each UC marked `equivalent` in `01-equivalence-report.md`:
- Read the corresponding pytest module under
  `tests/equivalence/test_uc_<id>_*.py`.
- Verify the test actually compares against the AS-IS snapshot (not
  a hand-written expected value).
- Verify the diff helper is invoked (`assert_equivalent`).

A UC marked `equivalent` whose test does NOT compare to the snapshot
is a false claim:
→ CHL severity `blocking`.

### Check 6 — AS-IS-bug-carry-over consistency

For each BUG-NN in `as_is_bug_carry_over`:
- Is there at least one test that explicitly references the BUG-NN?
- Does the assertion document the inherited buggy expectation?

A carry-over bug not exercised by any test means we have no proof
the behaviour is preserved (which matters for users who rely on it):
→ CHL severity `medium`.

### Check 7 — PO sign-off completeness

In `01-equivalence-report.md`:
- Are sign-off slots present (engineering lead, PO, security review)?
- Are all `accepted-difference` items in the dedicated section?
- Are all `regression-accepted` items in the dedicated section?
- Are all `regression-blocking` items in the dedicated section?
- Are all 8 quality-gate items rendered with current state?

A report that ships to PO with missing sign-off slots:
→ CHL severity `high` (UX of approval breaks).

### Check 8 — Performance gate compliance

In `04-performance-comparison.md`:
- For every UC marked `regression-soft` (>+10%): is there a PO sign-off
  field?
- For every UC marked `regression-hard` (>+25%): is it in
  `01-equivalence-report.md` § Blocking regressions?
- Are env caveats documented (CPU, RAM, JVM version)?

A perf delta > +25% without explicit blocking-regression listing:
→ CHL severity `blocking`.

A perf delta > +10% without env caveats:
→ CHL severity `medium` (numbers might be unreliable).

### Check 9 — Shell coverage in E2E

Verify that the FE test suite includes an end-to-end smoke spec that
actually drives the application as a user — not just isolated component
tests. Read `<frontend-dir>/tests/e2e/smoke.spec.ts` (or equivalent).

Required properties of the smoke spec:

1. It iterates over **every protected route in `app.routes.ts`** (or has
   a hard-coded list that the challenger can diff against the routes
   file — any orphan route generates one CHL per orphan).
2. It asserts the page does NOT contain Angular CLI placeholder strings
   (`Hello, infosync-frontend`, `Congratulations! Your app is running`,
   `Explore the Docs`, `Learn with Tutorials`).
3. It asserts a feature `<h1>`/`<h2>` is visible on each route
   (proves the lazy chunk rendered, not just the shell).
4. It asserts a nav link to each route exists.
5. The spec is part of the CI default pipeline (referenced from
   `tobe-testing-supervisor`'s Final Validation gate).

Severity:
- smoke spec absent → `blocking` (CHL-SHELL-NOEXIST)
- smoke spec exists but covers < 80% of protected routes → `high`
  (CHL-SHELL-PARTIAL)
- spec does not check for placeholder strings → `high`
  (CHL-SHELL-NOPLACEHOLDER-GUARD)
- spec runs only on the static build (no real backend) → `medium`
  (CHL-SHELL-NOREALAPI)

> Rationale: the InfoSync 2026-05 retrospective had 200/200 component
> tests + 204/204 equivalence tests all passing while the FE was
> unusable because every route showed the Angular CLI welcome card.
> Component tests and HTTP equivalence tests both run *below* the level
> at which this gap lives.

---
