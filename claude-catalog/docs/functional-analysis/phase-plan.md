# Phase 1 — Phase plan (Phase 0 bootstrap + Wave 1–3 + Wave 3c narrative + Wave 3d verification + Export Wave)

> Reference doc for `functional-analysis-supervisor`. Read at runtime to drive the bootstrap dialog, dispatch each wave, produce the human-readable feature narrative, write the phase verification report, and (on `approve`) regenerate the exports.
>
> **Iteration loop.** Phase 1 ends with the HITL iteration loop documented in [`refactoring-workflow/iteration-loop.md`](../refactoring-workflow/iteration-loop.md). The functional analysis is the most delicate part of the workflow — a misunderstanding here propagates everywhere downstream — so the loop allows unbounded iterations until the user picks `approve`. See § "Wave 4 — Iteration handling" below.

## Phase 0 — Bootstrap (supervisor only, no sub-agents)

1. Verify `.indexing-kb/` exists and contains at minimum:
   - `00-index.md` or `01-overview.md`
   - `02-structure/` and `04-modules/`
   - `06-data-flow/` (any of database/file-io/external-apis/configuration)
   - `07-business-logic/` (any of domain/validation/business-rules)
   If any of these is missing, stop and ask the user.
2. Read `.indexing-kb/00-index.md`, `01-overview.md`, `08-synthesis/bounded-contexts.md` (if present) to build a mental map.
3. **Detect stack mode** by reading the canonical AS-IS stack manifest at `.indexing-kb/bronze/stack.json` (produced by Phase 0 `codebase-mapper`). The supervisor uses these fields:
   - `stack.primary_language` — drives language-specific guidance (Python/Java/Kotlin/Go/Rust/C#/Ruby/PHP/TypeScript/JavaScript/...)
   - `stack.frameworks` — drives framework-conditional adjustments (e.g. `streamlit` → page-as-screen + reactive-rerun guidance; `rails`/`laravel`/`django`/`spring-mvc` → request-per-screen + MVC conventions; `angular`/`react`/`vue`/`qwik`/`nextjs`/`tanstack-start` → SPA / file-based-routing screens)
   - `stack.confidence` — if `low`, surface to the user before proceeding

   If `.indexing-kb/bronze/stack.json` is missing (Phase 0 from a pre-PR-02 run): fall back to a quick check of `.indexing-kb/05-streamlit/` (legacy Streamlit detection) and `01-overview.md` hints (CLI? web service? batch? library?). If still unclear, ask the user. The framework-conditional block already handles "no framework" gracefully.
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

**Wave 3b — functional-traceability-auditor (always ON)**
Dispatch after Wave 3 (challenger) completes (or after Wave 2 if challenger is disabled).
The auditor runs three passes: (1) traceability audit — every confirmed UC has evidence_ids; (2) negative space audit — UI files without UC, routes without feature; (3) AS-IS purity audit — no TO-BE references in outputs.
Read outputs from disk: `normalized/functional-traceability-audit.json` and `_meta/functional-traceability-report.md`.
If verdict is FAIL, do NOT declare Phase 1 complete — escalate to user.

**Gap closure loop (before HITL)**
1. Check if `validate_functional_analysis.py` exists in `.github/scripts/`; if so, run it.
2. Read `normalized/functional-traceability-audit.json` for verdict.
3. If FAIL: identify which gaps are auto-fixable (e.g., missing `status` field on a UC can be set to `requires_human_confirmation`); attempt fix via targeted sub-agent re-dispatch.
4. Surface all residual gaps to the user in the HITL summary.

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

## Wave 3c — Feature narrative (supervisor only)

After Wave 3b and before the Export Wave, the supervisor writes the
human-readable feature narrative at `00b-feature-narrative.md`. This
is the entry-point document for human review. Canonical structure
and hard rules in [`output-layout.md`](./output-layout.md#the-feature-narrative--00b-feature-narrativemd).

Inputs the supervisor reads:

- `00-context.md` — for the headline paragraph.
- `02-features.md` — for the F-NN list and feature titles.
- `06-use-cases/UC-NN-<slug>.md` — for the per-feature flows.
- `03-ui-map.md` and `04-screens/` — for the "What the user sees"
  subsection of each chapter.
- `09-inputs.md`, `10-outputs.md`, `11-transformations.md` — for the
  "Outputs and side effects" subsection.
- `12-implicit-logic.md` — for unusual rules visible inside a
  feature's flow.
- `14-unresolved-questions.md` — to surface inline per-feature.

Output: `00b-feature-narrative.md`, written by the supervisor in a
single `Write` call. The supervisor must:

- write one chapter per F-NN (or one chapter per group of thin F-NNs,
  see hard rules in output-layout);
- keep prose plain — no class names, no code, no Mermaid;
- reference every UC, S, A, IN, OUT, TR by stable ID;
- surface open questions inline in each affected feature chapter.

This wave is mandatory. Skipping it produces a partial Phase 1 (and
the verification report flags the omission).

## Wave 3d — Phase verification report (supervisor only)

After Wave 3c, the supervisor writes the verification report at
`_meta/phase-verification-report.md` per the canonical structure in
[`refactoring-workflow/phase-verification-report.md`](../refactoring-workflow/phase-verification-report.md).

The Phase-1 customization of the canonical structure:

| Section | Phase 1 source |
|---|---|
| 1. Executive summary | Manifest counts + `00-context.md` + the auditor verdicts. 2–3 paragraphs. |
| 2. What was produced | `00b-feature-narrative.md` chapters (list features), `02-features.md`, `06-use-cases/` (count by status), `03-ui-map.md` + `04-screens/`, `09-inputs.md` + `10-outputs.md`, `12-implicit-logic.md`. |
| 3. What changed since iteration N-1 | Read `_meta/iteration-log.jsonl` for the latest entry; list adjustments applied, sub-agents re-dispatched, deliberation traces consulted. Omit on iteration 1. |
| 4. Open questions and gaps | `14-unresolved-questions.md` + `normalized/functional-gaps.jsonl`. Group by severity. |
| 5. Audit verdicts | `_meta/functional-traceability-report.md` (always) + `_meta/challenger-report.md` (if ran). |
| 6. AS-IS purity check | Drift scan across all newly written files for this iteration; tokens from the Phase 2 drift list. |
| 7. What to verify | At minimum: read `00b-feature-narrative.md` end-to-end; review UCs marked `requires_human_confirmation` or `candidate_not_confirmed`; review blocking open questions. |
| 8. Recommendation | `approve` only if all verdicts PASS and no blocking issues; `iterate` otherwise. |

The verification report is the document presented to the user before
the iteration-loop prompt (§ "Wave 4 — Iteration handling" below).

## Export Wave — gated on `approve`

The Export Wave (PDF + PPTX via `document-creator` + `presentation-creator`)
no longer runs unconditionally at the end of every iteration. It runs:

- on `approve` from the iteration loop (Step F branch `approve` in the
  per-phase protocol), to produce the deliverable for stakeholders
  reflecting the approved state, OR
- on `Resume mode: exports-only` when an existing approved analysis
  has missing exports (no change to existing behaviour).

During iterations 1..N-1 (before approval) the exports are not
regenerated. This avoids the cost and risk of producing a deliverable
PDF that does not reflect the final user-approved state.

The wave itself is unchanged — same dispatchers, same inputs, same
Accenture branding. The only change is its trigger.

## Wave 4 — Iteration handling (supervisor only)

After Wave 3d the supervisor returns control to `refactoring-supervisor`
for the HITL iteration prompt (per-phase protocol Step F). The
workflow supervisor surfaces the verification-report path and asks
`approve / iterate / stop`.

If the user picks **`approve`**: the Phase 1 supervisor regenerates
the exports (above) and the workflow advances.

If the user picks **`iterate`**: the workflow supervisor captures the
adjustment delta and re-dispatches the Phase 1 supervisor with
`Resume mode: iterate` and the delta JSON path. The Phase 1
supervisor:

1. Reads the delta from `_meta/iteration-log.jsonl` (latest record).
2. Snapshots the current outputs to `_meta/snapshots/iter-<K>/`
   before any overwrite.
3. Decides which sub-agents to re-dispatch based on the adjustment
   `target_artifacts` and `target_ids`. The re-dispatch mapping:

   | Adjustment target | Sub-agents to re-dispatch |
   |---|---|
   | actor scope / actor IDs (A-NN) | actor-feature-mapper → user-flow-analyst (downstream) |
   | feature scope / feature IDs (F-NN) | actor-feature-mapper → user-flow-analyst, narrative wave |
   | UI / screens (S-NN) | ui-surface-analyst → user-flow-analyst |
   | UC flows (UC-NN) | user-flow-analyst (re-run) |
   | I/O catalogue (IN-/OUT-/TR-NN) | io-catalog-analyst → narrative wave |
   | implicit logic (IL-NN) | implicit-logic-analyst |
   | scope-of-iteration dispute | route to deliberative-decision-engine first; then re-decide |

4. Injects the user delta as a "User feedback from prior iteration"
   block into the dispatch prompt of every re-dispatched sub-agent
   (the template in `dispatch-prompt-template.md` accepts this block).
5. Re-runs Wave 3 (synthesis + 14-traceability + 14-unresolved),
   Wave 3b (auditor), Wave 3c (narrative), Wave 3d (verification
   report). The challenger re-runs only if the user requested it OR
   if `> 30%` of the artifacts changed in this iteration.
6. Returns control to the workflow supervisor for the next HITL
   prompt.

If the user picks **`stop`**: the workflow supervisor updates the
manifest with `status: partial` and ends the workflow. The Phase 1
supervisor does no further work.

### Manifest update for iterations

Every iteration appends a new entry to `manifest.json` `runs[]`:

```json
{
  "run_id": "<ISO-8601>",
  "iteration": <K>,
  "trigger": "fresh | iterate | exports-only | full-rerun",
  "delta_ref": "_meta/iteration-log.jsonl#<line>",  // if iterate
  "waves": [ ... ],
  "deliberation_traces": ["<trace-id>", ...],         // if any
  "status": "complete | partial | failed",
  "approved_at": null | "<ISO-8601>"                  // set only on approve
}
```

The `approved_at` field is set only when the user picks `approve` —
not on individual iteration completion. This is the signal that the
phase is locked from further iteration.

## Closing summary (compatibility shim)

The closing summary block that older callers expect is now produced as
part of the verification report's section 1 ("Executive summary"). The
old free-text "Phase 1 completed" block is no longer emitted by the
supervisor — the verification report supersedes it.
