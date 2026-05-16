# Iteration loop — canonical HITL pattern for analysis phases

> Reference doc for `refactoring-supervisor` and for every analysis-phase
> supervisor (Phase 1 `functional-analysis-supervisor`, Phase 2
> `technical-analysis-supervisor`, Phase 3 `baseline-testing-supervisor`).
> Read at runtime when reaching the end of an analysis phase, or when the
> user answers `iterate` to a post-phase prompt.
>
> The premise is the user-stated principle: **the analysis phases — and
> Phase 1 in particular — are the most delicate part of the workflow.**
> A misunderstanding captured there propagates through every later phase
> and is expensive to undo. Therefore each analysis phase ends with a
> human-in-the-loop iteration loop, not a one-shot proceed/stop choice.

## Scope

The iteration loop applies to Phases 1–3 (analysis phases). It does NOT
apply to Phase 0 (indexing — the KB is a deterministic artifact; revise
by re-running with adjusted scope) and it does NOT apply to Phase 4
(replatforming — Phase 4 has its own per-step HITL with the Step 3
sub-loop). Within Phase 4, decision-point debate is governed by
`integration-replatforming.md`.

## States

A phase under the iteration loop transitions through these states:

```
fresh ─┬─► run iteration 1 ──► verification-report ──► HITL
       │                                                 │
       │                                       ┌─────────┼─────────┐
       │                                       │         │         │
       │                                  approve     iterate    stop
       │                                       │         │         │
       │                                       ▼         ▼         ▼
       │                                   advance   delta capture  end
       │                                       │         │
       │                                       │         ▼
       │                                       │     run iteration N+1
       │                                       │     (targeted re-dispatch)
       │                                       │         │
       │                                       │         ▼
       │                                       │     verification-report
       │                                       │     (compared vs N)
       │                                       │         │
       │                                       │         ▼
       │                                       │       HITL again
       └◄──────────────────────────────────────┘
```

There is no fixed cap on iterations. The workflow ends when the user
answers `approve` or `stop`. The manifest records every iteration in
the `runs[]` array.

## The three user options

After every post-phase recap (and every verification report), the user
is offered exactly three options:

| Option | Meaning | Effect |
|---|---|---|
| `approve` | The analysis is accepted as-is. Open questions / partial sections are accepted. | Phase status set to `approved`. Workflow advances to next phase. |
| `iterate` | The analysis is partially wrong, incomplete, or based on a misreading. User provides specific adjustments. | Phase remains `in-progress`. A new iteration runs with the adjustments applied. A new verification report is produced. |
| `stop` | The user wants to end the workflow at this point. | Phase status set to `partial`. Workflow ends; manifest is finalized. |

The `approve` option must NEVER be auto-selected. The supervisor (workflow
or phase) must explicitly wait for the user's choice.

## Iteration delta — what the user provides

When the user picks `iterate`, the supervisor asks for the adjustments
to apply. The user response is captured verbatim AND structured. The
supervisor should accept any of the following input shapes and normalize
internally:

- **Free prose**: "Actually the admin panel is a separate actor; please
  re-extract the actor map. Also, UC-07 is wrong — it doesn't trigger
  on save, it triggers on form submit."
- **Bulleted list**: short items targeting specific outputs.
- **File-and-line callouts**: "In `02-features.md`, F-04 is mis-titled
  and merges two features."
- **A reference to deliberation**: "Use debate to decide whether the
  admin role is one actor or two."

The supervisor normalizes the user's adjustments into the structured
delta schema below (written to `_meta/iteration-log.jsonl`):

```json
{
  "iteration": <N+1>,
  "captured_at": "<ISO-8601>",
  "raw_user_input": "<verbatim>",
  "adjustments": [
    {
      "adjustment_id": "ADJ-NN",
      "target_artifacts": ["<path>", "..."],
      "target_ids": ["UC-07", "A-02", "..."],
      "kind": "correction | addition | removal | clarification | re-scope",
      "summary": "<one-line>",
      "rationale": "<from user input or inferred>",
      "deliberate": false
    }
  ],
  "debate_requested": false,
  "debate_trigger": null
}
```

When the user input is unstructured prose, the supervisor must produce
at least one `adjustment` per distinct intent it can identify. If the
input contains a debate trigger (lexicon match — see
`claude-catalog/docs/deliberation/trigger-lexicon.md`), set
`debate_requested: true` and route the contested adjustment through
deliberation (see § "Optional deliberation" below).

