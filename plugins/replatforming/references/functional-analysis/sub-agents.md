# Phase 1 — Sub-agents roster & phase plan

> Reference doc for `functional-analysis-supervisor`. Read at runtime when planning the wave sequence — what agents exist, which wave they belong to, where they write, and what each step blocks.

## Sub-agents available (Sonnet)

| Sub-agent | Wave | Output target |
|---|---|---|
| `actor-feature-mapper` | W1 | `01-actors.md`, `02-features.md` |
| `ui-surface-analyst` | W1 | `03-ui-map.md`, `04-screens/*.md`, `05-component-tree.md` |
| `io-catalog-analyst` | W1 | `09-inputs.md`, `10-outputs.md`, `11-transformations.md` |
| `user-flow-analyst` | W2 | `06-use-cases/UC-*.md`, `07-user-flows.md`, `08-sequence-diagrams.md` |
| `implicit-logic-analyst` | W2 | `12-implicit-logic.md` |
| `functional-analysis-challenger` | W3 (opt-in) | `_meta/challenger-report.md`, appends to `14-unresolved-questions.md` |

External agents called in the export wave (already published):

- `document-creator` → `_exports/01-functional-report.pdf`
- `presentation-creator` → `_exports/01-functional-deck.pptx`

## Phase plan (overview)

| Step | Wave | Mode | Dispatched agents | Blocks |
|---|---|---|---|---|
| Phase 0 | Bootstrap | supervisor only | — | all waves until confirmed |
| W1 | Discovery | parallel, single message | `actor-feature-mapper` + `ui-surface-analyst` + `io-catalog-analyst` | W2 |
| W1.5 | HITL checkpoint | user confirm | — | W2 |
| W2 | Behavior | parallel, single message | `user-flow-analyst` + `implicit-logic-analyst` | W3 |
| W3 | Synthesis | sequential, supervisor only (+ challenger if ON) | (you) + `functional-analysis-challenger` (opt-in) | export wave |
| Export | Always ON | parallel | `document-creator` + `presentation-creator` | — |
| Recap | — | supervisor only | — | end |

For the full per-wave dispatch instructions, the bootstrap dialog (incl. the `exports-only` resume mode and challenger-default heuristic), the HITL checkpoint prompts, and the closing-report schema, see [`phase-plan.md`](./phase-plan.md). For the worker prompt boilerplate (incl. framework-conditional adjustment blocks like the Streamlit one), see [`dispatch-prompt-template.md`](./dispatch-prompt-template.md). For the output directory layout, frontmatter contract, and `_meta/manifest.json` schema, see [`output-layout.md`](./output-layout.md).
