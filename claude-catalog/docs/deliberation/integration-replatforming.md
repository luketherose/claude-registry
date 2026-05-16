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

## Decision points (Phases 1–3)

The analysis phases run inside the iteration loop documented in
`claude-catalog/docs/refactoring-workflow/iteration-loop.md`. The
iteration loop is single-agent by default. Deliberation is invoked
ONLY when:

- the user's iteration adjustments contain a debate trigger (lexicon
  match ≥ 0.7), OR
- an adjustment conflicts with a prior sub-agent output and a single-
  agent resolution would be subjective.

When that happens, the supervisor (workflow or phase) routes the
contested adjustment(s) to the engine BEFORE re-dispatching the
worker sub-agents in the iteration.

The decision points eligible for deliberation in Phases 1–3:

| Phase | Decision | Why deliberative |
|---|---|---|
| Phase 1 | Is X one actor or two (e.g., "user" vs "user" + "admin")? | Foundational; propagates to use-case fan-out and downstream traceability |
| Phase 1 | Should feature F-NN be split / merged / renamed per the user's adjustment? | Touches taxonomy; risk of fragmenting or over-coupling features |
| Phase 1 | Is use case UC-NN a confirmed UC, a candidate, or out of scope? | Drives Phase 4 build sequencing; misclassifying inflates or deflates scope |
| Phase 1 | Does implicit-logic finding IL-NN reflect real business logic or just framework wiring? | Affects whether logic gets re-implemented in TO-BE |
| Phase 2 | Is finding T-NN of severity high/critical or medium/low? | Drives prioritization, mitigation budget, and Phase 4 risk register |
| Phase 2 | Is risk R-NN cross-domain or domain-local? | Affects synthesis matrix; cross-domain risks need broader mitigation |
| Phase 2 | Is performance hotspot P-NN a real bottleneck or a benign hot path? | Affects whether Phase 4 must replace or simply rehost |
| Phase 3 | Should test failure F-NN be marked xfail with AS-IS bug note, or escalated as a blocking baseline failure? | Affects Phase 4 equivalence reference; xfail can mask real bugs |
| Phase 3 | Is integration I-NN in scope for the regression baseline? | Coverage decision; out-of-scope integrations skip oracle capture |
| Phase 1–3 | Scope-of-iteration disputes — when the user's adjustments are broad ("redo the actor map") and may invalidate downstream work, the supervisor may route the scope question itself to the engine | Avoids cascading re-dispatch that overshoots user intent |

For each routed Phase 1–3 decision, the supervisor builds a brief that
includes:

- the contested artifact (with stable IDs and the artifact path)
- the original sub-agent output for that artifact (verbatim)
- the user's adjustment text (verbatim)
- the supervisor's framing of the disagreement
- 2–4 candidate resolutions (the original, the user's, and 1–2
  intermediate options if the supervisor can identify them)

The engine runs at its default policy (5 personas, 1 round; 2 rounds
if the supervisor flags the decision as high-risk). The engine's
final-decision artefact is read from disk, surfaced to the user, and
recorded in the iteration log of the phase. The contested adjustment
in the delta is updated with the engine's resolution as `rationale`
before re-dispatching the worker sub-agents.

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