If the user input is completely ambiguous and the supervisor cannot
identify any target artifact: **stop and ask one focused clarifying
question** before launching the iteration. Never start an iteration
with an empty or unparseable delta.

## Re-dispatch policy — what runs in iteration N+1

Iteration N+1 is NOT a full re-run. The supervisor picks which
sub-agents to re-dispatch based on the `target_artifacts` and
`target_ids` of each adjustment. The mapping is phase-specific (each
phase plan documents its own re-dispatch rules) but follows the same
principle: **re-run the minimum set of sub-agents required to apply
the adjustments cleanly, plus any downstream sub-agents whose outputs
depend on the changed ones.**

Cross-cutting rules:

- Re-dispatch is always preceded by a confirmation summary to the user:
  "I am about to re-run <list of sub-agents> with these adjustments
  applied. Proceed?" — except when the user has already pre-confirmed
  in the iteration request.
- Sub-agents are re-dispatched with the adjustments injected into their
  prompt as a "User feedback from prior iteration" block. The prompt
  template (per phase) must include this block.
- The auditor / challenger sub-agents (functional-traceability-auditor,
  technical-evidence-auditor, baseline-challenger) ALWAYS re-run in any
  iteration where at least one of their input artifacts changed.
- Exports (PDF / PPTX) are NOT regenerated automatically at the end of
  every iteration. They are regenerated only when the user picks
  `approve` (so the deliverable reflects the approved state).
- Manifest update is mandatory: append a new entry to `runs[]` with
  `iteration: N+1`, the dispatched sub-agents, and the per-wave outcomes.

## Optional deliberation — when adjustments are contested

If the user's iteration request contains a debate trigger (lexicon
match at confidence ≥ 0.7), OR if the supervisor detects that an
adjustment is in conflict with prior sub-agent outputs and a single-
agent resolution would be subjective, the supervisor routes the
contested adjustment through `deliberative-decision-engine` BEFORE
re-dispatching the worker sub-agents.

The flow:

1. Identify the contested adjustment(s) (one or more from the delta).
2. Build a decision brief per the schema in
   `claude-catalog/docs/deliberation/schemas.md`. The brief includes:
   - the original sub-agent output(s) for the contested artifact(s)
   - the user's adjustment text and rationale
   - the supervisor's framing of the disagreement
3. Dispatch the engine via the Agent tool with the brief + default
   policy from § "Default deliberation policy" in
   `claude-catalog/docs/deliberation/integration-replatforming.md`.
4. Read the engine's final-decision artefact from disk.
5. If `requiredHumanApproval == true`: halt; surface the engine's
   recommendation to the user; ask for explicit acceptance before
   updating the delta.
6. If `requiredHumanApproval == false`: rewrite the contested
   adjustment in the delta with the engine's resolution as
   `rationale`, then proceed to re-dispatch.
7. In either case, record the deliberation trace ID in the iteration-
   log entry.

Hard rules carry over from Phase 4:

- Never silently substitute a single-agent answer when deliberation was
  requested and could not complete.
- Routine adjustments (no debate trigger, no conflict) skip the
  deliberation step entirely. The default behaviour is single-agent.
- The verification report (next iteration) cross-references every
  deliberation trace ID consumed in the prior iteration.

## Convergence and exit conditions

The iteration loop has no built-in cap. It terminates when the user
picks `approve` or `stop`. Practical guidance:

- The supervisor should surface in the verification report a "delta vs
  prior iteration" summary, so the user can see whether the iteration
  is converging or oscillating.
- If after iteration N the user's adjustments largely re-open prior
  closed adjustments (i.e., the loop is oscillating), the supervisor
  may suggest a deliberation-based reset on the affected scope. It
  must not do so unilaterally.
- The phase status in the manifest is `in-progress` until `approve` or
  `stop`. The supervisor must NEVER set status to `complete` or
  `approved` without explicit user confirmation.

## Idempotency

Re-running an iteration with the exact same delta MUST produce the
same outputs (idempotent re-dispatch). To achieve this the supervisor:

- Passes the delta as a stable JSON block in the sub-agent prompt.
- Does not inject conversation context that varies between turns.
- Snapshots the prior iteration's outputs before overwriting (the
  phase plan documents the per-phase snapshot policy — usually a
  rename to `<file>.iter-N.bak` or a copy under `_meta/snapshots/`).

The snapshot serves both as a rollback target if the user picks
`iterate` again with different adjustments, and as the source of the
"what changed vs prior iteration" section of the verification report.
