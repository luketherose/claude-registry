# Execution stages

> Reference doc for `tobe-test-runner`. Read at runtime when about to
> execute the TO-BE test suites and when classifying failures.

Run the suites in this order (each gated on the previous succeeding or
the failure being non-blocking).

## 1. Backend unit + integration + contract tests

```bash
cd backend
./mvnw -B clean verify \
    -Dspring.profiles.active=test \
    -DfailIfNoTests=false \
    -Dgroups=" "
```

This single command runs:
- JUnit unit tests
- Slice tests (`@WebMvcTest`, `@DataJpaTest`)
- Integration tests with Testcontainers
- Spring Cloud Contract `verify` goal — produces JUnit reports for
  each contract

Capture:
- `backend/target/surefire-reports/*.xml` — unit results
- `backend/target/failsafe-reports/*.xml` — integration results
- `backend/target/site/jacoco/jacoco.xml` — coverage
- `backend/target/generated-test-sources/contracts/` — SCC contracts
  exercised

## 2. Frontend component tests

```bash
cd frontend
npm ci --prefer-offline --no-audit
npx jest --ci --coverage --reporters=default --reporters=jest-junit
```

Capture:
- `frontend/coverage/lcov.info`
- `frontend/coverage/coverage-summary.json`
- `frontend/junit.xml`

## 3. E2E tests (Playwright)

```bash
cd "${repo_root}"
npx playwright install --with-deps chromium
npx playwright test --reporter=list,junit
```

Capture:
- `playwright-report/`
- `test-results/` (traces, screenshots on failure)

## 4. Equivalence harness

```bash
cd "${repo_root}"
python -m venv .venv-tobe-tests
source .venv-tobe-tests/bin/activate
pip install -q pytest pytest-regressions httpx pytest-playwright
pytest tests/equivalence -v --junitxml=tests/equivalence/junit.xml
```

Capture:
- `tests/equivalence/junit.xml`
- updated snapshots (if any) — flag, don't auto-accept

## 5. Performance scenarios

```bash
cd e2e/perf
# k6 path
k6 run --summary-export=results-summary.json scenarios/<uc>.js
# Gatling path
./mvnw -pl ../perf gatling:test
```

Aggregated into `_meta/benchmark-comparison.json` (already populated
by `performance-comparator`; you only execute and update with real
numbers).

---

## Failure handling per suite

After each suite runs, parse the result:

```python
# Pseudocode
for failed_test in suite_results.failures:
    severity = classify(failed_test)
    if severity in ("critical", "high"):
        record_in_bug_registry(failed_test, severity)
        # do NOT mark xfail — test stays failing, supervisor escalates
    elif severity in ("medium", "low"):
        record_in_bug_registry(failed_test, severity)
        add_xfail_marker(failed_test, reason=f"TBUG-{nn}: {short_description}")
    else:
        # 'as-is-bug-carry-over' should have been pre-marked by Wave 1
        # If we see it here, it's a Wave 1 defect — escalate
        escalate(failed_test, reason="unexpected as-is-bug failure")
```

### Severity classification

Read the failed test's frontmatter or surrounding context to find:
- `related_ucs` — which UC does it cover?
- The UC's `priority` from Phase 1 → maps to severity:
  - `critical` UC → `critical` regression
  - `high` UC → `high` regression
  - `medium` UC → `medium` regression
  - `low`/unmarked → `low` regression
- Type-specific overrides:
  - Contract test failure (vs OpenAPI) → always `critical` (contract
    drift)
  - Security test failure (auth/authz) → `critical`
  - Security test failure (header missing, low-CVSS finding) →
    `medium` or `high` based on CVSS
  - Performance scenario p95 > +25% baseline → `critical`
  - Performance scenario p95 > +10% baseline → `high`

### Adding markers (the only place you edit test files)

Backend (Java):
```java
// Original:
@Test
void test_something() { ... }

// After classification (only if medium/low):
@Test
@Disabled("TBUG-12: snapshot diff in Customer.address.normalisation; see 06-tobe-bug-registry.md")
void test_something() { ... }
```

Frontend (Jest):
```typescript
test.skip('renders the empty state', () => { /* TBUG-12 */ });
```

Equivalence (pytest):
```python
@pytest.mark.xfail(strict=True, reason="TBUG-12: see 06-tobe-bug-registry.md")
def test_uc_12_happy_path(): ...
```

For each marker added, add an entry to `06-tobe-bug-registry.md`.
