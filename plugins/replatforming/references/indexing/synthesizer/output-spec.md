# Synthesizer: Output Specification

Reference doc for `synthesizer`. Read before writing any output file.

---

## Contents

- [File 1: `.indexing-kb/00-index.md`](#file-1-indexing-kb00-indexmd): the KB index template.
- [File 2: `.indexing-kb/01-overview.md`](#file-2-indexing-kb01-overviewmd): the overview template.
- [File 3: `.indexing-kb/08-synthesis/bounded-contexts.md`](#file-3-indexing-kb08-synthesisbounded-contextsmd): the bounded contexts template.
- [File 4: `.indexing-kb/08-synthesis/complexity-hotspots.md`](#file-4-indexing-kb08-synthesiscomplexity-hotspotsmd): the complexity hotspots template.
- [File 5: `.indexing-kb/08-synthesis/indexing-report.md`](#file-5-indexing-kb08-synthesisindexing-reportmd): the indexing report template.
- [File 6: `.indexing-kb/_meta/unresolved.md`](#file-6-indexing-kb_metaunresolvedmd): the unresolved questions template.

## File 1: `.indexing-kb/00-index.md`

```markdown
---
agent: synthesizer
generated: <ISO-8601>
source_files: ["all of .indexing-kb/"]
confidence: high
status: complete
---

# Indexing knowledge base

This KB was produced by the indexing-supervisor pipeline on <date>.
It is the source of truth for understanding this codebase before any
migration planning.

## Quick links
- [System overview](01-overview.md)
- [Codebase map](02-structure/codebase-map.md)
- [Language stats](02-structure/language-stats.md)
- [External deps](03-dependencies/external-deps.md)
- [Internal deps](03-dependencies/internal-deps.md)
- [Streamlit analysis](05-streamlit/pages.md) <!-- if applicable -->
- [Module docs](04-modules/)
- [Database access](06-data-flow/database.md)
- [External APIs](06-data-flow/external-apis.md)
- [File I/O](06-data-flow/file-io.md)
- [Configuration](06-data-flow/configuration.md)
- [Domain concepts](07-business-logic/domain-concepts.md)
- [Validation rules](07-business-logic/validation-rules.md)
- [Business rules](07-business-logic/business-rules.md)
- [Bounded context hypothesis](08-synthesis/bounded-contexts.md)
- [Complexity hotspots](08-synthesis/complexity-hotspots.md)
- [Indexing report](08-synthesis/indexing-report.md)
- [Open questions](_meta/unresolved.md)

## Coverage summary
<copied from indexing-report.md>

## Recommended reading order
1. `01-overview.md`: orient yourself in 1 minute
2. `08-synthesis/bounded-contexts.md`: the high-level shape
3. `07-business-logic/domain-concepts.md`: the ubiquitous language
4. `04-modules/<top-level packages>.md`: depth where you need it
5. `06-data-flow/*.md`: what crosses the boundary
6. `08-synthesis/complexity-hotspots.md`: where risk concentrates
7. The rest as needed
```

---

## File 2: `.indexing-kb/01-overview.md`

```markdown
---
agent: synthesizer
generated: <ISO-8601>
source_files: ["02-structure/", "03-dependencies/", "04-modules/", "05-streamlit/"]
confidence: <high|medium>
status: complete
---

# System overview

## What this system is
<1 paragraph, plain language>

## Main packages
| Package | Role |
|---|---|

## External surface
- HTTP endpoints exposed: <count + examples>
- DB: `<engine>`, <table count> tables
- Files read/written: <summary>
- Env vars consumed: <count>

## UI
- <Streamlit pages: count + entrypoint, OR "no UI">

## Key external dependencies
1. `<dep>`: <role>
...
```

---

## File 3: `.indexing-kb/08-synthesis/bounded-contexts.md`

```markdown
---
agent: synthesizer
generated: <ISO-8601>
source_files: ["04-modules/", "07-business-logic/", "03-dependencies/"]
confidence: medium
status: complete
---

# Bounded context hypothesis

## Candidate contexts

### Context 1: <Name>
- Packages: <list>
- Core entities: <list>
- Owns: <list of operations>
- Boundary signals: <which other contexts call into it>

### Context 2: ...

## Cross-context concerns
- <Entity that appears in multiple contexts: flag for review>
- <Operations that cross context boundaries>

## Open questions
- <Splits that could go either way>
- <Concepts with unclear ownership>
```

---

## File 4: `.indexing-kb/08-synthesis/complexity-hotspots.md`

```markdown
---
agent: synthesizer
generated: <ISO-8601>
source_files: ["02-structure/", "03-dependencies/", "07-business-logic/"]
confidence: high
status: complete
---

# Complexity hotspots

## Scored package list
| Package | LOC | In-degree | Rules | Score | Notes |
|---|---|---|---|---|---|

## High-risk hotspots (2+ axes high)
- `<pkg>`: large + heavy coupling. Migration order: late, after dependents are migrated.

## Standalone migration candidates (low everything)
- `<pkg>`: minimal coupling, small. Good first migration target.
```

---

## File 5: `.indexing-kb/08-synthesis/indexing-report.md`

```markdown
---
agent: synthesizer
generated: <ISO-8601>
source_files: ["all of .indexing-kb/"]
confidence: high
status: complete
---

# Indexing report

## Coverage
- Packages fully indexed: <N>/<total>
- Packages partial: <list with reason>
- Packages skipped: <list with reason>
- Streamlit pages indexed: <N> (or "n/a")

## Confidence summary
| File | Confidence |
|---|---|
| 02-structure/codebase-map.md | high |
| ... | ... |

Total: <N high>, <N medium>, <N low>

## Open questions
- Total: <N>
- See `_meta/unresolved.md` for full list

## Estimated effort to resolve unclarities
- Low-confidence sections to revisit: <N>
- Bounded contexts with split votes: <N>
- Magic numbers without context: <N>
```

---

## File 6: `.indexing-kb/_meta/unresolved.md`

```markdown
# Unresolved questions

Aggregated from all phases.

## Phase 1: Structural
### codebase-mapper
- <question>

### dependency-analyzer
- <question>

### streamlit-analyzer
- <question>

## Phase 2: Module documentation
### <package-1>
- <question>

## Phase 3: Cross-cutting
### data-flow-analyst
- <question>

### business-logic-analyst
- <question>
```
