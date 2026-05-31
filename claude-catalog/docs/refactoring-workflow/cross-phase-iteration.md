# Cross-phase iteration

> Reference doc for `refactoring-supervisor`. Read when the Workflow Retrospective
> routes to `iterate` — i.e., when issues at one or more analysis phases require
> re-running those phases and all downstream phases through Phase 4.
>
> Cross-phase iteration is the workflow-level analog of the per-phase iteration loop
> in `iteration-loop.md`. While the per-phase loop re-runs one phase in isolation,
> cross-phase iteration re-runs a contiguous block of phases (Phase N through Phase 4)
> in a single orchestrated pass, carrying the retrospective delta forward to each
> affected phase supervisor.

## Entry point calculation

The re-entry phase is the earliest phase that contains at least one `open` blocking
or high issue (direct or via downstream cascade):

```
earliest_phase = min(
  issues where severity in [blocking, high] and status == open
  → union(phase, downstream_impact phases)
  → filter(>= phase-1)       # Phase 0 re-run is a separate scope change
)
```

Phase 0 is excluded from cross-phase re-entry. If Phase 0 indexing is identified
as the root cause, the supervisor escalates to the user: "This requires re-running
Phase 0 (re-indexing). That is a separate workflow invocation — confirm?" Phase 0
re-indexing wipes the KB and is irreversible without git history.

**Re-entry mapping to Phase 4 scope:**

| Earliest re-entry phase | Phase 4 re-run scope |
|---|---|
| Phase 1 or Phase 2 | Full Phase 4 re-run from Step 0 (architecture may change) |
| Phase 3 only | Phase 4 from Step 6 only (re-validate against new baseline) |
| Phase 4 only | Phase 4 from the earliest affected step (determined from issue evidence) |

## Delta schema

The cross-phase delta is written to
`docs/refactoring/_meta/cross-phase-delta-iter<N>.json` before dispatching any
phase:

```json
{
  "iteration": <N>,
  "generated_at": "<ISO-8601>",
  "retrospective_ref": "docs/refactoring/retrospective.md",
  "reentry_phase": "phase-1",
  "phase_4_rerun_scope": "full | step-6-only | from-step-N",
  "phases": [
    {
      "phase": "phase-1",
      "adjustments": [
        {
          "adjustment_id": "XADJ-NN",
          "source_issue": "RETRO-01",
          "target_artifacts": ["<path>"],
          "target_ids": ["UC-07"],
          "kind": "correction | addition | removal | clarification | re-scope",
          "summary": "<one-line>",
          "rationale": "<from retrospective finding>"
        }
      ]
    },
    {
      "phase": "phase-2",
      "adjustments": [ ... ]
    }
  ]
}
```

