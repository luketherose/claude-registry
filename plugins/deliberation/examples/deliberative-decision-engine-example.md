# Example: deliberative-decision-engine

## Scenario 1: Italian prose trigger for a migration decision

**Setup**: a project with `.indexing-kb/`, Phase 1, Phase 2, and
Phase 3 outputs. The user is mid-Phase-4 and has not yet decided on
the migration approach for the `orders` bounded context.

**User prompt**:
> Decidi con dibattito: per il bounded context `orders` conviene
> lift-and-shift su Spring Boot mantenendo lo stesso schema, oppure
> rearchitect a event-driven con Kafka? Vincoli: cutover entro 60
> giorni, rollback obbligatorio, dati storici 5 anni da preservare.

**Expected behaviour**:

1. Engine Step 0 detects `decidi con dibattito` (confidence 0.9).
   `decisionType: "migration"`, `riskLevel: "high"` (cutover with
   rollback obligation, 5-year historical data).
2. Engine Step 1 writes `00-decision-brief.json` including the
   migration-criteria block (cutover risk: high; rollback obligatory;
   data-migration risk: high; reversibility: partially_reversible).
3. Engine Step 2 dispatches all 5 personas in parallel. Each writes
   its draft without seeing the others'.
4. Step 3 produces the evidence summary (judge in summariser mode, no
   recommendation).
5. Step 4 challenge round runs in parallel. The critic flags
   `severity: critical` on the lift-and-shift draft for the data-
   migration plan being underspecified. The risk-reviewer flags
   `requiresJudgeArbitration: true` because cutover is irreversible
   past 7 days.
6. Step 5 rebuttals: the proposer accepts the data-migration challenge
   `material` impact, narrows lift-and-shift to a strangler-fig with
   CDC; the operations-reviewer reduces confidence on lift-and-shift
   from 0.7 to 0.55.
7. Strategy selection: `decisionType: migration`, `riskLevel: high`,
   any disagreement → `judge_arbitration`. Engine dispatches
   debate-judge in arbitration mode. Judge addresses every
   `severity: critical` objection in `unresolvedObjectionsAddressed`.
8. Final artefact: `selectedOption: "rearchitect to event-driven with
   Kafka, with strangler-fig sequencing"`,
   `dissentingOpinions: [{role: "proposer", finalPosition:
   "lift-and-shift with CDC", finalConfidence: 0.55}]`,
   `validationPlan` and `rollbackPlan` populated, `requiredHumanApproval:
   true` (because reversibility is `partially_reversible` and the
   policy says require approval for high risk).

**Must NOT contain**:
- A consensus claim (proposer dissented).
- A single-agent answer.
- A recommendation field in `02-evidence-summary.json`.

---

## Scenario 2: Programmatic invocation by `refactoring-supervisor`

**Setup**: `refactoring-supervisor` is mid-Phase-4. The supervisor
detects an irreversible cutover decision and self-escalates.

**Dispatch from supervisor** (built per
`docs/deliberation/integration-replatforming.md`):

```json
{
  "task": "Choose cutover strategy for the orders bounded context",
  "decisionMode": "deliberative",
  "deliberationPolicy": {
    "agentCount": 5,
    "debateRounds": 2,
    "requireHumanApprovalForHighRisk": true,
    "preferredModelTier": "opus"
  },
  "brief": { /* full 00-decision-brief.json content with
                migrationCriteria block */ }
}
```

**Expected behaviour**:
- Engine `confidence: 1.0`, `source: "programmatic_flag"`.
- Two challenge rounds run (`*.r1.json` and `*.r2.json` present in
  `03-challenges/`).
- Final-decision strategy is `human_arbitration` (irreversible +
  policy says require approval). The engine produces a
  `pending_human_approval` artefact with the explicit
  `humanApprovalQuestion`.
- Supervisor halts Phase 4 Step 5 at the HITL gate; renders the
  pending question with the audit-trail tree to the user.

---

## Scenario 3: False positive — casual mention of "debate"

**User prompt**:
> The team is critical of monoliths and we should debate this later.

**Expected behaviour**:
- Step 0 detector: lemmas `critical` and `debate` matched but the
  false-positive guard subtracts (future-tense planning + adjective
  use). Confidence 0.2.
- Engine does NOT auto-trigger.
- Supervisor proceeds with a standard answer.
- No `.deliberation-kb/<trace-id>/` directory is created.

---

## Scenario 4: Trigger ambiguity → clarifying question

**User prompt**:
> vorrei pesare i pro e contro, ma forse non serve un dibattito vero
> e proprio

**Expected behaviour**:
- Confidence in [0.4, 0.7).
- Engine asks ONE focused clarifying question:
  "Vuoi che usi il dibattito multi-agente o una risposta diretta?"
- Engine waits for user clarification before proceeding.

---

## Scenario 5: Failure — only 2 personas respond

**Setup**: simulate persona dispatch failures (e.g., a persona
returns an empty artefact twice).

**Expected behaviour**:
- Engine retries each failed dispatch once.
- After failures persist, engine writes
  `05-final-decision.json` with `status: "failed_insufficient_drafts"`.
- `_meta/manifest.json.failureEvents` records the dispatch failures.
- Engine surfaces a failure user-facing report.
- Engine does NOT silently switch to a single-agent answer.
