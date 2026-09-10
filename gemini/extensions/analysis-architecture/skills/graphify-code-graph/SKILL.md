---
name: graphify-code-graph
description: "This skill should be used when an agent needs to understand, navigate, or reason about a codebase through a persistent code knowledge graph instead of ad-hoc grepping: architecture recovery, onboarding onto a legacy codebase, dependency and impact analysis, \"what calls X / what does X reach\", data-flow tracing, refactoring and migration discovery (architectural hubs, hidden cross-module edges), or token-efficient repo Q&A. Trigger phrases: \"map this codebase\", \"what depends on X\", \"impact of changing Y\", \"how does Z flow through the code\", \"build a knowledge graph of the repo\", \"query the codebase\". It documents the graphify CLI (local, deterministic tree-sitter AST extraction; GraphRAG-ready graph.json) and the compliance-safe workflow. Do not use for producing the narrative technical map / bounded-context report: that is tech-analyst; this skill feeds it."
---


# Graphify Code Graph
Drive **graphify**, an MIT-licensed CLI that turns a codebase into a **persistent, queryable knowledge graph**, using the commands, workflow and guardrails below. This is a playbook, not an executor. Whichever agent holds `Bash` runs the commands.

graphify parses code **locally with tree-sitter AST**: no LLM call, no network, no upload, and no API key. It emits `graph.json` (GraphRAG-ready), `graph.html` (interactive), and `GRAPH_REPORT.md` (audit). Every edge carries an honesty tag (`EXTRACTED` / `INFERRED` / `AMBIGUOUS`) and a `source_location` (`file:line`).

Prefer graphify over grep whenever the question is **relational** ("what connects / calls / reaches") rather than a literal string match.

---

## Compliance & privacy (read first on sensitive codebases)

- **Code is safe by construction.** Tree-sitter AST extraction runs entirely on-device with zero LLM calls and nothing uploaded. A code-only run (`graphify <path>` on a repo) needs no API key and sends no code anywhere.
- **Non-code files are the risk.** Docs, PDFs, images and (where a grammar is missing) schemas are read by the configured **model backend** during semantic extraction. On corpora with secrets, credentials, or regulated data:
  - Run graphify on **code only** (point it at source directories; exclude docs/dumps), OR
  - Keep semantic extraction **on-device** with a local backend (e.g. Ollama), OR
  - Only set `GEMINI_API_KEY`/`GOOGLE_API_KEY` when the client's usage policy allows that content to reach that provider.
  - graphify reads **only** `GEMINI_API_KEY`/`GOOGLE_API_KEY` for semantic work, never `ANTHROPIC_API_KEY`/`OPENAI_API_KEY`. Never prompt for a key; a code-only run needs none.
- `detect` reports `skipped_sensitive` files. Always surface that list so a wrongly-included secret file is visible before extraction.
- **Never send raw code to an LLM out of band.** The graph (structure + `file:line`) is the artifact shared downstream, not the source.

---

## Prerequisites

```bash
uv tool install graphifyy          # PyPI package is "graphifyy" (double-y); CLI is "graphify"
graphify install --platform gemini # register the /graphify skill in Gemini CLI (or: claude, cursor, codex, ...)
graphify --version
```

`graphify --help` lists every command. If the binary is missing but `uv` is present, `uv tool install --upgrade graphifyy` restores it.

---

## Core workflow on code

```bash
graphify <path>                 # full pipeline: detect → AST extract → cluster → graph.json + graph.html + GRAPH_REPORT.md
graphify <path> --mode deep     # richer INFERRED edges (slower)
graphify <path> --update        # incremental: re-extract only changed files (SHA256 cache)
graphify <path> --directed      # preserve edge direction (source → target) — better for call/impact analysis
graphify <path> --no-viz        # skip HTML (use for > 5000-node graphs / CI)
graphify <path> --neo4j         # emit cypher for Neo4j; --neo4j-push bolt://… to load directly
graphify <path> --watch         # rebuild on save (deterministic, no LLM)
```

Outputs land in `graphify-out/`: `graph.json` (persistent: query it for weeks without rebuilding), `graph.html`, `GRAPH_REPORT.md`. On a code-only corpus the semantic (LLM) stage is skipped entirely.

**Corpus guardrail:** if `detect` reports > 2,000,000 words or > 500 files, scope to a subfolder before building (rank top subdirectories by file count) rather than graphing everything at once.

---

## Query playbook (use the existing graph, do not rebuild)

**Fast path:** if `graphify-out/graph.json` already exists and the user asks a question about the code, query it directly. Do not re-run the pipeline.

```bash
graphify query "how does authentication reach the database?"   # BFS traversal, broad context
graphify query "…" --dfs                                       # trace one specific path
graphify query "…" --budget 1500                               # cap answer tokens
graphify path "AuthModule" "Database"                          # shortest connection between two nodes
graphify explain "StaffingProfileSync"                         # node + neighborhood in plain language
graphify affected "OrderService" --depth 2                     # reverse traversal → impact set
graphify god-nodes --top 10                                    # most-connected architectural hubs
```

When citing a fact from a query, quote the node's `source_location` (`file:line`). Answer only from what the graph contains.

---

## Reading the graph honestly

- Respect edge tags: `EXTRACTED` (found in code) > `INFERRED` (derived) > `AMBIGUOUS` (uncertain). Never present an `INFERRED`/`AMBIGUOUS` edge as fact.
- `god-nodes` = architectural hubs; high degree often means a refactoring or risk hotspot.
- Communities = candidate modules/bounded contexts; use them as a starting hypothesis, not ground truth.
- Surface any `GRAPH HEALTH WARNING` (dangling/collapsed edges). Do not hide it.

---

## Limitations to flag

- **No SQL/PL-SQL tree-sitter grammar** ships by default: `.sql`/PL-SQL is not AST-parsed and would fall to the model backend (a compliance risk on sensitive schemas). For database dependencies prefer the DB data dictionary (`ALL_DEPENDENCIES`, `ALL_SOURCE`) and load the result via `--neo4j`.
- Supported code grammars include Java, Python, TypeScript/JavaScript, Go, Rust, C/C++, C#, Kotlin, Scala, Ruby, PHP, Bash and more; confirm the target language is covered before relying on AST edges.
- Large monorepos need scoping (see the corpus guardrail).

---

## Integration with the analysis pipeline

- graphify produces the **deterministic, on-device structural layer** (call graph, dependencies, `file:line`), the low, factual level of a code knowledge graph. Hand the graph and `GRAPH_REPORT.md` to `tech-analyst` for the narrative module map / bounded-context write-up; this skill does not produce that report.
- `--neo4j` export lets the same graph feed a Neo4j-based analysis (e.g. alongside jQAssistant) and GraphRAG-style querying.
