# Deliberation — integration with the Replatforming Agent

How `deliberative-decision-engine` plugs into `refactoring-supervisor`
(capability name: "Application Replatforming") at decision points
across Phases 0–4.

## Integration model

`refactoring-supervisor` retains its standard answering behaviour. The
deliberation engine is invoked **only** when one of these is true:

1. The user explicitly requests deliberation in their utterance
   (matched by the trigger lexicon at confidence ≥ 0.7).
2. The dispatch JSON for the supervisor contains
   `decisionMode: "deliberative"` (or
   `useDeliberativeDecision: true`).
3. The supervisor itself routes a Phase-4 decision point to the
   engine because the decision is irreversible / production-impacting
   / compliance-sensitive (the supervisor's own escalation rule).

The supervisor never auto-deliberates routine answers. The default
behaviour is single-agent.

## Decision points (Phase 4)

When `decisionMode: deliberative` or an explicit trigger fires, the
supervisor routes the following decision points to the engine instead
of deciding directly:

| Phase / step | Decision | Why deliberative |
|---|---|---|
| Phase 4 Step 0 | Choosing target architecture style | Foundational, hard to reverse later |
| Phase 4 Step 0 | Lift-and-shift vs refactor vs rearchitect vs rebuild vs replace | Drives every subsequent step; trade-off-heavy |
| Phase 4 Step 0 | Target cloud / runtime / platform | Lock-in, cost envelope, supplier risk |
| Phase 4 Step 1 | Sequencing of migration waves | Operational / dependency risk |
| Phase 4 Step 2 (per feature) | Resolving dependency conflicts where multiple modernization paths are viable | Cross-cutting impact |
| Phase 4 Step 2 / Step 4 | Data-migration strategy (one-shot vs dual-write vs CDC) | Data-loss risk |
| Phase 4 Step 5 | Cutover strategy (big-bang / parallel-run / strangler-fig / blue-green / canary) | Production-impacting |
| Phase 4 Step 5 | Rollback strategy | Reversibility / RTO-RPO |
| Phase 4 Step 5 | Resolving conflicting modernization recommendations across personas | Synthesis-heavy |
| Phase 4 any step | Approving risky automated changes | Safety control |
| Phase 4 any step | Selecting between competing implementation plans | Disagreement among specialist sub-agents |
| Phase 4 any step | Evaluating security / compliance-sensitive changes | Hard rule for human or judge arbitration |

For each, the supervisor builds a **decision brief** (per the schema in
`schemas.md`) and dispatches the engine as a sub-agent:

```
Agent(
  subagent_type: "deliberative-decision-engine",
  prompt: <self-contained brief + policy JSON>
)
```

The supervisor receives the engine's `05-final-decision.json` artefact
path back. When `requiredHumanApproval == true`, the supervisor halts
forward progress and surfaces the pending decision to the user via the
existing HITL checkpoint mechanism (the same one it uses between
phases). When `requiredHumanApproval == false`, the supervisor records
the decision in `.refactoring-kb/_meta/decision-log.json` and
proceeds.

## Programmatic invocation

The supervisor accepts an optional dispatch JSON of shape:

```json
{
  "decisionMode": "deliberative",
  "deliberationPolicy": {
    "agentCount": 5,
    "debateRounds": 2,
    "finalDecisionStrategy": "auto",
    "commitProtocol": "auto",
    "requireHumanApprovalForHighRisk": true,
    "preferredModelTier": "opus"
  }
}
```

When present at supervisor entry, every decision point above is routed
to the engine for the duration of the workflow. When absent, the
supervisor's standard single-agent behaviour applies.

## Audit-trail integration

Deliberation artefacts live at `<repo>/.deliberation-kb/<trace-id>/`.
The supervisor's per-phase recap and the Phase-4 final replatforming
report (`docs/refactoring/01-replatforming-report.md`) cross-reference
every deliberation trace ID consumed by that phase, so the
replatforming report contains a "Decisions made through deliberation"
section listing each (trace ID, decision question, selected option,
human-approval status).

## Trigger detection inside the supervisor

For prose-level triggers, the supervisor passes the user's utterance
to the engine's Step-0 detector unchanged. The engine returns a
`triggers.json` record; the supervisor records it in its own audit
trail and proceeds with the deliberation if confidence ≥ 0.7. Below
0.7, the supervisor asks one focused clarifying question
(`Vuoi che usi il dibattito multi-agente o una risposta diretta?`)
and waits for confirmation before proceeding.

## Failure handling at the integration boundary

- **Deliberation aborts with `failed_insufficient_drafts`**: the
  supervisor halts the affected step, surfaces the failure artefact,
  and asks the user how to proceed (retry / proceed standard with
  explicit consent / abort the phase). It NEVER silently substitutes a
  single-agent answer.
- **Deliberation returns `pending_human_approval`**: the supervisor
  treats this as a hard HITL gate. The phase does not advance until
  the user provides the decision. The engine can be re-invoked with
  the user's input as additional evidence.
- **Trigger detection ambiguous (confidence 0.4–0.7)**: the
  supervisor asks one clarifying question, then proceeds standard if
  the user declines deliberation.

## Example user invocations (recipes)

### Italian — explicit prose trigger

> Decidi con dibattito quale strategia di migrazione usare tra
> lift-and-shift e refactoring per il backend Spring.

Supervisor detects (`decidi con dibattito` exact match → confidence
0.9) → builds the migration-strategy brief → dispatches the engine
with default policy → engine runs the 7-step pipeline → returns a
final decision artefact. Supervisor renders the user-facing report.

### Italian — programmatic trigger from a calling tool

```json
{
  "task": "scegliere la strategia di cutover per la migrazione
           del modulo orders",
  "decisionMode": "deliberative",
  "deliberationPolicy": {
    "debateRounds": 2,
    "requireHumanApprovalForHighRisk": true
  }
}
```

Supervisor reads the JSON, routes to the engine, the engine runs with
2 challenge rounds.

### English — explicit prose trigger

> Use multi-agent debate before selecting the target architecture.

Supervisor detects (`multi-agent debate` exact match → confidence
0.95) → routes the target-architecture decision to the engine.

### High-risk decision auto-escalates inside the supervisor

The supervisor is partway through Phase 4 Step 5 (cutover) and the
inferred risk level is `irreversible`. Even without an explicit
trigger, the supervisor's own escalation rule routes the cutover
decision to the engine with `requireHumanApprovalForHighRisk: true`,
and the engine returns a `pending_human_approval` artefact. The user
sees the standard HITL checkpoint UI.
