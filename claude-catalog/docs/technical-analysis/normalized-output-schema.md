# Phase 2 — Normalized Output Schema (JSONL Artifacts)

## Purpose

Alongside the existing numbered markdown files, Phase 2 now produces structured JSONL artifacts in `docs/analysis/02-technical/normalized/` that are machine-readable, citeable, and validated by `validate_technical_analysis.py`. These artifacts are the authoritative source for downstream phases: Phase 4 (refactoring) consumes `technical-findings.jsonl` and `risk-register.jsonl` to drive remediation prioritisation. Final markdown reports must be generated FROM normalized JSONL, not independently.

## Directory layout

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

## technical-findings.jsonl schema

One JSON object per line. Each object represents a single technical finding in the AS-IS system.

```json
{
  "finding_id": "TECH-PERF-001",
  "category": "performance | security | resilience | code-quality | data-access | integration | state | dependency",
  "severity": "critical | high | medium | low",
  "confidence": "high | medium | low",
  "statement": "Description of observed problem (AS-IS only, no TO-BE recommendations)",
  "evidence_ids": ["EV-000123"],
  "context_bundle_ids": [],
  "affected_components": ["module/path"],
  "affected_use_cases": ["UC-004"],
  "validation": {
    "type": "static_code_review | tool_output | runtime_observation | benchmark",
    "status": "verified | not_verified | requires_validation"
  },
  "status": "confirmed | candidate | requires_validation | rejected",
  "recommended_remediation_phase": "Phase 4 hardening | backlog | before migration | human decision"
}
```

`finding_id` convention: `TECH-<CATEGORY_ABBREV>-<NNN>` where category abbreviations are `PERF`, `SEC`, `RES`, `CQ`, `DA`, `INT`, `STATE`, `DEP`.

## risk-register.jsonl schema

One JSON object per line. Each object aggregates one or more technical findings into a risk entry.

```json
{
  "risk_id": "RISK-001",
  "title": "Risk title",
  "severity": "critical | high | medium | low",
  "category": "security | performance | resilience | maintainability | compliance",
  "finding_ids": ["TECH-PERF-001"],
  "evidence_ids": ["EV-000123"],
  "affected_use_cases": ["UC-001"],
  "affected_components": ["module/path"],
  "likelihood": "high | medium | low",
  "impact": "high | medium | low",
  "remediation_priority": "P1 | P2 | P3 | backlog"
}
```

## technical-gaps.jsonl schema

Same structure as `functional-gaps.jsonl`. One JSON object per line representing an unresolved gap in the technical analysis.

```json
{
  "gap_id": "TGAP-001",
  "description": "What is unknown or unverifiable",
  "affected_area": "performance | security | resilience | code-quality | data-access | integration | state | dependency",
  "blocking": true,
  "open_question": "Specific question to resolve this gap"
}
```

## risk-evidence-matrix.csv format

CSV with the following columns:

```
risk_id,title,severity,evidence_count,evidence_ids,affected_uc_ids
```

One row per risk. `evidence_ids` and `affected_uc_ids` are semicolon-separated lists within their CSV cells.

## technical-evidence-audit.json schema

Single JSON object (not JSONL) representing the output of the technical-evidence-auditor.

```json
{
  "audit_id": "TEA-001",
  "run_at": "ISO-8601",
  "evidence_checks": {
    "findings_with_evidence": {"total": 0, "with_evidence": 0, "missing": []},
    "high_critical_verified": {"total": 0, "verified": 0, "unverified": []},
    "security_with_tool_evidence": {"total": 0, "with_tool": 0, "missing_tool": []}
  },
  "as_is_purity_violations": [],
  "verdict": "PASS | PASS_WITH_GAPS | FAIL"
}
```

`as_is_purity_violations`: uses of TO-BE terminology detected in AS-IS finding statements.

## Rules

- No finding without an `evidence_id`. Findings with `severity: high` or `severity: critical` must additionally have `validation.status: verified`.
- Security findings must cite scanner or lockfile evidence (e.g., `pip-audit` output, `requirements.txt` with CVE reference). No CVE claim is valid without tool evidence.
- No TO-BE recommendations in `statement`. Forbidden terms: `Spring Boot`, `Angular`, `migrate to`, `replatform`, `target architecture`, `TO-BE`.
- `requires_validation` status is valid only when the gap is recorded in `technical-gaps.jsonl` with `blocking: true`.

## Analysis quality summary

Phase 2 must produce a `docs/analysis/02-technical/final/analysis-quality-summary.md` file after the auditor completes. Required metrics:

| Metric | Description |
|---|---|
| `claims_with_evidence_pct` | % of findings that cite at least one evidence_id |
| `high_critical_with_evidence_pct` | % of high/critical findings with `validation.status: verified` |
| `confirmed_findings_count` | Count of findings with `status: confirmed` |
| `candidate_findings_count` | Count of findings with `status: candidate` |
| `open_gaps` | Count of entries in `technical-gaps.jsonl` with `blocking: true` |
| `validator_verdict` | Output of `validate_technical_analysis.py` (PASS / PASS_WITH_GAPS / FAIL) |
| `auditor_verdict` | `technical-evidence-audit.json` verdict field |
