# Module Documenter: Output Specification

Reference doc for `module-documenter`. Read before writing any output file.

---

## Output targets

| Artifact | Path | Tier |
|---|---|---|
| Module summary (JSONL) | `.indexing-kb/silver/module-summaries.jsonl` | Silver: one record per package |
| Large-file summary (JSONL) | `.indexing-kb/silver/large-file-summaries.jsonl` | Silver: for packages with large files |
| Assumptions (JSONL) | `.indexing-kb/silver/assumptions.jsonl` | Silver: assumptions made during analysis |
| Human-readable doc | `.indexing-kb/04-modules/<package-name>.md` | Human |

---

## Silver JSONL record schema (`silver/module-summaries.jsonl`)

One record per package, appended (do not overwrite the file):

```json
{
  "module_id": "MOD-001",
  "package": "app.services",
  "file": "app/services/import_service.py",
  "purpose": "Short factual description",
  "public_api": ["function_name", "ClassName"],
  "evidence_ids": ["EV-000001"],
  "confidence": "high | medium | low",
  "is_large_file": false,
  "chunk_ids_used": []
}
```

---

## Markdown output schema (`.indexing-kb/04-modules/<package-name>.md`)

Single file per package:

```markdown
---
agent: module-documenter
generated: <ISO-8601>
source_files: ["<package path>"]
language: <python | java | kotlin | go | …>
confidence: <high|medium|low>
status: complete
---

# Package: <name>

## Purpose
<2-3 sentences inferred from docs, names, and structure. If unclear,
write: "Purpose unclear — see Open questions" and add the question below.>

## Public interface

### Classes / types
| Name | Kind | File | Members (count) | Purpose (1 line) |
|---|---|---|---|---|

(Kind = class | interface | trait | enum | record | struct | sealed | …
per language.)

### Functions / methods
| Name | File | Signature | Side effects? |
|---|---|---|---|

### Constants / module-level values
| Name | File | Type (if declared) | Value (if simple literal) |
|---|---|---|---|

### Re-exports
| Name | Source | (e.g. for Python `from .x import Y`; for Rust `pub use`; for TS `index.ts`) |
|---|---|---|

## Internal structure
- Sub-packages / sub-modules: <list>
- File organization: <one-line description>

## Entrypoints (external-facing)
- Imported externally as: <list of import statements observed elsewhere>

## Technical debt markers
| File:line | Type | Comment (truncated) |
|---|---|---|
| `<path>:42` | TODO | "fix this race condition" |
| `<path>:88` | FIXME | "..." |

## Open questions
- <Functions with unclear purpose: name + file:line>
- <Classes with no doc comment AND ambiguous name>
- <Sub-packages whose role is unclear>
```
