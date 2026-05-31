# Workflow Retrospective

> Reference doc for `refactoring-supervisor`. Read immediately after Phase 4 Step 6
> PO sign-off is captured (auto-trigger), or when the user explicitly requests a
> retrospective ("retrospettiva", "retrospective", "cosa è andato storto").
>
> The retrospective is the BMAD-mandated quality gate that closes the workflow loop:
> it surfaces what was learned across all five phases, classifies issues by scope and
> severity, and determines whether the workflow should close or re-iterate from an
> earlier phase. It does NOT run any sub-agents — it synthesizes from artifacts
> already on disk.

## When it runs

| Mode | Trigger |
|---|---|
| **Auto** | Immediately after Phase 4 Step 6 PO sign-off is captured |
| **Manual** | User explicitly requests it at any point after Phase 4 |

In Auto mode the supervisor announces: "Phase 4 is complete — entering Workflow
Retrospective." In Manual mode it confirms: "Run the workflow retrospective now? [yes /
stop]"

## Review dimensions — one per phase

The supervisor reads these artifacts (do not re-read source code):

| Phase | Artifact(s) to read |
|---|---|
| Phase 0 | `.indexing-kb/gold/indexing-audit.md` (verdict + gaps) |
| Phase 1 | `docs/analysis/01-functional/_meta/phase-verification-report.md` + `_meta/iteration-log.jsonl` |
| Phase 2 | `docs/analysis/02-technical/_meta/phase-verification-report.md` + `_meta/iteration-log.jsonl` |
| Phase 3 | `docs/analysis/03-baseline/baseline-report.md` |
| Phase 4 | `docs/refactoring/workflow-manifest.json` + `docs/refactoring/01-replatforming-report.md` |

For each phase, assess:

| Field | Description |
|---|---|
| `overall_verdict` | `green` / `amber` / `red` |
| `issues[]` | List of issues found (see issue schema) |
| `what_worked` | Notable successes (1–3 bullets) |
| `what_to_improve` | Adjustments for a hypothetical re-run (1–3 bullets) |

### Issue schema

```json
{
  "issue_id": "RETRO-NN",
  "phase": "phase-1",
  "severity": "blocking | high | medium | low",
  "kind": "misanalysis | coverage-gap | wrong-assumption | integration-mismatch | performance-regression | scope-drift | other",
  "summary": "<one-line>",
  "evidence": "<file path or artifact reference>",
  "downstream_impact": ["phase-2", "phase-4"],
  "rerun_scope": "full-phase | targeted | none",
  "status": "open | accepted | deferred"
}
```

`downstream_impact` lists every phase that would need to change if this issue were
resolved. `rerun_scope` is the minimum re-run scope for this issue in isolation; the
actual cascade is computed by `cross-phase-iteration.md`.

## Severity classification

| Severity | Criteria |
|---|---|
| `blocking` | Delivered TO-BE does NOT faithfully replicate AS-IS for ≥ 1 confirmed UC. Must re-iterate. |
| `high` | Analysis was materially wrong (e.g., key actor missing, UC scope incorrect), but delivered code is correct — likely due to corrections during Phase 4. Should re-iterate; user may override with explicit `accept`. |
| `medium` | Analysis was incomplete or partially incorrect; delivered code is correct. Document and defer. |
| `low` | Minor gaps, notes for a future run. Document and close. |

A retrospective with ≥ 1 `blocking` issue MUST recommend `iterate`. A retrospective
with ≥ 1 `high` issue SHOULD recommend `iterate` (user may override).

## Output file

Write the retrospective to `docs/refactoring/retrospective.md`. The file is human-
readable AND machine-parseable (the `## Recommendation` section uses a canonical
format the supervisor reads without re-inference).

```markdown
# Workflow Retrospective — <project-name>
Generated: <ISO-8601>
Workflow: application-replatforming v<N>

## Executive summary
<3–5 lines: overall verdict, issue counts, recommendation>

## Phase 0 — Codebase Indexing
### Verdict: green | amber | red
### What worked
- ...
### What to improve
- ...
### Issues
| ID | Severity | Summary | Downstream impact | Rerun scope | Status |
|---|---|---|---|---|---|

## Phase 1 — Functional Analysis
(same structure)

## Phase 2 — Technical Analysis
(same structure)

## Phase 3 — Baseline Testing
(same structure)

## Phase 4 — Application Replatforming
(same structure)

## Cross-cutting findings
<Issues spanning multiple phases, not attributable to a single phase>

## Recommendation
<!-- DO NOT EDIT THIS BLOCK MANUALLY — parsed by refactoring-supervisor -->
decision: close | iterate | defer-and-close
earliest_affected_phase: phase-N    <!-- only when decision is iterate -->
open_blocking_count: N
open_high_count: N
<!-- END RECOMMENDATION BLOCK -->
```

## Decision options

After producing the report, the supervisor presents:

```
=== Workflow Retrospective — complete ===

Report: docs/refactoring/retrospective.md

Summary:
- Blocking issues: <N>
- High issues:     <N>
- Medium issues:   <N>
- Low issues:      <N>

Recommendation: <close | iterate | defer-and-close>
<one-sentence rationale>

What would you like to do?

  [close]              Accept findings as-is. Workflow complete. All open issues
                       are marked `accepted` in the report.
  [iterate]            Re-run from the earliest affected phase with adjustments.
                       You will be asked to confirm re-run scope.
                       ← offered only when ≥ 1 open blocking or high issue
  [defer-and-close]    Mark all open issues as `deferred`. Close the workflow now.
                       Issues remain visible for a future run.
```

`close` is NEVER auto-selected. The supervisor waits for explicit user input.

If the retrospective has ≥ 1 blocking issue, choosing `close` requires `close
--override` (the supervisor re-asks once to confirm intentional acceptance of known
failures). If all issues are medium/low, `close` is offered normally.

## Routing to cross-phase iteration

When the user picks `iterate`:

1. Collect all `blocking` and `high` issues with `status: open`.
2. Union all their `downstream_impact` phase IDs. Add the issue's own phase.
3. The **earliest phase** in the union (Phase 1 < 2 < 3 < 4) is the re-entry point.
   Phase 0 is never a re-entry point — Phase 0 re-runs are a separate scope change.
4. Build the cross-phase delta (see `cross-phase-iteration.md` § "Delta schema").
5. Confirm re-run scope with the user:
   ```
   I will re-run the workflow from Phase <N> through Phase 4 with these adjustments:
   <list of issues being addressed, grouped by phase>
   Existing outputs will be archived before overwriting.
   Confirm? [yes / revise scope / stop]
   ```
6. On `yes`: execute cross-phase iteration per `cross-phase-iteration.md`.

## Re-iteration record

When a cross-phase iteration is triggered from the retrospective, append to the
existing `docs/refactoring/retrospective.md` (do NOT overwrite):

```markdown
## Re-iteration record

### Iteration 1 — <ISO-8601>
Triggered by: issues RETRO-01, RETRO-03
Re-entry phase: phase-1
Cross-phase delta: docs/refactoring/_meta/cross-phase-delta-iter1.json
Outcome: <pointer to the new retrospective after re-iteration>
```

After each cross-phase iteration, the supervisor produces a new retrospective
report at `docs/refactoring/retrospective-iter<N>.md` and presents the same
decision loop. The cycle repeats until the user picks `close` or `defer-and-close`.

## Idempotency

Re-running the retrospective with the same disk artifacts MUST produce the same
`issues[]` list (same IDs, same severity). The supervisor reads from disk only —
it must not re-infer severity from conversation context. If the artifacts have
changed (a new cross-phase iteration ran), different outputs are expected and correct.
