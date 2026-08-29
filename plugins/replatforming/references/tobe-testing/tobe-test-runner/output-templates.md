# Output templates

> Reference doc for `tobe-test-runner`. Read at runtime when writing
> the consolidated coverage, contract-test, and bug-registry reports.

## Frontmatter (every markdown report)

```yaml
---
phase: 5
sub_step: 5.6
agent: tobe-test-runner
generated: <ISO-8601>
sources:
  - <test-paths actually executed>
  - <coverage tool outputs>
related_ucs: [<UC-NN>, ...]
confidence: high | medium | low
status: complete | partial | needs-review | blocked
---
```

## `02-coverage-report.md`

```markdown
---
<frontmatter>
---

# TO-BE coverage report

## Backend (JaCoCo)
| BC | Line % | Branch % | Threshold met? |
|---|---|---|---|
| <bc-1> | 84% | 72% | yes |
| <bc-2> | 78% | 65% | NO — see exclusions |

Targets: line ≥ 80%, branch ≥ 70%.

## Frontend (Jest)
| Module | Line % | Function % |
|---|---|---|
| ... | ... | ... |

## Equivalence (pytest)
| UC ID | UC priority | Equivalent | Regression | Skipped |
|---|---|---|---|---|
| UC-001 | critical | yes | — | — |
| UC-002 | high | partial | TBUG-3 | — |

## Excluded code
<list of generated code, presentation-only components, etc.>
```

## `03-contract-tests-report.md`

```markdown
---
<frontmatter>
---

# TO-BE contract tests report (vs OpenAPI)

## Coverage
| OpenAPI operationId | SCC contract present | Verdict | Notes |
|---|---|---|---|
| createCustomer | yes | pass | — |
| updateCustomer | yes | FAIL | response body missing `updatedAt` field |
| deleteCustomer | NO | n/a | contract not authored — escalate |

## Contract drift
<critical drifts listed; each is a blocker>
```

## `06-tobe-bug-registry.md`

```markdown
---
<frontmatter>
---

# TO-BE bug registry (medium / low non-blocking)

> Critical and high regressions are NOT in this registry — they are
> in `01-equivalence-report.md` as blocking.

## TBUG-001 — <title>
- **Severity**: medium
- **Affected UC**: UC-007
- **Test**: backend/src/test/.../FooServiceTest.java#test_normalises_address
- **Symptom**: TO-BE returns "Via Roma 12" where AS-IS returned
  "via roma 12" (case difference)
- **Disposition**: xfail; recommend address normalisation alignment in
  Phase 4 hardening loop
- **AS-IS source ref**: original/InfoSync/services/customer.py:42
```

## Final report (printed to supervisor)

```
TO-BE test runner complete.
Execute policy:           on | backend-only | frontend-only | off

Suites executed:
  - Backend (mvn verify):     <pass>/<total> tests; coverage line=<%>, branch=<%>
  - Frontend (jest):          <pass>/<total> tests; coverage line=<%>, function=<%>
  - E2E (playwright):         <pass>/<total> specs
  - Equivalence (pytest):     <pass>/<total> tests
  - Performance (k6/gatling): <count> scenarios; p95 regressions: <count>

Contract tests vs OpenAPI: <pass>/<total>; drifts: <count>

Failure classification:
  - critical:  <count>  ← blocking (escalated)
  - high:      <count>  ← blocking unless PO accepts
  - medium:    <count>  ← TBUG registry, xfail
  - low:       <count>  ← TBUG registry, skip

Files modified (markers only):
  - backend: <count>
  - frontend: <count>
  - equivalence: <count>

Open questions: <count>
Confidence:    high | medium | low
Status:        complete | partial | needs-review | blocked
```
