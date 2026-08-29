# Evidence Ledger Schema

## Purpose

The `evidence-ledger.jsonl` file at `.indexing-kb/evidence-ledger.jsonl` is the central registry of all observable facts extracted from the codebase during Phase 0. It is the single source of truth for grounding claims.

Every Silver claim must cite at least one `EV-` id from this file. A claim without an evidence_id is a gap, not a finding. Gold artifacts must trace every fact back to evidence already registered here.

The ledger is append-only during a pipeline run. Sub-agents write to it; no agent deletes or modifies existing records.

## File location

`.indexing-kb/evidence-ledger.jsonl`

One JSON object per line. UTF-8. No trailing comma. No wrapping array.

## Record schema

```json
{
  "evidence_id": "EV-000001",
  "kind": "source_symbol | source_file | source_chunk | route | ui_surface | config | dependency | test | runtime_observation | tool_output",
  "file": "path/to/file.py",
  "lines": "10-42",
  "symbols": ["symbolName"],
  "chunk_id": "CHUNK-path-to-file-0001",
  "hash": "sha256:...",
  "summary": "Short verifiable description of what was observed.",
  "detected_by": "agent-or-script-name",
  "verified_by": null
}
```

Field rules:

- `evidence_id`: required. Format `EV-` + 6-digit zero-padded sequence. Globally unique within a run.
- `kind`: required. One of the values defined in "Kind values" below.
- `file`: required. Repo-relative path to the source file.
- `lines`: required for `source_symbol`, `source_chunk`, `route`, `ui_surface`, `test`. Format `"start-end"` (inclusive). Omit for `dependency`, `tool_output`, `runtime_observation`.
- `symbols`: optional. List of symbol names (class, function, constant) observed in this evidence record.
- `chunk_id`: required when `kind` is `source_chunk`. Format defined in `large-file-policy.md`.
- `hash`: optional but recommended. SHA-256 hash of the observed lines, prefixed `sha256:`. Enables change detection on re-runs.
- `summary`: required. One or two sentences describing what was observed in verifiable terms. Must describe the observation, not the interpretation.
- `detected_by`: required. Name of the sub-agent or script that produced this record (e.g., `codebase-mapper`, `business-logic-analyst`, `dependency-analyzer`).
- `verified_by`: nullable. Set when a confirming agent appends its `tool_output` record — the original record retains `verified_by: null` (ledger is append-only); the confirmation is carried in the appended record's `summary`.

## Kind values

| Kind | Description |
|---|---|
| `source_symbol` | A class, function, method, or constant detected in source. Lines point to the definition. |
| `source_file` | An entire file treated as evidence. Use only for files below the large-file threshold. |
| `source_chunk` | A line-range chunk of a large file. Must carry a `chunk_id`. |
| `route` | An HTTP endpoint or page route detected in the source (Flask route, FastAPI path, Django URL, etc.). |
| `ui_surface` | A Streamlit page, widget group, form, or other UI component detected in source. |
| `config` | A configuration key, environment variable, or settings entry detected. |
| `dependency` | An external library or package declared in requirements, pyproject.toml, package.json, etc. |
| `test` | A test file or individual test function detected. |
| `runtime_observation` | Runtime behavior observed via a tool-assisted run (e.g., profiler output, request log). Rare. |
| `tool_output` | Output from a scanner, linter, or static analysis tool (e.g., bandit, semgrep, pylint). |

## ID format

`EV-` followed by a 6-digit zero-padded sequence number. Sequence is global within a single pipeline run.

Examples: `EV-000001`, `EV-000042`, `EV-001337`.

The sequence restarts at `EV-000001` for each new run. Evidence from different runs must not be mixed in the same ledger file.

## Uniqueness rule

`evidence_id` must be unique per run. Never reuse an id within a run, even if the underlying evidence is identical. Duplicate evidence for the same file+lines+kind is allowed (a second agent may independently observe the same symbol) but must receive a distinct evidence_id. The `verified_by` field is the mechanism for cross-agent confirmation — not ID reuse.

## How sub-agents emit evidence

When a sub-agent observes a symbol, file, chunk, route, or pattern, it must:

1. Read the current tail of `evidence-ledger.jsonl` to determine the next sequence number and to check whether the same `file` + `lines` + `kind` combination already exists.
2. If the combination already exists, append a `tool_output` record that references the original `evidence_id` in its `summary` (e.g., `"Independently confirmed EV-000042"`) and sets `detected_by` to the confirming agent. Do not modify the original record — the ledger is append-only.
3. If the combination is new, append a new record with the next available `evidence_id`.
4. Always set `detected_by` to the sub-agent's canonical name as declared in the catalog.

Confirmation is recorded via an appended `tool_output` record, not by modifying the original. The same agent that created a record must not confirm its own evidence.

## Evidence for large files

For files classified as `large`, `huge`, or `giant` in `bronze/large-files.jsonl`:

- Evidence must point to a `chunk_id` and `lines` range, never to the whole file.
- Use `kind: source_chunk` with the chunk's line range.
- The only exception is a `source_file` record that captures the file's existence and metadata (size, line count, classification) — this is not a behavioral claim.
- Never write a behavioral summary that cites only the file path without a chunk_id. Downstream consumers cannot verify which lines support the claim.
