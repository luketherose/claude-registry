# Phase 2 — Normalized output schemas

> Reference doc for `technical-analysis-supervisor` and Phase 2 sub-agents. Read at runtime when writing JSONL artifacts to `docs/analysis/02-technical/normalized/` or `raw/`.

---

## `normalized/technical-findings.jsonl`

Merged by risk-synthesizer from all W1 raw JSONL. One record per finding.

```json
{
  "finding_id": "TECH-PERF-001",
  "category": "performance | security | resilience | code-quality | data-access | integration | state | dependency",
  "severity": "critical | high | medium | low",
  "confidence": "high | medium | low",
  "statement": "Description of observed problem (AS-IS only — no TO-BE prescriptions)",
  "evidence_ids": ["EV-000123"],
  "context_bundle_ids": [],
  "affected_components": ["module/path.py"],
  "affected_use_cases": ["UC-004"],
  "validation": {
    "type": "static_code_review | tool_output | runtime_observation | benchmark",
    "status": "verified | not_verified | requires_validation"
  },
  "status": "confirmed | candidate | requires_validation | rejected",
  "recommended_remediation_phase": "Phase 4 hardening | backlog | before migration | human decision",
  "source_agent": "performance-analyst"
}
```

**Rules:**
- `severity: high` or `critical`: `evidence_ids` MUST be non-empty; `validation.status` MUST be `verified` or `requires_validation`.
- `statement` must be AS-IS — no "should", "must", "migrate to", "replace with".
- Risk-synthesizer CANNOT introduce findings; it merges from W1 JSONL only.

---

## `normalized/risk-register.jsonl`

One record per risk (derived from findings).

```json
{
  "risk_id": "RISK-001",
  "title": "Risk title",
  "category": "security | performance | resilience | code-quality | dependency | integration",
  "severity": "critical | high | medium | low",
  "likelihood": "high | medium | low",
  "impact": "high | medium | low",
  "related_finding_ids": ["TECH-SEC-001"],
  "affected_components": ["module/path.py"],
  "affected_use_cases": ["UC-004"],
  "evidence_ids": ["EV-000123"],
  "remediation_priority": 1,
  "status": "open | acknowledged | mitigated"
}
```

---

## `normalized/technical-gaps.jsonl`

One record per gap.

```json
{
  "gap_id": "TGAP-001",
  "category": "missing_evidence | unanalyzed_component | tool_failure | large_file_uncovered | unknown_integration",
  "blocking": true,
  "description": "What is unknown",
  "affected_components": ["path/to/file.py"],
  "source_agent": "security-analyst",
  "auto_resolvable": false
}
```

---

## `raw/` files

One JSONL per W1 sub-agent:

- `raw/code-quality-findings.jsonl`
- `raw/state-runtime-findings.jsonl`
- `raw/dependency-security-findings.jsonl`
- `raw/data-access-findings.jsonl`
- `raw/integration-findings.jsonl`
- `raw/performance-findings.jsonl`
- `raw/resilience-findings.jsonl`
- `raw/security-findings.jsonl`

Each raw file uses the same schema as `technical-findings.jsonl` but with `status: candidate` (not yet merged/confirmed by synthesizer).

---

## `normalized/risk-evidence-matrix.csv`

Columns: `risk_id, title, severity, finding_count, evidence_count, has_verified_evidence (true/false)`

One row per risk. Produced by technical-evidence-auditor.

---

## `normalized/technical-evidence-audit.json`

Schema (produced by `technical-evidence-auditor`):

```json
{
  "run_id": "<ISO-8601>",
  "agent": "technical-evidence-auditor",
  "verdict": "PASS | PASS_WITH_GAPS | FAIL",
  "evidence_completeness": {
    "findings_with_evidence": 0,
    "findings_without_evidence": 0,
    "high_critical_verified": 0,
    "high_critical_unverified": 0
  },
  "purity_violations": [],
  "findings": []
}
```

---

## `final/analysis-quality-summary.md` template

Goes in `final/` after the auditor completes.

```markdown
# Analysis Quality Summary — Phase 2

Generated: <ISO-8601>
Verdict: PASS | PASS_WITH_GAPS | FAIL

## Coverage
- Total findings confirmed: X (N critical, M high, P medium, Q low)
- Findings with evidence: X / total
- High/critical findings verified: X / total high/critical
- Technical gaps: X (N blocking)

## Confidence distribution
- High confidence: X%
- Medium confidence: X%
- Low/speculative: X%

## AS-IS purity
- Violations: 0

## Unresolved gaps
[List from technical-gaps.jsonl where blocking=true]
```
