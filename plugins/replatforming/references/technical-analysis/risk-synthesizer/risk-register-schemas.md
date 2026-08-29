# Risk register schemas (MD / JSON / CSV)

> Reference doc for `risk-synthesizer`. Read at runtime when writing the
> consolidated risk register. Defines the three serialization shapes that
> downstream tools (Excel, Jira import, dashboards) rely on.

## Goal

Provide the canonical schemas for the three risk-register artifacts:

- `09-synthesis/risk-register.md` — human-readable, sortable table
- `_meta/risk-register.json` — machine-readable, schema-versioned
- `_meta/risk-register.csv` — flat, tool-importable

Keep the same item set across all three. Only the encoding differs.

---

## Stable finding-ID prefixes (per source agent)

When parsing Wave 1 outputs preserve the prefixes verbatim — never renumber.

| Prefix | Source agent |
|---|---|
| `RISK-CQ-NN` | code-quality-analyst |
| `ST-NN` | state-runtime-analyst |
| `VULN-NN` | dependency-security-analyst (vulnerabilities) |
| `DEP-NN` | dependency-security-analyst (deprecations) |
| `RISK-DA-NN` | data-access-analyst |
| `INT-NN`, `RISK-INT-NN` | integration-analyst |
| `PERF-NN` | performance-analyst |
| `RISK-RES-NN` | resilience-analyst |
| `SEC-NN` | security-analyst |

For each finding capture: ID, title, severity, source agent, source file,
location, AS-IS remediation hint, related finding IDs (when merged).

---

## Markdown — `09-synthesis/risk-register.md`

```markdown
---
agent: risk-synthesizer
generated: <ISO-8601>
sources:
  - docs/analysis/02-technical/01-code-quality/...
  - docs/analysis/02-technical/02-state-runtime/...
  - ... (list every Wave 1 file actually read)
  - docs/analysis/01-functional/...  (if available)
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# Risk register (consolidated)

## Summary
- Critical: <N>
- High:     <N>
- Medium:   <N>
- Low:      <N>
- Info:     <N>
- Total:    <N>

## Distribution by source agent

| Agent | Critical | High | Medium | Low | Info | Total |
|---|---|---|---|---|---|---|
| code-quality-analyst | ... |
| state-runtime-analyst | ... |
| dependency-security-analyst | ... |
| data-access-analyst | ... |
| integration-analyst | ... |
| performance-analyst | ... |
| resilience-analyst | ... |
| security-analyst | ... |

## Risk register (sortable)

| ID | Severity | Source | Title | Affected | Effort |
|---|---|---|---|---|---|
| SEC-01 | critical | security | Hard-coded API key | F-03 / UC-07 | small |
| SEC-02 | critical | security | SQL injection in reports | F-05 / UC-12 | medium |
| RISK-DA-02 | critical | data-access | Pickle deserialization | F-09 | medium |
| ... |

(Sorted by severity desc, then likelihood desc.)

## Cross-references

| Finding | Other findings (same root cause) |
|---|---|
| SEC-02 | RISK-DA-01 (same SQL injection seen by data-access) |

## Phase 1 traceability gaps
<list features / use cases that have no technical findings — could be
clean code OR could be uncovered scope>

## Open questions
- <e.g., "finding X reported by two agents with different severities;
  kept the higher one">
- <e.g., "Phase 1 unavailable; risk-to-feature traceability is empty">
```

---

## JSON — `_meta/risk-register.json`

```json
{
  "schema_version": "1.0",
  "generated": "<ISO-8601>",
  "agent": "risk-synthesizer",
  "items": [
    {
      "id": "SEC-01",
      "title": "Hard-coded API key",
      "severity": "critical",
      "source_agent": "security-analyst",
      "source_file": "08-security/security-findings.md",
      "owasp": "A02",
      "location": "<repo-path>:<line>",
      "likelihood": "certain",
      "impact": "major",
      "estimated_effort": "small",
      "remediation_hint": "...",
      "related_findings": ["VULN-NN"],
      "affected_features": ["F-03"],
      "affected_use_cases": ["UC-07"]
    }
  ]
}
```

---

## CSV — `_meta/risk-register.csv`

Stable column order (do not reorder — external tools rely on it):

```
id, severity, source_agent, title, owasp, location,
likelihood, impact, effort, affected_features, affected_use_cases,
remediation_hint
```
