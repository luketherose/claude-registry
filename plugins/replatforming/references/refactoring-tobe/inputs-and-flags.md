# Inputs and bootstrap flags — Phase 4

> Reference doc for `refactoring-tobe-supervisor`. Read at runtime
> during Phase 0 bootstrap to validate inputs and parse user-supplied
> flags.

## Required inputs

| Path | Source phase | Used for |
|---|---|---|
| `<repo>/.indexing-kb/` | Phase 0 | system overview, glossary, hot paths |
| `<repo>/docs/analysis/01-functional/` | Phase 1 | UC catalogue, business processes |
| `<repo>/docs/analysis/02-technical/` | Phase 2 | code quality, hotspots, dependency graph |
| `<repo>/tests/baseline/` and `<repo>/docs/analysis/03-baseline/` | Phase 3 | traceability + equivalence reference |

If any required Phase 0–3 input is missing or carries `status: failed`,
**stop and ask the user**: offer to run the missing phase first or
abort.

If Phase 3 reports unresolved `critical` AS-IS bugs, **stop and ask**:
the user must decide whether to defer those bugs to Phase 5 (document
in TO-BE as known limitations) or pause Phase 4 for a fix-cycle.

## Optional inputs

- Prior partial outputs in `.refactoring-kb/`, `docs/refactoring/`,
  `backend/`, `frontend/` (resume support).

## Optional flags

| Flag | Default | Alternatives |
|---|---|---|
| `--mode` (Q1) | `A` | `B` (per-BC milestone) |
| `--code-scope` (Q2) | `scaffold-todo` | `full`, `structural` |
| `--verify` (Q3) | `auto` | `on`, `off` |
| `--review-mode` (Q4) | `background` | `sync`, `off` |
| `--with-exports` | OFF | opt-in for PDF + PPTX of roadmap |
| `--target-backend-dir <path>` | `<repo>/backend/` | any writable path |
| `--target-frontend-dir <path>` | `<repo>/frontend/` | any writable path |

For full descriptions of Q1–Q4, the bootstrap recommendation
heuristics, and the decision logic, see
[`iteration-and-scope-modes.md`](iteration-and-scope-modes.md).

For the full TO-BE output directory tree and frontmatter contract every
worker must respect, see [`output-layout.md`](output-layout.md).