Each phase entry lists only the adjustments that the supervisor of that phase must
apply. Adjustments for downstream phases are derived automatically by the workflow
supervisor (e.g., if Phase 1 adds a new actor, Phase 2 may need to add technical
findings for that actor's system interactions).

## Archive policy

Before overwriting any phase output, the supervisor archives the existing state:

```
docs/analysis/01-functional/  →  docs/analysis/01-functional-archive-iter<N>/
docs/analysis/02-technical/   →  docs/analysis/02-technical-archive-iter<N>/
tests/baseline/               →  tests/baseline-archive-iter<N>/
backend/   frontend/          →  backend-archive-iter<N>/  frontend-archive-iter<N>/
```

Archives are NOT deleted. They serve as rollback targets if the user wants to revert
to a prior state. The workflow manifest records the archive paths in its `phases[]`
entries.

Do NOT archive `.indexing-kb/` — it is Phase 0's artifact and is not re-run.

## Execution protocol

After archive and user confirmation, the supervisor runs the following sequence
(same HITL gates as a fresh workflow run):

```
For each phase P from reentry_phase to phase-4 (inclusive):
  1. Read the per-phase adjustments from the cross-phase delta.
  2. If adjustments for P are empty: dispatch P in its normal resume mode
     (the phase may still need to re-run to consume changed inputs from P-1).
  3. If adjustments for P are non-empty: dispatch P with `Resume mode: iterate`,
     passing the delta path. The phase supervisor applies the adjustments per its
     own phase plan (same mechanism as the per-phase iteration loop).
  4. Follow Steps A → F of `per-phase-protocol.md` for phases 1–3.
  5. For Phase 4: use the `phase_4_rerun_scope` from the delta:
     - `full` → run Phase 4 from Step 0 (after archiving backend/ frontend/)
     - `step-6-only` → run Phase 4 from Step 6 (existing code preserved)
     - `from-step-N` → run Phase 4 from Step N (existing code partially preserved)
  6. Per-phase iteration loop (approve / iterate / stop) is active for phases 1–3
     as usual. The cross-phase iteration does not bypass per-phase HITL.
```

**Hard rule:** The supervisor MUST NOT skip a phase in the re-run range even if its
inputs appear unchanged. Each phase must re-validate its outputs given the new
upstream artifacts.

## Phase 4 re-run — artifact reuse

When `phase_4_rerun_scope` is `step-6-only` (Phase 3 change only):
- The existing `backend/` and `frontend/` code is preserved.
- Step 6 re-runs the full test suite and compares against the new Phase 3 baseline.
- If tests now fail that previously passed, the Step 3 sub-loop is triggered.
- The `01-replatforming-report.md` is re-generated to reflect the new baseline.

When `phase_4_rerun_scope` is `full` (Phase 1 or 2 change):
- Existing `backend/` and `frontend/` are archived (see Archive policy above).
- Phase 4 runs from Step 0 — the architecture may be different.
- Exception: if the user confirms "the existing code is still valid — only update the
  documentation artifacts", the supervisor accepts and runs Phase 4 Step 6 only,
  plus updates the replatforming report.

## State management

Throughout the cross-phase iteration:

- `docs/refactoring/workflow-manifest.json` is updated after every phase with the
  cross-phase iteration number in a new `cross_phase_iterations[]` array:
  ```json
  "cross_phase_iterations": [
    {
      "iteration": 1,
      "started_at": "<ISO-8601>",
      "reentry_phase": "phase-1",
      "delta_file": "docs/refactoring/_meta/cross-phase-delta-iter1.json",
      "completed_at": "<ISO-8601>",
      "status": "complete | in-progress | failed"
    }
  ]
  ```
- Per-phase `_meta/pipeline-state.yaml` is updated by each phase supervisor as usual.
- The iteration log at `_meta/iteration-log.jsonl` in each phase directory gets a new
  entry with `source: cross-phase-iteration` and the delta reference.

## Post-iteration retrospective

After all phases in the re-run range complete (including Phase 4 sign-off), the
supervisor automatically enters a new retrospective (Step G) on the updated outputs.
The new retrospective is written to `docs/refactoring/retrospective-iter<N>.md`.

The loop continues until the user picks `close` or `defer-and-close`.

## Deliberation during cross-phase iteration

If during the cross-phase delta construction the supervisor detects that an adjustment
is contested (e.g., the retrospective identified a UC that two sub-agents previously
disagreed on), route it through `deliberative-decision-engine` per
`integration-replatforming.md` before finalizing the delta. The deliberation trace ID
is recorded in the XADJ entry.

## Escalation to user

The supervisor escalates (halts and asks) in these situations:

| Situation | Action |
|---|---|
| Archive directory already exists from a prior iteration | Ask: "Archive from iteration N already exists. Overwrite or rename to iter<N+1>?" |
| Phase 4 re-run scope is `full` but `backend/` contains uncommitted local changes | Alert user; ask to commit, stash, or discard before archiving |
| Cross-phase delta is empty for all phases (no adjustments to apply) | Warn: "No actionable adjustments found. Re-running would produce identical outputs. Proceed anyway?" |
| Phase N's supervisor reports `failed` during cross-phase iteration | Stop; surface the failure; offer `retry-phase` or `stop-and-restore` (restore from archive) |
