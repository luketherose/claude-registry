# Phase 2 — Sub-agents roster & phase plan

> Reference doc for `technical-analysis-supervisor`. Read at runtime when planning the wave sequence — what agents exist, which wave they belong to, where they write, and what each step blocks.

## Sub-agents available (Sonnet)

| Sub-agent | Wave | Output target |
|---|---|---|
| `code-quality-analyst` | W1 | `01-code-quality/` |
| `state-runtime-analyst` | W1 | `02-state-runtime/` |
| `dependency-security-analyst` | W1 | `03-dependencies-security/`, `_meta/dependencies.json` |
| `data-access-analyst` | W1 | `04-data-access/` |
| `integration-analyst` | W1 | `05-integrations/` |
| `performance-analyst` | W1 | `06-performance/` |
| `resilience-analyst` | W1 | `07-resilience/` |
| `security-analyst` | W1 | `08-security/` |
| `risk-synthesizer` | W2 | `09-synthesis/`, `_meta/risk-register.{json,csv}` |
| `technical-analysis-challenger` | W3 (always ON) | `_meta/challenger-report.md`, appends to `14-unresolved-questions.md` |

External agents called in the export wave (already published):

- `document-creator` → `_exports/02-technical-report.pdf`
- `presentation-creator` → `_exports/02-technical-deck.pptx`

## Phase plan (overview)

| Step | Wave | Mode | Dispatched agents | Blocks |
|---|---|---|---|---|
| Phase 0 | Bootstrap | supervisor only | — | all waves until confirmed |
| W1 | Discovery | per `--mode` (parallel / batched / sequential) | 8 W1 analysts | W2 |
| W1.5 | HITL checkpoint | user confirm | — | W2 |
| W2 | Synthesis | sequential, single | `risk-synthesizer` | W3 |
| W3 | Challenger | always ON | `technical-analysis-challenger` | export wave / completion |
| Export | Always ON | parallel | `document-creator` + `presentation-creator` | — |
| Recap | — | supervisor only | — | end |

For the full per-wave dispatch instructions, the bootstrap dialog (incl. the `exports-only` resume mode), the HITL checkpoint prompts, and the closing-report schema, see [`phase-plan.md`](./phase-plan.md). For the W1 dispatch decision tree and the batching plan, see [`dispatch-mode.md`](./dispatch-mode.md). For the worker prompt boilerplate (incl. Streamlit-aware adjustments), see [`dispatch-prompt-template.md`](./dispatch-prompt-template.md).
