# Evidence-backed Context Graph Schema

## Purpose

The context graph is a lightweight graph over the indexed KB that connects files,
symbols, UI surfaces, routes, use cases, rules, data flows, risks, and tests. It
enables targeted context bundle retrieval for Phase 1 and Phase 2 agents.

The graph does NOT replace the evidence ledger. Its role is to FIND evidence, not
to be a source of truth itself. No claim may cite only the graph without an
`evidence_id` that traces back to a Bronze or Silver record.

## Location

`.indexing-kb/graph/` with the following files:

| File | Description |
|---|---|
| `nodes.jsonl` | One node record per line |
| `edges.jsonl` | One edge record per line |
| `aliases.jsonl` | Name aliases and canonical mappings |
| `retrieval-index.json` | Fast lookup index for bundle assembly |
| `graph-quality-report.md` | Quality metrics and PASS/FAIL verdict |
| `context-bundles/` | Pre-assembled subgraphs per use case |

## Node types

File, SourceChunk, Symbol, Package, Entrypoint, Route, UISurface, Callback,
StateVariable, ConfigKey, EnvVar, Dependency, DataEntity, DatabaseTable,
ExternalSystem, IOBoundary, BusinessRule, ValidationRule, FeatureCandidate,
UseCase, Actor, TechnicalFinding, Risk, Test, Evidence, Gap

## Node schema

```json
{
  "node_id": "SYM-app.pages.upload.render_upload_page",
  "type": "Symbol",
  "label": "render_upload_page",
  "file": "app/pages/upload.py",
  "lines": "42-117",
  "evidence_ids": ["EV-000184"],
  "tags": ["ui", "upload", "csv"],
  "confidence": "high",
  "origin": "deterministic_scan | static_analysis | agent_extraction | human_confirmed"
}
```

`node_id` format: `<TYPE>-<qualified-name>`, e.g.:
- `SYM-app.pages.upload.render_upload_page`
- `FILE-app/pages/upload.py`
- `UI-upload_csv_page`
- `ENV-DATABASE_URL`

## Edge types

CONTAINS, IMPORTS, CALLS, READS_ENV, READS_CONFIG, READS_STATE, WRITES_STATE,
EXPOSES_ROUTE, RENDERS_UI, TRIGGERS_CALLBACK, READS_DATA, WRITES_DATA,
CALLS_EXTERNAL_SYSTEM, IMPLEMENTS_FEATURE, SUPPORTS_USE_CASE, ENFORCES_RULE,
VALIDATED_BY_TEST, AFFECTS_USE_CASE, HAS_RISK, HAS_GAP, CITES_EVIDENCE,
ALIAS_OF, RELATED_TO

## Edge schema

```json
{
  "edge_id": "EDGE-000101",
  "source": "UI-upload_csv_page",
  "target": "SYM-app.services.import_service.validate_records",
  "type": "CALLS",
  "evidence_ids": ["EV-000184", "EV-000191"],
  "confidence": "high",
  "origin": "deterministic_scan | static_analysis | agent_extraction | human_confirmed",
  "status": "confirmed | candidate | rejected",
  "inference_level": "direct | derived | speculative"
}
```

## Graph rules

- Only `confirmed` nodes and edges may feed final reports as established facts.
- `candidate` edges feed open questions and gaps.
- `rejected` edges remain as negative knowledge — useful for audits.
- Every non-trivial edge must have at least one `evidence_id`.
- The graph CANNOT be the sole source of truth for any claim.
- No claim may cite only the graph without an `evidence_id`.

## Context bundle

A context bundle is a targeted subgraph assembled for a specific purpose, e.g.
"confirm UC for CSV import". Bundles are the primary retrieval unit for Phase 1
and Phase 2 agents — they keep context windows small and evidence-anchored.

Schema:

```json
{
  "bundle_id": "CTX-UC-CAND-014",
  "purpose": "confirm functional use case for CSV import",
  "seed_nodes": ["UI-upload_csv_page"],
  "included_nodes": ["UI-upload_csv_page", "SYM-render_upload_page", "SYM-validate_csv"],
  "included_evidence_ids": ["EV-000184", "EV-000185"],
  "included_chunks": ["CHUNK-app-pages-upload-0001"],
  "excluded_candidates": [
    {"node_id": "SYM-archive_import", "reason": "dead/unreferenced from selected UI surface"}
  ],
  "open_gaps": ["No test evidence found for invalid CSV format"]
}
```

Context bundles are stored at `graph/context-bundles/CTX-<id>.json`.

## Graph quality report

`graph/graph-quality-report.md` must include:

- Node counts per type
- Edge counts per type
- Orphan nodes (nodes with no edges)
- Candidate edges count
- Rejected edges count
- UI surfaces without a mapped use case
- Routes without a handler symbol
- Env vars without config documentation
- Business rules without a use case
- Verdict: PASS | PASS_WITH_GAPS | FAIL

## Build scripts

`build_context_graph.py` reads `bronze/`, `silver/`, and `evidence-ledger.jsonl`,
then writes `graph/`.

`retrieve_context_bundle.py --seed <node_id> --hops 2 --purpose functional`
traverses the graph and writes a context bundle to `graph/context-bundles/`.
