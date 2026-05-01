# Phase 1 — Phase plan (Phase 0 bootstrap + Wave 1–3 + Export Wave + final report)

> Reference doc for `functional-analysis-supervisor`. Read at runtime to drive the bootstrap dialog, dispatch each wave, and produce the closing report.

## Phase 0 — Bootstrap (supervisor only, no sub-agents)

1. Verify `.indexing-kb/` exists and contains at minimum:
   - `00-index.md` or `01-overview.md`
   - `02-structure/` and `04-modules/`
   - `06-data-flow/` (any of database/file-io/external-apis/configuration)
   - `07-business-logic/` (any of domain/validation/business-rules)
   If any of these is missing, stop and ask the user.
2. Read `.indexing-kb/00-index.md`, `01-overview.md`, `08-synthesis/bounded-contexts.md` (if present) to build a mental map.
3. **Detect stack mode** by reading the canonical AS-IS stack manifest at `.indexing-kb/02-structure/stack.json` (produced by Phase 0 `codebase-mapper`). The supervisor uses these fields:
   - `stack.primary_language` — drives language-specific guidance (Python/Java/Kotlin/Go/Rust/C#/Ruby/PHP/TypeScript/JavaScript/...)
   - `stack.frameworks` — drives framework-conditional adjustments (e.g. `streamlit` → page-as-screen + reactive-rerun guidance; `rails`/`laravel`/`django`/`spring-mvc` → request-per-screen + MVC conventions; `angular`/`react`/`vue`/`qwik`/`nextjs`/`tanstack-start` → SPA / file-based-routing screens)
   - `stack.confidence` — if `low`, surface to the user before proceeding

   If `.indexing-kb/02-structure/stack.json` is missing (Phase 0 from a pre-PR-02 run): fall back to a quick check of `.indexing-kb/05-streamlit/` (legacy Streamlit detection) and `01-overview.md` hints (CLI? web service? batch? library?). If still unclear, ask the user. The framework-conditional block already handles "no framework" gracefully.
4. Read `docs/analysis/01-functional/_meta/manifest.json` if it exists (resume support).
5. **Detect resume mode**. Inspect what is on disk and pick one of:

   | Condition | Resume mode |
   |---|---|
   | No `docs/analysis/01-functional/` | `fresh` |
   | Manifest reports `partial` / `failed` / missing while output dir exists | `resume-incomplete` |
   | Manifest reports `complete` AND **both** `_exports/01-functional-report.pdf` AND `_exports/01-functional-deck.pptx` exist | `complete` (default = nothing to do; ask user whether to refresh) |
   | Manifest reports `complete` AND **at least one of** the export files is missing | `exports-only-eligible` — offer the user the option to dispatch ONLY the export wave |
   | Manifest reports `complete` AND user explicitly asked for a refresh | `full-rerun` |

   When `exports-only-eligible` triggers, ask the user verbatim:

   ```
   The functional analysis at docs/analysis/01-functional/ is complete,
   but the following Accenture-branded export(s) are missing:
     - <list missing files>

   What should I do?
     [exports-only]  regenerate only the missing export(s), reusing the
                     existing analysis. Fast — does not re-run any of
                     the W1/W2/W3 sub-agents.
     [full-rerun]    re-run the full pipeline from W1 (overwrites the
                     existing analysis; you'll get an explicit
                     overwrite confirmation).
     [skip]          do nothing, leave the analysis as-is without the
                     missing export(s).
   ```

   Default recommendation: `exports-only`. Do not proceed without an explicit answer.

6. Determine **challenger default**:
   - **Implicit-logic-heavy stacks** → challenger ON by default. These are stacks where significant business logic is interleaved with UI or framework callbacks and is hard to surface from static analysis alone:
     - `streamlit` (script-as-page reactive rerun model)
     - any future stack flagged in `claude-catalog/docs/language-agnostic-design.md` as implicit-logic-heavy
   - Other stacks → challenger OFF unless user opts in with `--challenger` or "include challenger pass"
   (Skipped in `exports-only` mode — the challenger has already run in the original pipeline if it was enabled then.)
7. Check exports:
   - If resume mode is `exports-only`: skip this step; the export wave itself will overwrite only the missing file(s) (existing files are kept untouched).
   - Else if `_exports/01-functional-report.pdf` or `_exports/01-functional-deck.pptx` already exist → **ask the user explicitly** whether to overwrite. Do not silently overwrite. Choices: `overwrite`, `keep` (skip export wave), `rename` (append timestamp suffix).
8. Write `00-context.md` with:
   - 1-paragraph system summary derived from `01-overview.md`
   - Scope: what is in / out of analysis
   - Stack info (verbatim from `02-structure/stack.json`): `primary_language`, `languages[]`, `frameworks[]`, `confidence`
   - Source KB pointer
   - Resume mode
   - Challenger setting
   - Export overwrite decision
   In `exports-only` mode, do NOT overwrite an existing `00-context.md` from the prior run — append a `## Re-run note` block at the bottom that records the date and which files were regenerated.
9. **Present the plan to the user**:
   - resume mode, scope, stack mode, challenger setting, export policy, expected outputs
   - ask for confirmation before dispatching any sub-agent

Skip Phase 0 confirmation only if the user has explicitly said "go ahead, do the whole pipeline" in the same conversation — and even then, post the plan and wait at least one turn before dispatch unless the user repeats "proceed".

> **Resume-mode shortcut**: if bootstrap chose `exports-only`, skip Waves 1, 1.5, 2, and 3 entirely. Jump directly to the Export Wave below — that is the whole point of `exports-only`. The existing analysis in `docs/analysis/01-functional/` is treated as the source of truth and is not modified.

## Wave 1 — Discovery (parallel, single message with multiple Agent calls)

Dispatch in parallel:
- `actor-feature-mapper`
- `ui-surface-analyst`
- `io-catalog-analyst`

After dispatch, read all outputs from disk. Verify:
- expected files exist and have valid frontmatter
- no sub-agent wrote outside `docs/analysis/01-functional/`
- no contradictions on shared concepts (e.g., a screen mentioned by ui-surface-analyst that doesn't exist in `.indexing-kb/05-streamlit/pages.md`)

If any sub-agent reports `status: needs-review` or `confidence: low` on a foundational deliverable (actors, features, UI map): surface to the user **before Wave 2**. Wave 2 depends on these.

## Wave 1.5 — Human-in-the-loop checkpoint

Present to the user:
- list of identified actors (with confidence)
- feature map (with screens-per-feature counts)
- UI map (high-level)
- any blocking unresolved items

Ask: "Proceed to Wave 2 (use cases, flows, implicit logic), revise Wave 1 outputs, or stop?"

This checkpoint is non-negotiable when Wave 1 produced ≥ 1 `blocked` item or ≥ 3 `low` confidence items. Otherwise it is recommended but skippable if the user has set `--no-checkpoint`.

## Wave 2 — Behavior (parallel, single message)

Dispatch in parallel:
- `user-flow-analyst` (depends on actors + features + UI map from W1)
- `implicit-logic-analyst` (depends on UI map + IO catalog from W1)

Both sub-agents are passed the paths of the W1 outputs they depend on, plus the relevant `.indexing-kb/` sections. Pass paths, not contents.

After dispatch, read outputs. Aggregate `## Open questions` sections from all sub-agents (W1 + W2) into `14-unresolved-questions.md`.

## Wave 3 — Synthesis (sequential, supervisor only)

The supervisor produces three artifacts directly (no sub-agent):

1. **`13-traceability.md`** — generated mechanically:
   - parse all per-item frontmatter from W1+W2 outputs
   - build matrices: Actor × Feature, Feature × Screen, Feature × UC, UC × Input/Output, Screen × ImplicitLogic
   - flag orphans (e.g., feature without UC, input without transformation)

2. **`14-unresolved-questions.md`** — final aggregation, grouped by source sub-agent and severity (blocking / needs-review / nice-to-have).

3. **`README.md`** — entry point with navigation links and reading order.

If `00-context.md` says challenger is ON → dispatch `functional-analysis-challenger` after the three artifacts above are written. The challenger reads the full set of outputs and produces `_meta/challenger-report.md` plus appends entries to `14-unresolved-questions.md` under a `## Challenger findings` section.

## Export Wave — Always ON (parallel, single message)

After Wave 3 completes (and the challenger, if it ran), dispatch in parallel:
- `document-creator` → `_exports/01-functional-report.pdf`
- `presentation-creator` → `_exports/01-functional-deck.pptx`

In `exports-only` resume mode, dispatch ONLY the generators whose output file is missing on disk. Existing export files are kept untouched. If both files exist, the supervisor should not have reached this wave in `exports-only` mode (bootstrap step 5 would have classified the run as `complete`, not `exports-only-eligible`).

Both agents are passed paths to the entire `docs/analysis/01-functional/` tree as source. Audience and content shape:

- `document-creator` produces a **functional reference PDF** for the business-side stakeholders and the receiving delivery team. It consolidates: system context (`00-context.md`), actor map, feature catalogue, UI map + screens, full use-case set (`06-use-cases/`), user flows + sequence diagrams, I/O catalogue, implicit logic, traceability matrix, and the open-questions register. Sequence diagrams must be rendered (Mermaid). Accenture-branded.

- `presentation-creator` produces an **executive functional deck** for steering committee. Suggested skeleton (the agent has the full source and may adjust):
  - 1: Title + system one-liner
  - 2: Scope, actors at a glance
  - 3: Feature map (top-level groups)
  - 4: Top user journeys (one slide per top journey, ≤ 5)
  - 5: Coverage stats (counts of actors, features, screens, UCs)
  - 6: Open questions / risks (from `14-unresolved-questions.md`)
  - 7: Recommended next steps
  Accenture-branded.

If the export overwrite decision in bootstrap was `keep` → skip this wave and note in the final recap.

If either generator fails: do not block Phase 1 completion; mark the export as failed in the manifest and surface in the recap. The markdown analysis under `docs/analysis/01-functional/` is the primary deliverable; exports are a value-add view on top of it.

After the export wave, verify both files exist on disk under `_exports/`. Do not trust the Agent tool result text alone.

## Wave 3.5 — Final report

Post a final user-facing summary:

```
Phase 1 Functional Analysis — complete.

Output: docs/analysis/01-functional/
Entry:  docs/analysis/01-functional/README.md

Exports:
- PDF:  docs/analysis/01-functional/_exports/01-functional-report.pdf
- PPTX: docs/analysis/01-functional/_exports/01-functional-deck.pptx
  (or "skipped" / "failed" with reason)

Coverage:
- Actors:   <N>
- Features: <N>
- Screens:  <N>
- UCs:      <N>
- I/O:      <N inputs>, <N outputs>, <N transformations>
- Implicit logic items: <N>

Quality:
- Open questions: <N> (see 14-unresolved-questions.md)
- Low-confidence sections: <N>
- Challenger findings: <N> (or "challenger not run")

Recommended next: review 14-unresolved-questions.md before proceeding to
later phases of the workflow.
```
