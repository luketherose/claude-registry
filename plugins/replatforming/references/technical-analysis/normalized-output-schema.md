# Phase 2 — Normalized output schemas

> Reference doc for `technical-analysis-supervisor` and Phase 2 sub-agents. Read at runtime when writing JSONL artifacts to `docs/analysis/02-technical/normalized/` or `raw/`.

## Purpose

---

## `normalized/technical-findings.jsonl`

```
docs/analysis/02-technical/
  raw/
    code-quality-findings.jsonl
    performance-findings.jsonl
    resilience-findings.jsonl
    dependency-security-findings.jsonl
    integration-findings.jsonl
    data-access-findings.jsonl
    security-findings.jsonl
    state-runtime-findings.jsonl
  normalized/
    technical-findings.jsonl
    risk-register.jsonl
    risk-evidence-matrix.csv
    technical-gaps.jsonl
    technical-evidence-audit.json
  _meta/
    technical-evidence-report.md  (technical-evidence-auditor)
```

## `normalized/technical-findings.jsonl`

Merged by risk-synthesizer from all W1 raw JSONL. One record per finding.

`finding_id` convention: `TECH-<CATEGORY_ABBREV>-<NNN>` where category abbreviations are `PERF`, `SEC`, `RES`, `CQ`, `DA`, `INT`, `STATE`, `DEP`.

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

One JSON object per line aggregating one or more technical findings into a risk entry.

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
  "remediation_priority": "P1 | P2 | P3 | backlog",
  "status": "open | acknowledged | mitigated"
}
```

---

## `normalized/technical-gaps.jsonl`

One JSON object per line representing an unresolved gap in the technical analysis.

```json
{
  "gap_id": "TGAP-001",
  "category": "missing_evidence | unanalyzed_component | tool_failure | large_file_uncovered | unknown_integration",
  "description": "What is unknown or unverifiable",
  "affected_area": "performance | security | resilience | code-quality | data-access | integration | state | dependency",
  "affected_components": ["path/to/file.py"],
  "blocking": true,
  "open_question": "Specific question to resolve this gap",
  "source_agent": "security-analyst",
  "auto_resolvable": false
}
```

---

## `raw/` files

One JSONL per W1 sub-agent (pre-normalization):

- `raw/code-quality-findings.jsonl`
- `raw/state-runtime-findings.jsonl`
- `raw/dependency-security-findings.jsonl`
- `raw/data-access-findings.jsonl`
- `raw/integration-findings.jsonl`
- `raw/performance-findings.jsonl`
- `raw/resilience-findings.jsonl`
- `raw/security-findings.jsonl`

Each raw file uses the same schema as `technical-findings.jsonl` but with `status: candidate` (not yet merged/confirmed by risk-synthesizer).

---

## `normalized/risk-evidence-matrix.csv`

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

---

## `normalized/technical-evidence-audit.json`

---

## `normalized/risk-evidence-matrix.csv`

Columns: `risk_id, title, severity, finding_count, evidence_count, has_verified_evidence (true/false)`

One row per risk. Produced by technical-evidence-auditor.

---

## `normalized/technical-evidence-audit.json`

Schema (produced by `technical-evidence-auditor`):

```json
{
  "audit_id": "TEA-001",
  "run_at": "ISO-8601",
  "agent": "technical-evidence-auditor",
  "verdict": "PASS | PASS_WITH_GAPS | FAIL",
  "evidence_checks": {
    "findings_with_evidence": {"total": 0, "with_evidence": 0, "missing": []},
    "high_critical_verified": {"total": 0, "verified": 0, "unverified": []},
    "security_with_tool_evidence": {"total": 0, "with_tool": 0, "missing_tool": []}
  },
  "as_is_purity_violations": [],
  "findings": []
}
```

---

---

```markdown
# Analysis Quality Summary — Phase 2

Generated: <ISO-8601>
Verdict: PASS | PASS_WITH_GAPS | FAIL

| Metric | Description |
|---|---|
| `claims_with_evidence_pct` | % of findings that cite at least one evidence_id |
| `high_critical_with_evidence_pct` | % of high/critical findings with `validation.status: verified` |
| `confirmed_findings_count` | Count of findings with `status: confirmed` |
| `candidate_findings_count` | Count of findings with `status: candidate` |
| `open_gaps` | Count of entries in `technical-gaps.jsonl` with `blocking: true` |
| `validator_verdict` | Output of `validate_technical_analysis.py` (PASS / PASS_WITH_GAPS / FAIL) |
| `auditor_verdict` | `technical-evidence-audit.json` verdict field |

---

## Rules

- No finding without an `evidence_id`. Findings with `severity: high` or `severity: critical` must additionally have `validation.status: verified`.
- Security findings must cite scanner or lockfile evidence (e.g., `pip-audit` output, `requirements.txt` with CVE reference). No CVE claim is valid without tool evidence.
- No TO-BE recommendations in `statement`. Forbidden terms: `Spring Boot`, `Angular`, `migrate to`, `replatform`, `target architecture`, `TO-BE`.
- `requires_validation` status is valid only when the gap is recorded in `technical-gaps.jsonl` with `blocking: true`.
