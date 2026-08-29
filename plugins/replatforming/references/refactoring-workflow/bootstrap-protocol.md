# Phase 0 — Bootstrap protocol (workflow supervisor's own bootstrap)

> Reference doc for `refactoring-supervisor`. Read at runtime when starting
> the workflow — before the first delegated phase. This is the supervisor's
> OWN bootstrap (Phase 0 of YOUR workflow), not the indexing-supervisor's
> Phase 0.

Before the first delegated phase, follow this exact sequence.

## 1. Verify repo root is a git repository

If not, ask the user.

## 2. Detect existing state — per-phase

For each phase 0..4, set
`detected = (output root exists) AND (manifest reports complete)`,
and capture key metadata to display to the user. Phases 0–3 are
detected exactly as before (their logic, structure, and outputs are
unchanged from prior versions). Phase 4 detection now includes
step-level resume awareness because the new replatforming model
has 7 steps with hard gates:

| Phase | Output root probe | Manifest probe | Metadata to display |
|---|---|---|---|
| 0 | `<repo>/.indexing-kb/` | `.indexing-kb/_meta/manifest.json` last run `complete` | module count, LOC, stack |
| 1 | `<repo>/docs/analysis/01-functional/` | `…/_meta/manifest.json` `status: complete` | actors / features / UCs counts; PDF+PPTX present? |
| 2 | `<repo>/docs/analysis/02-technical/` | `…/_meta/manifest.json` `status: complete` | risk count by severity; PDF+PPTX present? |
| 3 | `<repo>/tests/baseline/` AND `<repo>/docs/analysis/03-baseline/` | `docs/analysis/03-baseline/_meta/manifest.json` `status: complete` | tests authored / executed counts; Postman present? |
| 4 | `<repo>/docs/refactoring/` AND configured `backend/` / `frontend/` dirs | `docs/refactoring/_meta/manifest.json` `status: complete` AND `current_step == 6` AND Step 6 gate fields all green AND `po_signoff: approved` | current step (0–6); features done / total (Step 2 progress); last successful gate (build / startup / tests); replatforming-report present? PO sign-off status; validation-loop trigger count |

For each phase, if the output root exists but the manifest reports
`partial`, `failed`, `in-progress`, or is missing/unreadable: classify
as `inconsistent` (NOT a skip candidate) and surface this in step 4.

### Sub-state — exports-missing (Phases 1 and 2 only)

For phases 1 and 2, additionally check whether the Accenture-branded exports are
present on disk:

- Phase 1: `docs/analysis/01-functional/_exports/01-functional-report.pdf`
  AND `docs/analysis/01-functional/_exports/01-functional-deck.pptx`
- Phase 2: `docs/analysis/02-technical/_exports/02-technical-report.pdf`
  AND `docs/analysis/02-technical/_exports/02-technical-deck.pptx`

If the manifest reports `complete` AND **at least one** of the two
export files is missing on disk, mark the phase as
`complete-but-exports-missing`. List which file(s) are missing in
the metadata column. This sub-state unlocks the new
`regenerate-exports` option in step 5.

## 3. Read or create the workflow manifest

Read or create `<repo>/docs/refactoring/workflow-manifest.json`
(see `workflow-manifest-spec.md` for the schema).

## 4. Present the detected state to the user as a table

One row per phase, with a recommendation. Use this exact shape:

```
=== Application Replatforming workflow — detected state ===

Phase | Status                        | Detected                                       | Recommendation
------|-------------------------------|------------------------------------------------|---------------------
  0   | complete                      | .indexing-kb/ + manifest OK                    | skip (run if you want a refresh)
  1   | complete-but-exports-missing  | …01-functional/ — PDF present, PPTX missing    | regenerate-exports
  2   | partial                       | …02-technical/ — manifest=partial              | re-run recommended
  3   | absent                        | (none)                                         | run after Phase 2 — next phase
  4   | partial                       | replatforming at Step 2: 4/12 features done    | resume from Step 2 (recommended)
```

Phase 4 sub-states (replatforming-specific):

- `absent`                                       → recommend `run` (start at Step 0)
- `in-progress at step N`                        → recommend `resume from Step N`
- `failed at step N (gate not green)`            → recommend `revise` (discuss the failed gate first)
- `complete` (current_step==6 + PO sign-off)     → recommend `skip` or `re-run` for a fresh attempt

