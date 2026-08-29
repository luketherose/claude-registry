# User-Flow Analyst: JSONL Output Specification

This document defines the JSONL output schemas for `user-flow-analyst`. Read it before writing any JSONL file. Write raw JSONL to `docs/analysis/01-functional/raw/` BEFORE writing narrative markdown.

---

## `docs/analysis/01-functional/raw/user-flow-findings.jsonl`

Raw UC findings before normalization: one record per candidate UC, as derived from the cross-product of Wave 1 outputs.

---

## `docs/analysis/01-functional/normalized/use-case-candidates.jsonl`

Authoritative UC list. One record per use case. Required schema:

```json
{
  "uc_id": "UC-001",
  "title": "Use case title",
  "status": "confirmed | candidate_not_confirmed | requires_human_confirmation",
  "actors": ["A-01"],
  "evidence_ids": ["EV-000001"],
  "source_confidence": "high | medium | low",
  "inference_level": "direct | derived | speculative",
  "unknowns": [],
  "related_features": ["F-01"],
  "related_screens": ["S-01"],
  "related_transformations": ["TR-01"]
}
```

Rules:
- Never mark a UC `status: confirmed` without at least one `evidence_id` from `.indexing-kb/evidence-ledger.jsonl`.
- UCs with no confirming evidence → `status: candidate_not_confirmed`; populate `unknowns`.
- UCs with conflicting signals across Wave 1 outputs → `status: requires_human_confirmation`.
