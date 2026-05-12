# Sub-agents catalogue (Sonnet)

> Reference doc for `indexing-supervisor`. Read at runtime when planning a
> dispatch — confirms which sub-agent owns which output target.

---

## Knowledge base layout

The KB lives at `<repo>/.indexing-kb/` and is the only writable location for
sub-agents.

> IMPORTANT: The canonical `stack.json` path is now `.indexing-kb/bronze/stack.json`.
> All downstream phases (Phase 1, 2, 3) must read from this path.

> IMPORTANT: Sub-agents must also append to `evidence-ledger.jsonl` at the KB root
> for every observable fact they extract. See `docs/indexing/evidence-ledger-schema.md`.

> Silver outputs are JSONL (one JSON record per line), not markdown. Every Silver
> record must include `evidence_ids` array. See `docs/indexing/grounding-policy.md`.

Full directory layout:

```
.indexing-kb/
  bronze/                          ← deterministic facts from scripts
    manifest.json                  (codebase-mapper)
    file-inventory.jsonl           (codebase-mapper)
    file-hashes.json               (codebase-mapper)
    stack.json                     (codebase-mapper — SINGLE SOURCE OF TRUTH)
    symbol-index.jsonl             (codebase-mapper)
    import-graph.json              (dependency-analyzer)
    dependency-locks.json          (dependency-analyzer)
    entrypoints.json               (codebase-mapper)
    routes.json                    (codebase-mapper)
    ui-surfaces.json               (codebase-mapper / streamlit-analyzer)
    config-env-index.jsonl         (data-flow-analyst)
    io-boundaries.jsonl            (data-flow-analyst)
    test-inventory.jsonl           (codebase-mapper)
    large-files.jsonl              (codebase-mapper)
    large-file-chunks.jsonl        (codebase-mapper)
    parse-errors.jsonl             (codebase-mapper)
  silver/                          ← agentic extractions with evidence_ids
    module-summaries.jsonl         (module-documenter)
    business-rules.jsonl           (business-logic-analyst)
    validation-rules.jsonl         (business-logic-analyst)
    state-machines.jsonl           (business-logic-analyst)
    data-flows.jsonl               (data-flow-analyst)
    integration-points.jsonl       (data-flow-analyst)
    framework-findings.jsonl       (streamlit-analyzer)
    assumptions.jsonl              (all sub-agents)
    gaps.jsonl                     (all sub-agents)
    large-file-summaries.jsonl     (module-documenter)
  gold/                            ← synthesis, no new claims
    system-overview.md             (synthesizer)
    bounded-context-hypothesis.md  (synthesizer)
    complexity-hotspots.md         (synthesizer)
    coverage-report.md             (indexing-auditor)
    unresolved-gaps.md             (synthesizer + indexing-auditor)
    indexing-audit.md              (indexing-auditor)
    indexing-audit.json            (indexing-auditor)
    analysis-quality-summary.md    (indexing-auditor)
  graph/                           ← context graph + retrieval
    nodes.jsonl
    edges.jsonl
    aliases.jsonl
    retrieval-index.json
    graph-quality-report.md
    context-bundles/
  evidence-ledger.jsonl            ← central evidence registry
  _meta/
    manifest.json                  (unchanged format)
    unresolved.md                  (unchanged)
```

Sub-agents must not write outside `.indexing-kb/`. Verify after each dispatch
by listing modified files.

---

## Sub-agents (Sonnet)

| Sub-agent | Output target |
|---|---|
| `codebase-mapper` | `bronze/manifest.json`, `bronze/file-inventory.jsonl`, `bronze/file-hashes.json`, `bronze/stack.json` (authoritative AS-IS stack), `bronze/symbol-index.jsonl`, `bronze/entrypoints.json`, `bronze/routes.json`, `bronze/test-inventory.jsonl`, `bronze/large-files.jsonl`, `bronze/large-file-chunks.jsonl`, `bronze/parse-errors.jsonl` |
| `dependency-analyzer` | `bronze/import-graph.json`, `bronze/dependency-locks.json` |
| `streamlit-analyzer` | `silver/framework-findings.jsonl`, `bronze/ui-surfaces.json` (only if Streamlit detected) |
| `module-documenter` | `silver/module-summaries.jsonl`, `silver/large-file-summaries.jsonl` (one invocation per package) |
| `data-flow-analyst` | `silver/data-flows.jsonl`, `silver/integration-points.jsonl`, `bronze/config-env-index.jsonl`, `bronze/io-boundaries.jsonl` |
| `business-logic-analyst` | `silver/business-rules.jsonl`, `silver/validation-rules.jsonl`, `silver/state-machines.jsonl` |
| `synthesizer` | `gold/system-overview.md`, `gold/bounded-context-hypothesis.md`, `gold/complexity-hotspots.md`, `gold/unresolved-gaps.md` |
| `indexing-auditor` | `gold/indexing-audit.md`, `gold/indexing-audit.json` (read-only quality gate) |

---

## Phase 0 workflow steps

Sub-agents run in waves. The supervisor dispatches them in the order below and
waits for each wave to complete before advancing.

| Wave | Sub-agent(s) | Notes |
|---|---|---|
| 1 | `codebase-mapper` | Always first — produces bronze/stack.json used by all later agents |
| 2 | `dependency-analyzer`, `streamlit-analyzer` (conditional) | Run in parallel |
| 3 | `module-documenter` (one per package), `data-flow-analyst`, `business-logic-analyst` | Run in parallel |
| 4 | `synthesizer` | Requires Waves 1–3 complete |
| 4a | `indexing-auditor` | Run after synthesizer completes. Read-only audit pass — produces gold/indexing-audit.md and gold/indexing-audit.json. Must complete before HITL checkpoint. |
| HITL | — | Supervisor presents summary to user; user confirms or requests gap closure |
