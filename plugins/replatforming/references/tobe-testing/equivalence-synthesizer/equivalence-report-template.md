# `01-equivalence-report.md` — template

> Reference doc for `equivalence-synthesizer`. Read at runtime when assembling
> the deliverable equivalence report (W4 of Phase 5).

## Goal

Define the exact structure of `01-equivalence-report.md`, the deliverable that
the Product Owner signs off and that gates go-live. Includes the verdict
classification rules used to derive a per-UC verdict from test outcomes.

## Required sections

```markdown
---
<frontmatter>
---

# TO-BE equivalence report — Phase 5

## Executive summary

(3-5 lines)
- Total UCs: <N>
- Equivalent: <N>
- Accepted-differences: <N> (require PO sign-off)
- Regressions (blocking): <N>
- Regressions (accepted): <N> (require PO sign-off)
- Not tested: <N> (with documented reason each)

## Verdict per UC

| UC ID | UC title | Priority | Verdict | Test reference | Notes |
|---|---|---|---|---|---|
| UC-001 | <title> | critical | equivalent | tests/equivalence/test_uc_001_*.py | — |
| UC-002 | <title> | high     | accepted-difference | tests/equivalence/test_uc_002_*.py | TZ format change — see Accepted differences |
| UC-003 | <title> | medium   | regression-accepted | tests/equivalence/test_uc_003_*.py | TBUG-7 — PO accepted xfail until Phase 4 hardening loop |
| UC-004 | <title> | critical | regression-blocking | tests/equivalence/test_uc_004_*.py | TBUG-12 — see Blocking regressions |
| UC-005 | <title> | low      | not-tested | — | Streamlit-only diagnostic page; no Angular equivalent |

(One row per UC from Phase 1. Every UC must appear. If a UC has
no row, this report is incomplete.)

## Contract tests verdict (vs OpenAPI)

| OperationId | Verdict | Notes |
|---|---|---|
| createCustomer | pass | — |
| updateCustomer | drift | response missing `updatedAt` field |

(One row per operationId in OpenAPI. Drifts are blocking.)

## Performance verdict

| UC / endpoint | AS-IS p95 | TO-BE p95 | Delta | Verdict |
|---|---|---|---|---|
| UC-001 | 120 ms | 134 ms | +11.7% | regression-soft (>10%) |

p95 regressions > +25%: blocking unless PO accepts.
p95 regressions > +10%: PO sign-off required (regression-soft / -accepted).

## Security verdict

- OWASP Top 10 coverage: 10/10
- Phase 2 regression matrix: <N> AS-IS findings, <N> mitigated, <N>
  not-applicable, <N> regressed
- Open critical security findings: <N>  (must be 0 for go-live)
- Open high security findings: <N>  (must be 0 or PO-accepted)

## Accepted differences (require PO sign-off)

For each:

### AD-NN — <title>
- **Affected UC**: UC-<id>
- **AS-IS behaviour**: <description>
- **TO-BE behaviour**: <description>
- **Reason for difference**: <design choice / framework constraint / explicit improvement>
- **Impact**: <user-facing | internal-only>
- **PO sign-off**: pending | yes (<date>, <name>)

## Blocking regressions (must be resolved before go-live)

For each:

### REG-NN — <title>
- **Severity**: critical | high
- **Affected UC**: UC-<id>
- **Test that detected it**: <path:line>
- **Symptom**: <description>
- **Recommended fix path**: Phase 4 hardening loop on BC <bc>
- **Status**: open | in-progress (Phase 4 loop) | fixed (re-test pending)

## Coverage and quality summary

(Aggregated from 02-coverage-report.md)
- Backend line coverage: <%> (target ≥ 80%)
- Backend branch coverage: <%> (target ≥ 70%)
- Frontend line coverage: <%>
- E2E specs vs user flows: <count>/<total>
- Backend test classes: <count>
- Frontend spec files: <count>

## Quality gate (Phase 5 → go-live)

- [ ] All critical regressions resolved
- [ ] All blocking contract drifts resolved
- [ ] All p95 > +25% regressions resolved or PO-accepted
- [ ] All open critical security findings resolved
- [ ] Backend line coverage ≥ 80%
- [ ] Backend branch coverage ≥ 70%
- [ ] PO sign-off on this report
- [ ] All accepted-differences signed off

(Each item rendered with current state; tick what's already met.)

## Sign-off

- **Engineering lead**: ________________  date: ________
- **Product Owner**:    ________________  date: ________
- **Security review**:  ________________  date: ________
```

## Verdict classification rules

For each UC, derive its verdict from the test results:

| Test outcome | Conditions | Verdict |
|---|---|---|
| All assertions pass | No accepted_diffs declared | `equivalent` |
| All assertions pass | Accepted_diffs present, PO sign-off pending | `accepted-difference` |
| Some assertions fail | Severity = critical OR high | `regression-blocking` |
| Some assertions fail | Severity = medium OR low, in TBUG registry, marked `xfail` | `regression-accepted` (assuming PO will sign) |
| Test module is `pytest.skip` | With documented reason | `not-tested-with-reason` |

Severity is inherited from the UC's Phase 1 priority unless type-specific
overrides apply (contract drift = critical, security regression = critical
or high based on CVSS).
