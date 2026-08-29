# `05-security-findings.md` — output document template

> Reference doc for `security-test-writer`. Read at runtime when
> authoring the consolidated security output document.

## Frontmatter

```yaml
---
phase: 5
sub_step: 5.5
agent: security-test-writer
generated: <ISO-8601>
sources:
  - docs/analysis/02-technical/08-security/
  - docs/refactoring/4.7-hardening/
  - docs/refactoring/api/openapi.yaml
  - backend/src/main/java/.../security/
related_ucs: [<UC-NN>, ...]
confidence: high | medium | low
status: complete | partial | needs-review | blocked
---
```

## Body

```markdown
# Security findings — TO-BE Phase 5

## Summary
- OWASP Top 10 coverage: 10/10
- Phase 2 regressions tested: <N> / <total>
- Open findings: critical=<N>, high=<N>, medium=<N>, low=<N>

## OWASP Top 10 coverage
| Category | Test class | Status |
|---|---|---|
| A01 Broken Access Control | A01_BrokenAccessControlTest | complete |
| ... | ... | ... |

## Phase 2 regression matrix
| AS-IS finding | Status in TO-BE | Test reference |
|---|---|---|
| SEC-001 | mitigated | A03_InjectionTest#test_payloadX |
| SEC-002 | not-applicable | n/a (Streamlit-only) |
| ... | ... | ... |

## Open findings
### SEC-NN: <title>
<as per item-frontmatter shape from supervisor spec>

## ZAP baseline (optional)
<Run instructions; latest scan summary if executed>

## Open questions
<list>
```

## Final terminal output (printed by the agent on completion)

```
Security tests authored.
OWASP categories covered:    10 / 10 (any non-applicable explicitly documented)
Phase 2 regressions tested:  <N> / <total>
Authentication tests:        <count>
Authorisation matrix size:   <roles × endpoints>
ZAP scan:                    configured | not-configured
Open findings (critical):    <count>
Open findings (high):        <count>
Open questions:              <count>
Confidence:                  high | medium | low
Status:                      complete | partial | needs-review | blocked
```
