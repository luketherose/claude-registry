# Phase 1 — Normalized output schemas

> Reference doc for `functional-analysis-supervisor` and Phase 1 sub-agents. Read at runtime when writing JSONL artifacts to `docs/analysis/01-functional/normalized/` or `raw/`.

---

## `normalized/use-case-candidates.jsonl`

One record per use case.

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
- `requires_human_confirmation` — conflicting signals; present to user in HITL.

---

## `normalized/feature-candidates.jsonl`

One record per feature.

```json
{
  "feature_id": "F-001",
  "title": "Feature title",
  "actors": ["Actor Name"],
  "description": "What the feature does",
  "evidence_ids": ["EV-000001"],
  "related_uc_ids": ["UC-001"],
  "confidence": "high | medium | low",
  "inference_level": "direct | derived | speculative",
  "source_agent": "actor-feature-mapper"
}
```

---

## `normalized/actor-candidates.jsonl`

One record per actor.

```json
{
  "actor_id": "A-001",
  "title": "Actor name",
  "description": "Role description",
  "evidence_ids": ["EV-000001"],
  "related_feature_ids": ["F-001"],
  "confidence": "high | medium | low",
  "source_agent": "actor-feature-mapper"
}
```

---

## `normalized/business-rules.jsonl`

One record per business rule.

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

One record per gap or open question.

```json
{
  "gap_id": "FGAP-001",
  "category": "missing_evidence | unmapped_ui | orphan_io | unresolved_rule | unknown_actor | large_file_uncovered",
  "blocking": true,
  "description": "What is unknown or uncovered",
  "affected_items": ["UC-001", "F-002"],
  "source_agent": "user-flow-analyst",
  "auto_resolvable": false
}
```

---

## `raw/` files

One JSONL per sub-agent (pre-normalization):

- `raw/ui-surface-findings.jsonl` — ui-surface-analyst raw output
- `raw/io-catalog-findings.jsonl` — io-catalog-analyst raw output
- `raw/user-flow-findings.jsonl` — user-flow-analyst raw output
- `raw/implicit-logic-findings.jsonl` — implicit-logic-analyst raw output

Each raw file: one record per finding, same fields as the normalized equivalent plus a `raw_text` field for the agent's original description.

---

## `normalized/uc-evidence-matrix.csv`

Columns: `uc_id, title, evidence_count, has_evidence (true/false), inference_level, status`

One row per use case. Produced by functional-traceability-auditor.

---

## `normalized/functional-traceability-audit.json`

Schema (see `functional-traceability-auditor` for the full spec — this is the output it produces):

```json
{
  "run_id": "<ISO-8601>",
  "agent": "functional-traceability-auditor",
  "verdict": "PASS | PASS_WITH_GAPS | FAIL",
  "pass1_traceability": {"uc_with_evidence": 0, "uc_without_evidence": 0},
  "pass2_negative_space": {"routes_covered": 0, "routes_uncovered": 0},
  "pass3_purity": {"violations": []},
  "findings": []
}
```

---

## Confidence + inference levels (applies to all JSONL)

| Level | Inference | Meaning |
|---|---|---|
| `high` | `direct` | Code evidence directly proves the claim |
| `medium` | `derived` | Inferred from multiple indirect signals |
| `low` | `speculative` | Plausible but unverified |

Missing evidence → use `functional-gaps.jsonl`, not a speculative claim.
