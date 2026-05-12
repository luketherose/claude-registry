# Phase 1 — Normalized Output Schema (JSONL Artifacts)

> Reference doc for `functional-analysis-supervisor` and Phase 1 sub-agents. Read at runtime when writing JSONL artifacts to `docs/analysis/01-functional/normalized/` or `raw/`.

## Purpose

Alongside the existing numbered markdown files, Phase 1 now produces structured JSONL artifacts in `docs/analysis/01-functional/normalized/` that are machine-readable, citeable, and validated by `validate_functional_analysis.py`. These artifacts are the authoritative source for downstream phases: Phase 3 (baseline testing) consumes `use-case-candidates.jsonl` to derive test targets; Phase 4 (refactoring) consumes `feature-candidates.jsonl` and `business-rules.jsonl`. Final markdown reports must be generated FROM normalized JSONL, not independently.

## Directory layout

```
docs/analysis/01-functional/
  raw/
    actor-feature-findings.jsonl     (actor-feature-mapper raw output)
    ui-surface-findings.jsonl        (ui-surface-analyst raw output)
    io-catalog-findings.jsonl        (io-catalog-analyst raw output)
    implicit-logic-findings.jsonl    (implicit-logic-analyst raw output)
    user-flow-findings.jsonl         (user-flow-analyst raw output)
  normalized/
    feature-candidates.jsonl
    use-case-candidates.jsonl
    actor-candidates.jsonl
    business-rules.jsonl
    uc-evidence-matrix.csv
    functional-gaps.jsonl
    functional-traceability-audit.json
  _meta/
    functional-traceability-report.md  (functional-traceability-auditor)
```

## `normalized/use-case-candidates.jsonl`

One JSON object per line. Each object represents a single use case candidate.

```json
{
  "uc_id": "UC-001",
  "title": "Use case title",
  "status": "confirmed | candidate_not_confirmed | requires_human_confirmation",
  "actors": ["Actor Name"],
  "trigger": "What initiates this use case",
  "main_flow": ["Step 1", "Step 2"],
  "alternative_flows": [{"condition": "...", "steps": ["..."]}],
  "business_rules": ["BR-001"],
  "evidence_ids": ["EV-000001"],
  "context_bundle_ids": [],
  "source_confidence": "high | medium | low",
  "inference_level": "direct | derived | speculative",
  "unknowns": ["Open question text"],
  "source_agent": "user-flow-analyst"
}
```

**Status rules:**
- `status: confirmed` requires at least one `evidence_id`.
- `candidate_not_confirmed` — identified but insufficient evidence; must include at least one `unknown`.
- `requires_human_confirmation` — conflicting signals; present to user in HITL. Blocks further pipeline progress until resolved.

Only `confirmed` UCs can be consumed by Phase 3 as test targets; `candidate_not_confirmed` must not be treated as requirements by Phase 4.

---

## `normalized/feature-candidates.jsonl`

One JSON object per line. Each object represents a single feature candidate.

```json
{
  "feature_id": "F-001",
  "title": "Feature title",
  "description": "What the feature does",
  "actors": ["Actor Name"],
  "related_uc_ids": ["UC-001"],
  "evidence_ids": ["EV-000001"],
  "status": "confirmed | candidate | deprecated",
  "confidence": "high | medium | low",
  "inference_level": "direct | derived | speculative",
  "source_agent": "actor-feature-mapper"
}
```

---

## `normalized/actor-candidates.jsonl`

One JSON object per line. Each object represents a single actor candidate.

```json
{
  "actor_id": "A-001",
  "name": "Actor name",
  "type": "human | system | external",
  "description": "Role description",
  "evidence_ids": ["EV-000001"],
  "related_feature_ids": ["F-001"],
  "status": "confirmed | inferred | requires_human_confirmation",
  "confidence": "high | medium | low",
  "source_agent": "actor-feature-mapper"
}
```

---

## `normalized/business-rules.jsonl`

One JSON object per line. Each object represents a single business rule extracted from the AS-IS system.

```json
{
  "rule_id": "BR-001",
  "title": "Rule title",
  "statement": "The rule as a declarative statement",
  "domain": "pricing | access_control | validation | workflow | data_integrity",
  "evidence_ids": ["EV-000001"],
  "enforced_in": ["file/path.py:line"],
  "related_uc_ids": ["UC-001"],
  "confidence": "high | medium | low",
  "inference_level": "direct | derived | speculative",
  "source_agent": "actor-feature-mapper | implicit-logic-analyst"
}
```

---

## `normalized/functional-gaps.jsonl`

One JSON object per line. Each object represents an unresolved gap or open question.

