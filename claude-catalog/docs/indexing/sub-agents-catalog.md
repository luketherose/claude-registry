# Sub-agents catalogue (Sonnet)

> Reference doc for `indexing-supervisor`. Read at runtime when planning a
> dispatch — confirms which sub-agent owns which output target.

---

## Knowledge base layout

The KB lives at `<repo>/.indexing-kb/` and is the only writable location for
sub-agents. Every file is markdown with YAML frontmatter:

```yaml
---
agent: <sub-agent-name>
generated: <ISO-8601 timestamp>
source_files: [<paths-or-globs>]
confidence: high | medium | low
status: complete | partial | needs-review
---
```

Full directory layout:

```
.indexing-kb/
├── 00-index.md                  (synthesizer)
├── 01-overview.md               (synthesizer)
├── 02-structure/                (codebase-mapper)
├── 03-dependencies/             (dependency-analyzer)
├── 04-modules/                  (module-documenter, one file per package)
├── 05-streamlit/                (streamlit-analyzer, only if applicable)
├── 06-data-flow/                (data-flow-analyst)
├── 07-business-logic/           (business-logic-analyst)
├── 08-synthesis/                (synthesizer)
└── _meta/
    ├── manifest.json
    ├── coverage.md
    └── unresolved.md
```

Sub-agents must not write outside `.indexing-kb/`. Verify after each dispatch
by listing modified files.

---

## Sub-agents (Sonnet)

| Sub-agent | Output target |
|---|---|
| `codebase-mapper` | `02-structure/codebase-map.md`, `02-structure/language-stats.md`, `02-structure/stack.json` (authoritative AS-IS stack) |
| `dependency-analyzer` | `03-dependencies/external-deps.md`, `03-dependencies/internal-deps.md` |
| `streamlit-analyzer` | `05-streamlit/*.md` (only if Streamlit detected) |
| `module-documenter` | `04-modules/<package>.md` (one invocation per package) |
| `data-flow-analyst` | `06-data-flow/*.md` |
| `business-logic-analyst` | `07-business-logic/*.md` |
| `synthesizer` | `00-index.md`, `01-overview.md`, `08-synthesis/*.md` |
