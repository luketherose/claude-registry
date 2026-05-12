# Codebase mapper — output templates

> Reference doc for `codebase-mapper`. Read at runtime when emitting
> primary deliverable files under `.indexing-kb/bronze/` and the
> backward-compatible copies under `.indexing-kb/02-structure/`.

All files are mandatory on every run. Write each through the `Write`
tool — never via Bash heredoc/redirect.

---

## bronze/file-inventory.jsonl (one record per file)

```json
{"file": "path/to/file.py", "size_bytes": 1234, "line_count": 50, "language": "python", "category": "source | test | config | docs | generated | vendor | build_artifact", "hash": "sha256:..."}
```

`category` values:
- `source` — production source code
- `test` — test files (detected by naming convention or framework markers)
- `config` — configuration files (.env, .yaml, .toml, .ini, etc.)
- `docs` — documentation files (.md, .rst, .txt, etc.)
- `generated` — auto-generated files (build artifacts, proto outputs, etc.)
- `vendor` — vendored third-party code
- `build_artifact` — compiled outputs, lock files with binary content

---

## bronze/large-files.jsonl (one record per large file)

```json
{"file": "path/to/large_file.py", "size_bytes": 245000, "line_count": 3120, "classification": "large | huge | giant | generated | minified | data | vendor | source", "language": "python", "parse_strategy": "ast_symbols | regex_symbols | line_chunks | data_profile | excluded_generated", "reason": "why it is considered large", "status": "indexed | partially_indexed | excluded_with_reason | parse_failed", "notes": []}
```

`classification` values:
- `large` — >800 lines or >150 KB
- `huge` — >2000 lines or >500 KB
- `giant` — >5000 lines or >1 MB
- `generated` — auto-generated (may be excluded)
- `minified` — minified JS/CSS (excluded from symbol indexing)
- `data` — data file (CSV, JSON fixture, etc.) — data profile only
- `vendor` — vendored code — excluded from analysis
- `source` — large but genuine source code

`parse_strategy` values:
- `ast_symbols` — Python AST used to create per-class/function chunks
- `regex_symbols` — regex-based symbol extraction for non-Python
- `line_chunks` — 200-line windows (fallback)
- `data_profile` — row count, column names sample only
- `excluded_generated` — excluded because auto-generated

---

## bronze/large-file-chunks.jsonl (one record per chunk)

```json
{"chunk_id": "CHUNK-path-to-file-0001", "file": "path/to/large_file.py", "lines": "1-220", "kind": "symbol | class | function | logical_section | line_window | data_sample | config_block", "symbols": ["optional"], "hash": "sha256:...", "summary": "Short factual summary.", "evidence_id": "EV-000123"}
```

`evidence_id` must match an entry in `evidence-ledger.jsonl` with `kind: source_chunk`.

---

## bronze/stack.json

```json
{
  "schema_version": "1.0",
  "generated": "<ISO-8601>",
  "stack": {
    "primary_language": "python",
    "languages": ["python", "typescript"],
    "frameworks": ["streamlit", "fastapi"],
    "build_tools": ["uv", "npm"],
    "package_managers": ["pip", "npm"],
    "runtime": "cpython 3.11",
    "test_frameworks": ["pytest"],
    "confidence": "high",
    "evidence": [
      "pyproject.toml at repo root (Python build manifest)",
      "12 .py files, 0 .java files (Python primary)",
      "import streamlit as st in app.py:1 (Streamlit framework)",
      "package.json with @angular/cli@17 in frontend/ (Angular framework)",
      "pytest declared in pyproject.toml [project.optional-dependencies] (test framework)"
    ]
  }
}
```

`bronze/stack.json` is **the single source of truth** for AS-IS stack
information. Every supervisor at Phases 1-5 reads it (directly or via the
manifest copy) to decide which sub-agents and skills to engage. Schema is
documented in `claude-catalog/docs/language-agnostic-design.md`.

---

## Backward-compatible legacy files (02-structure/)

Write these only when an existing KB already contains `02-structure/`.
Do not create this directory on a fresh run.

## File 1: `.indexing-kb/02-structure/codebase-map.md`

````markdown
---
agent: codebase-mapper
generated: <ISO-8601>
source_files: ["<scanned root>"]
confidence: high
status: complete
---

# Codebase map

## Repository statistics
- Total files: <N>
- Source files by language:
  - python: <N> (LOC: <N>)
  - java: <N> (LOC: <N>)
  - typescript: <N> (LOC: <N>)
  - …
- Test files: <N>
- Config files: <N>
- Build manifests: <N>

## Stack summary
- Primary language: <python | java | …>
- Languages: [<list>]
- Frameworks: [<list>]
- Test frameworks: [<list>]
- Build tools: [<list>]
- Confidence: <high|medium|low>

(See `stack.json` for the machine-readable form.)

## Top-level packages / modules
| Package | Path | Files | LOC | Marker |
|---|---|---|---|---|

## Entrypoints
- `<path>` — <reason>

## Directory tree (depth 3)

```
<output of: find <root> -maxdepth 3 -type d -not -path '*/skip/*'>
```

## Skipped directories
- `<dir>` — reason
````

---

## File 2: `.indexing-kb/02-structure/language-stats.md`

```markdown
---
agent: codebase-mapper
generated: <ISO-8601>
source_files: ["<scanned root>"]
confidence: high
status: complete
---

# Language statistics

| Language/Type | File count | LOC | % of codebase |
|---|---|---|---|
| python | … | … | … |
| typescript | … | … | … |
| html / template | … | … | … |
| config | … | … | … |
| build manifest | … | … | … |
| other | … | … | … |
```

---

## File 3: `.indexing-kb/02-structure/stack.json` (legacy backward-compat copy)

Same schema as `bronze/stack.json`. Written only when `02-structure/` already exists in the KB.