```json
{
  "gap_id": "FGAP-001",
  "category": "missing_evidence | unmapped_ui | orphan_io | unresolved_rule | unknown_actor | large_file_uncovered",
  "description": "What is unknown or uncovered",
  "affected_area": "uc | actor | feature | business_rule | io | ui",
  "affected_items": ["UC-001", "F-002"],
  "blocking": true,
  "open_question": "Specific question to resolve this gap",
  "source_agent": "user-flow-analyst",
  "auto_resolvable": false
}
```

---

## `raw/` files

One JSONL per sub-agent (pre-normalization):

- `raw/actor-feature-findings.jsonl` — actor-feature-mapper raw output
- `raw/ui-surface-findings.jsonl` — ui-surface-analyst raw output
- `raw/io-catalog-findings.jsonl` — io-catalog-analyst raw output
- `raw/user-flow-findings.jsonl` — user-flow-analyst raw output
- `raw/implicit-logic-findings.jsonl` — implicit-logic-analyst raw output

Each raw file: one record per finding, same fields as the normalized equivalent plus a `raw_text` field for the agent's original description.

---

## `normalized/uc-evidence-matrix.csv`

CSV with the following columns:

```
uc_id,title,status,evidence_count,evidence_ids,confidence
```

One row per use case. `evidence_ids` is a semicolon-separated list within the CSV cell.

---

## `normalized/functional-traceability-audit.json`

Single JSON object (not JSONL) representing the output of the functional-traceability-auditor.

```json
{
  "audit_id": "FTA-001",
  "run_at": "ISO-8601",
  "agent": "functional-traceability-auditor",
  "verdict": "PASS | PASS_WITH_GAPS | FAIL",
  "traceability_checks": {
    "uc_with_evidence": {"total": 0, "confirmed_with_evidence": 0, "missing_evidence": []},
    "ui_surfaces_mapped": {"total": 0, "mapped": 0, "intentionally_unmapped": 0, "unmapped": []},
    "io_linked_to_uc": {"total": 0, "linked": 0, "unlinked": []},
    "business_rules_with_evidence": {"total": 0, "with_evidence": 0, "missing_evidence": []}
  },
  "negative_space_findings": [],
  "as_is_purity_violations": [],
  "findings": []
}
```

`negative_space_findings`: areas of the UI or codebase with no corresponding UC — potential missing coverage. `as_is_purity_violations`: uses of TO-BE terminology detected in AS-IS artifacts.

---

## Analysis quality summary

Phase 1 must produce a `docs/analysis/01-functional/final/analysis-quality-summary.md` file after the auditor completes. Required metrics:

| Metric | Description |
|---|---|
| `claims_with_evidence_pct` | % of UC/feature/actor claims that cite at least one evidence_id |
| `claims_inferred_pct` | % of claims with `inference_level: derived` |
| `speculative_claims_count` | Count of claims with `inference_level: speculative` |
| `uc_confirmed_count` | Count of UCs with `status: confirmed` |
| `uc_candidate_count` | Count of UCs with `status: candidate_not_confirmed` |
| `ui_surfaces_mapped_pct` | % of identified UI surfaces linked to at least one UC |
| `io_boundaries_mapped_pct` | % of identified IO boundaries linked to at least one UC |
| `open_gaps_count` | Count of entries in `functional-gaps.jsonl` with `blocking: true` |
| `as_is_violations` | Count of AS-IS purity violations from the audit |
| `validator_verdict` | Output of `validate_functional_analysis.py` (PASS / PASS_WITH_GAPS / FAIL) |
| `auditor_verdict` | `functional-traceability-audit.json` verdict field |

---

## Confidence + inference levels (applies to all JSONL)

| Level | Inference | Meaning |
|---|---|---|
| `high` | `direct` | Code evidence directly proves the claim |
| `medium` | `derived` | Inferred from multiple indirect signals |
| `low` | `speculative` | Plausible but unverified |

Missing evidence → use `functional-gaps.jsonl`, not a speculative claim.

---

## Rules

- Confirmed UCs must have at least one `evidence_ids` entry. A `confirmed` UC with an empty `evidence_ids` array is a validation error.
- No TO-BE terminology is permitted in any AS-IS artifact. Forbidden terms: `Spring Boot`, `Angular`, `migrate to`, `replatform`, `target architecture`, `TO-BE`.
- Final markdown reports (numbered files 01–14) must be generated FROM normalized JSONL, not independently. If a claim appears in a markdown report but not in the JSONL, it is treated as undocumented and does not count toward evidence coverage.
- `speculative` inference level requires a corresponding entry in `functional-gaps.jsonl` explaining what evidence is missing.
