# Codebase mapper — output templates

> Reference doc for `codebase-mapper`. Read at runtime when emitting the
> three deliverable files under `.indexing-kb/02-structure/`.

All three files are mandatory on every run. Write each through the `Write`
tool — never via Bash heredoc/redirect.

---

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

## File 3: `.indexing-kb/02-structure/stack.json`

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

`stack.json` is **the single source of truth** for AS-IS stack
information. Every supervisor at Phases 1-5 reads it (directly or via the
manifest copy) to decide which sub-agents and skills to engage. Schema is
documented in `claude-catalog/docs/language-agnostic-design.md`.
