# Grounding Policy — No Evidence, No Claim

## Purpose

Agents in the Phase 0 indexing pipeline must not invent, infer, or speculate about codebase behavior without traceable evidence. Every claim about what the codebase does, how it behaves, or what business logic it implements must be grounded in observed source artifacts.

Framework knowledge is NOT evidence. Knowing that Flask routes are defined with `@app.route` does not prove a particular route exists in this codebase — that must be observed in the source. Naming plausibility is NOT evidence. A class named `ApprovalManager` does not prove an approval workflow exists — the behavior must be verified in the code body.

Violations of this policy produce unreliable knowledge bases that mislead downstream phases and cause replatforming decisions to be made on hallucinated foundations.

## Evidence ID citation rules

Every claim in a silver or gold artifact must cite at least one `evidence_id` of the form `EV-NNNNNN` sourced from `evidence-ledger.jsonl`.

Rules:

- Cite the specific file path and line range where the evidence was observed, not just the file name.
- For large files: cite the `chunk_id` from `bronze/large-file-chunks.jsonl` plus the line range of the relevant chunk. Do not cite the whole file as evidence for a specific behavior.
- Never write "from the code it emerges that..." — write the evidence_id instead. Example: `evidence_ids: ["EV-000042"]`.
- A claim without at least one `evidence_id` is a gap, not a finding.
- Multiple evidence_ids are allowed and encouraged when a claim is supported by several observations.

## Confidence and inference levels

Every claim must carry both a `confidence` and an `inference_level` field:

| confidence | inference_level | Meaning |
|---|---|---|
| `high` | `direct` | Direct code evidence, observed and verified in the source |
| `medium` | `derived` | Inferred from multiple indirect signals that together strongly suggest the behavior |
| `low` | `speculative` | Plausible based on naming, structure, or partial signals, but unverified |

If no evidence exists to support a claim at even `low` confidence, do not create a claim. Create a gap record in `silver/gaps.jsonl` instead.

## What you MUST NOT do

- Use framework knowledge to promote a claim to fact without direct code evidence. Knowing a framework's conventions does not substitute for reading the actual code.
- Use naming plausibility as proof of business behavior. A class named `ApprovalManager` does not prove an approval workflow exists. A function named `send_notification` does not prove a notification is sent — it must be observed.
- Claim a feature exists because of a function name, file name, or import alias alone.
- Skip reading a chunk and still claim knowledge of its content. If you have not read chunk `CHUNK-foo-0003`, you have no evidence for claims about lines 600–800 of `foo.py`.
- Attribute behavior to a large file you haven't chunked. A file classified as large/huge/giant must be chunked before any claims are drawn from it.
- Aggregate multiple speculative claims into a medium-confidence finding. Stacking speculation does not raise confidence.
- Emit a finding with `inference_level: direct` when the evidence was indirect, renamed, or inferred.

## Gaps and open questions

When evidence is missing or insufficient, create a gap record rather than a claim.

Gap records go in `silver/gaps.jsonl`. Format:

```json
{
  "gap_id": "GAP-001",
  "description": "No source evidence found for the reported approval workflow. ApprovalManager class was not chunked.",
  "affected_area": "business-logic",
  "blocking": true
}
```

Field rules:

- `gap_id`: sequential, prefixed `GAP-`, three-digit zero-padded.
- `description`: plain-language statement of what is unknown and why.
- `affected_area`: one of `business-logic`, `data-access`, `integration`, `configuration`, `security`, `ui`, `infrastructure`, `unknown`.
- `blocking`: `true` if the gap prevents Phase 0 from declaring PASS; `false` if it is informational only. Non-blocking gaps are surfaced to downstream phases as open questions.

## Synthesizer rule

The synthesizer agent that produces gold artifacts operates under a strict aggregation-only constraint:

- It CANNOT introduce new facts. Every fact in a gold artifact must trace back to a claim already present in `bronze/` or `silver/` with a valid `evidence_id`.
- It CAN aggregate, group, deduplicate, and prioritize claims that already exist.
- It CAN assign a consolidated confidence level when multiple silver claims converge on the same finding.
- If a claim does not appear in bronze or silver with a valid evidence_id, it must not appear in gold. The synthesizer must not "fill in" plausible details from framework knowledge.
- When the synthesizer detects a conflict between two silver claims about the same symbol, it must record the conflict explicitly rather than silently picking one.
