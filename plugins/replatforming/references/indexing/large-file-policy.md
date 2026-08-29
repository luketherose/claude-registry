# Large File Handling Policy

## Problem

Agents struggle with large source files. Common failure modes include losing content from the middle of the file, hallucinating behavior not present in the actual code, and citing a file as evidence for a claim without having read the relevant lines. This policy mandates a structured outline-first, chunk-based approach that produces verifiable evidence records for every large file.

Skipping this policy is a grounding violation per `grounding-policy.md`.

## Thresholds

| Classification | Line count | Size |
|---|---|---|
| `large` | > 800 lines | > 150 KB (153 600 bytes) |
| `huge` | > 2 000 lines | > 500 KB (512 000 bytes) |
| `giant` | > 5 000 lines | > 1 MB (1 048 576 bytes) |

These thresholds are configurable via the `large_file_thresholds` field in `bronze/manifest.json`. If that field is absent, the defaults above apply.

All three classifications are treated as large files for policy purposes. The classification affects how urgently chunking is prioritized and how many agents may need to collaborate, but the mandatory steps are the same.

## Mandatory strategy: outline → chunk → evidence → summary

Processing a large file must follow these four steps in order. Steps must not be skipped or reordered.

### Step 1 — Outline

Before reading any line-range chunk, produce a structural outline of the file. Use AST parsing for Python files. Use regex heuristics for other languages.

The outline must list:

- Top-level classes and their methods (name + line number)
- Top-level functions (name + line number)
- Import blocks (line range)
- Route or handler definitions
- Constants and configuration blocks
- UI sections, page definitions, or widget registrations (for Streamlit files)
- Callbacks and event handlers
- Data access calls (ORM queries, raw SQL, file I/O)
- External service calls (HTTP clients, queue producers/consumers)
- Test functions or test classes

The outline is stored in `bronze/large-file-outlines.jsonl` with the file path, classification, and the structured symbol list.

### Step 2 — Chunk

Divide the file into semantic chunks based on the outline. Rules:

- Prefer symbol-based chunks: one chunk per top-level class or top-level function. Keep the full body of the symbol in one chunk.
- When a class body exceeds 300 lines, split at the method level.
- For files where semantic chunking is impossible (e.g., a procedural script with no top-level symbols), fall back to 200-line windows with a 20-line overlap.
- Each chunk gets:
  - `chunk_id`: `CHUNK-<safe-path>-<4digit-seq>` where `<safe-path>` replaces `/`, `.`, spaces, and other non-alphanumeric characters with `-` and `<4digit-seq>` is zero-padded (e.g., `CHUNK-src-app-routes-0003`).
  - `sha256` hash of the exact lines in the chunk.
  - `lines`: start and end line numbers (inclusive).

Chunks are stored in `bronze/large-file-chunks.jsonl`.

### Step 3 — Evidence

Every chunk that contains behavior relevant to the knowledge base must produce an evidence record in `evidence-ledger.jsonl` with `kind: source_chunk`.

The evidence record's `summary` must describe what was observed in that chunk in verifiable terms (e.g., "Defines `process_payment` method that calls `stripe.PaymentIntent.create` at line 234"). It must not summarize behavior that is not in the chunk.

Not every chunk must become evidence. Chunks classified as `support_code`, `generated`, `vendor`, or `dead_or_unreferenced` (see symbol classification below) may be skipped, but the skip decision must be recorded in `bronze/large-file-chunks.jsonl` as `analyzed: false` with a `skip_reason`.

### Step 4 — Summary

Only after chunk-level evidence is established, produce a file-level summary. The summary must aggregate chunk summaries. It must not introduce claims that are not already present in the chunk-level evidence records.

Never skip directly to a file-level summary without first completing Steps 1–3.

## Symbol classification taxonomy

Every symbol or chunk must be assigned one of the following classifications:

| Classification | Meaning |
|---|---|
| `relevant_functional` | Contains business logic, domain behavior, or feature implementation |
| `relevant_technical` | Contains infrastructure, middleware, framework wiring, or cross-cutting concerns |
| `support_code` | Utility helpers, formatters, validators with no business semantics |
| `test_code` | Test functions, test classes, fixtures |
| `config` | Configuration constants, environment loading, settings |
| `generated` | Auto-generated code (migrations, serializers, protobuf outputs) |
| `vendor` | Third-party code bundled in the repo |
| `dead_or_unreferenced` | Symbols with no callers detected and no export |
| `unknown_requires_review` | Cannot be classified without additional context |

Classification is stored in the `classification` field of each chunk record in `bronze/large-file-chunks.jsonl`.

## Generated, minified, and vendor files

If a large file is clearly generated (e.g., database migration, compiled asset, protobuf output), minified (JS/CSS bundle), or a vendored third-party artifact:

- Do NOT analyze it as source code.
- Do NOT run the outline → chunk → evidence → summary pipeline on it.
- Register it in `bronze/large-files.jsonl` with `status: excluded_with_reason` and a human-readable `exclusion_reason`.
- Do NOT create feature findings or business-logic claims from it.

Indicators of generated/minified/vendor status: file path contains `migrations/`, `vendor/`, `node_modules/`, `dist/`, `build/`, `.min.js`; or the first line contains a generator comment.

## Data files (JSON, CSV, XML, YAML)

For data files above the large threshold:

- Do not read the entire file.
- Produce a deterministic profile:
  - File size and line count.
  - Schema, column names, or top-level keys.
  - Head sample: first 10 records or entries.
  - Tail sample: last 10 records or entries.
  - Approximate null value counts per column (for tabular files).
  - Approximate value types per column.
- Store the profile in `bronze/data-file-profiles.jsonl`.
- Do NOT infer business rules from a dataset without additional evidence from source code that reads or processes the file.

## Parse errors

If a large file cannot be parsed (syntax error, encoding issue, binary content):

1. Add a record to `bronze/parse-errors.jsonl` with the file path, classification, and error message.
2. Create a gap in `silver/gaps.jsonl` with `blocking: true` if the file is classified `relevant_functional` or `relevant_technical`; `blocking: false` otherwise.
3. Never invent behavior from a failed parse. The file is unknown territory until the parse error is resolved.

## Coverage gate

Phase 0 cannot declare PASS if any source file classified as `large`, `huge`, or `giant` satisfies both of the following conditions:

- No entry in `bronze/large-files.jsonl` with a valid `status` field.
- No `exclusion_reason` explaining why it was intentionally skipped.

Every large file must be accounted for: either analyzed (with chunk evidence) or explicitly excluded. Unaccounted large files are blocking gaps.