Recommendations:

- `complete`                       → recommend `skip`
- `complete-but-exports-missing`   → recommend `regenerate-exports` (Phases 1 and 2 only)
- `inconsistent`                   → recommend `re-run` (do not auto-resume from broken state)
- `absent`                         → recommend `run`
- first incomplete                 → marked as the **next phase** in the table

## 5. Ask explicitly, per phase that is not `absent`, what to do

This is the HITL prompt the user requires. Do not proceed with
"skip what's complete" silently — ask for every detected phase. Use
this exact shape:

```
=== Per-phase decisions ===

Phase 0 (indexing) is COMPLETE in this repo.
  What should I do?
    [skip]    keep existing .indexing-kb/, do not dispatch indexing-supervisor
    [re-run]  overwrite (you'll get an overwrite confirmation from the phase supervisor)
    [revise]  inspect a specific section together first

Phase 1 (functional-analysis) is COMPLETE BUT EXPORTS ARE MISSING in this repo.
  Missing: <list of missing export files>
  What should I do?
    [regenerate-exports]  dispatch functional-analysis-supervisor in
                           `exports-only` resume mode — runs ONLY the
                           export wave (document-creator + presentation-creator),
                           reusing the existing analysis. Fast, no W1/W2/W3
                           re-run.
    [skip]                keep existing analysis, accept that the export(s)
                           are missing
    [re-run]               re-run the full pipeline from W1 (overwrites the
                           existing analysis)
    [revise]               inspect together first

Phase 2 (technical-analysis) is COMPLETE in this repo.
  What should I do?
    [skip] / [re-run] / [revise]
    (also [regenerate-exports] if exports are missing)

…repeat for every phase whose status is complete or inconsistent…

Phase 3 (baseline-testing) is the next phase to run.
  What should I do?
    [run]     dispatch baseline-testing-supervisor as planned
    [defer]   stop the workflow here

```

The `regenerate-exports` choice is offered ONLY for phases 1 and 2,
and ONLY when the phase is in sub-state `complete-but-exports-missing`.
For all other phases / states, the choices remain skip / re-run / revise
(or run / defer for the next phase).

Default deny: do not proceed without an explicit per-phase answer.
The user may answer all at once ("skip 0, regenerate-exports 1, skip 2,
run 3, defer 4"), or one at a time. Echo back the consolidated plan
before moving on.

## 6. Determine the effective phase plan from the user's answers

- phases marked `skip` → not dispatched; their outputs are assumed
  valid. They count as `complete` in the workflow manifest.
- phases marked `regenerate-exports` (Phases 1 and 2 only) →
  dispatched with the option `resume_mode: exports-only` in the
  prompt. The phase supervisor will detect this, skip its W1/W2/W3
  waves, and dispatch ONLY the export wave for the missing file(s).
  Existing analysis under `docs/analysis/0N-*` is treated as the
  source of truth and is not modified. Faster than `re-run`.
- phases marked `re-run` → dispatched in order; the phase supervisor
  handles overwrite confirmation for its own outputs (`docs/`,
  `tests/`, `backend/`, `frontend/`, `_exports/`).
- phases marked `revise` → pause workflow, discuss with user, do
  not dispatch the supervisor. Resume after revision.
- the first `run` phase is the workflow's starting point; subsequent
  phases follow the standard per-phase protocol.

## 7. Present the consolidated workflow plan to the user

- per-phase decision (skip / re-run / revise / run / defer; for
  Phase 4: also the resume-from-step option)
- which phases are supported in this workflow today
- explicit reminder: "Phase 5 onwards is not yet implemented; the
  previous standalone Phase 5 (TO-BE Testing & Equivalence
  Verification) has been absorbed into Phase 4 Step 6 in v3.0.0"

## 8. Wait for one final confirmation

Wait before delegating the first phase marked `run` or `re-run`.

---

Bootstrap confirmation is non-negotiable, even if the user has said
"do everything". The per-phase prompt in step 5 is also non-negotiable
when at least one phase is detected as `complete` or `inconsistent` —
the user has explicitly required visibility on what is being skipped.

If the user requests `--no-resume-prompt` or "just start fresh from
Phase 0": treat all detected phases as `re-run` candidates (still
prompt the phase supervisors for their own overwrite confirmations on
existing outputs).
