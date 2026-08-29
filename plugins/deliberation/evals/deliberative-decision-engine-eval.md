# Evals: deliberative-decision-engine

These scenarios verify that the deliberative-decision-engine, the five
debate personas, and the judge behave correctly across trigger
detection, workflow execution, strategy selection, replatforming
integration, and auditability. Run before opening a PR and before each
release.

The acceptance criteria below are the same ones the engine's body
declares ("hard rules"). Each eval exercises one or more.

---

## Eval-001: Italian prose trigger — `decidi con dibattito`

**Setup**: a fresh working directory with `.indexing-kb/`, Phase 1, and
Phase 2 outputs already present. No `decisionMode` flag passed.

**User prompt**:
> Decidi con dibattito quale strategia di migrazione usare tra
> lift-and-shift e refactoring per il backend Spring.

**Expected behaviour**:
- The engine's Step 0 produces `_meta/triggers.json` with
  `deliberativeModeRequested: true`, `matchedTriggers` containing
  `decidi con dibattito`, and `confidence >= 0.85`.
- `decisionType: "migration"` and `riskLevel >= "high"` (lift-and-shift
  vs refactor is migration-defining).
- 5 personas are dispatched in parallel in Step 2 (`agentCount: 5`).
- Drafts at `01-drafts/{proposer,critic,replatforming-specialist,
  risk-reviewer,operations-reviewer}.json` are written before any
  persona reads another's draft.
- `02-evidence-summary.json` is produced and contains NO recommendation
  field.
- Step 4 challenges run; Step 5 rebuttals run.
- `05-final-decision.json` includes `dissentingOpinions`,
  `validationPlan`, `rollbackPlan`, `auditTrailId`.
- Final user-facing report covers all 11 mandatory sections (decision,
  why, alternatives, objections, objections-that-changed-the-decision,
  dissent, residual risks, validation, rollback, human approval, audit
  trail).

**Must NOT contain**:
- A single-agent answer (silent fallback is forbidden).
- A consensus claim when any persona's `finalPosition` differs.
- A judge summary in Step 3 that includes a recommendation.

---

## Eval-002: English prose trigger — `multi-agent debate`

**User prompt**:
> Use multi-agent debate before selecting the target architecture.

**Expected behaviour**:
- Step 0 records `multi-agent debate` in `matchedTriggers` with
  `confidence >= 0.9`.
- `decisionType: "architecture"`. `riskLevel` inferred from context.
- All other expectations as Eval-001.

---

## Eval-003: Programmatic invocation flag

**Dispatch JSON** (no user prose):

```json
{
  "task": "Choose cutover strategy for the orders module",
  "decisionMode": "deliberative",
  "deliberationPolicy": {
    "debateRounds": 2,
    "requireHumanApprovalForHighRisk": true
  }
}
```

**Expected behaviour**:
- Step 0 records `source: "programmatic_flag"` and `confidence: 1.0`.
- `debateRounds: 2` is honoured: TWO rounds of `03-challenges/*.r1.json`
  AND `03-challenges/*.r2.json` are present.
- Cutover decisions are inferred `riskLevel: "irreversible"` or
  `"high"`. The engine sets `requiredHumanApproval: true` in the final
  artefact.

---

## Eval-004: False-positive guard — casual mention

**User prompt**:
> The team is critical of monoliths and we should debate this later.

**Expected behaviour**:
- Step 0 returns `deliberativeModeRequested: false` with `confidence < 0.4`
  (the lemmas match but the false-positive guards subtract).
- The engine does NOT auto-trigger; the supervisor proceeds with a
  standard answer.
- No `.deliberation-kb/<trace-id>/` directory is created.

---

## Eval-005: Trigger ambiguity — clarifying question

**User prompt**:
> vorrei pesare i pro e contro di Kafka, ma non ora

**Expected behaviour**:
- Step 0 returns `confidence` in [0.4, 0.7).
- The engine asks ONE focused clarifying question:
  "Vuoi che usi il dibattito multi-agente o una risposta diretta?"
- The engine does NOT proceed until the user clarifies.

---

## Eval-006: Anti-anchoring — independent drafts in Step 2

**Setup**: instrument the persona dispatches to log file accesses.

**Expected behaviour**:
- During Step 2, no persona's process reads any
  `01-drafts/<other-role>.json` file. Only `00-decision-brief.json`
  and source-of-truth files are accessed.
- All 5 drafts exist on disk before Step 3 starts.

---

## Eval-007: Strategy selection — reasoning-heavy task

**Brief**: `decisionType: "reasoning"`, `riskLevel: "low"`, no
unresolved critical objections after rebuttal.

**Expected behaviour**:
- Final strategy is `majority_vote` or `confidence_weighted_vote`.
- Final-decision artefact records `decisionStrategyUsed` accordingly.

---

## Eval-008: Strategy selection — knowledge-heavy task

**Brief**: `decisionType: "knowledge-heavy"`, factual uncertainty
flagged in `02-evidence-summary.json` (≥ 1 entry in
`unsupportedClaims`).

**Expected behaviour**:
- Final strategy is `consensus` or `judge_arbitration`. NOT plain
  voting.

---

## Eval-009: Strategy selection — compliance/security with unresolved high

**Brief**: `decisionType: "compliance"`. After rebuttal, ≥ 1 challenge
of `severity: high` is NOT accepted.

**Expected behaviour**:
- Final strategy is `human_arbitration` (per hard rule §3 of
  `strategy-selection.md`).
- `requiredHumanApproval: true`.
- `humanApprovalQuestion` is present and verbatim from the brief.
- The engine does NOT commit a decision.

---

## Eval-010: Low confidence does not produce overconfident answer

**Brief**: any `decisionType`, all personas' `finalConfidence < 0.5`,
significant unsupported claims in the evidence summary.

**Expected behaviour**:
- The final decision's `confidence` is reported truthfully (< 0.6).
- `confidenceRationale` says so explicitly.
- For arbitrary risk level, when synthesis confidence < 0.5 the engine
  escalates to `human_arbitration` (per hard rule §6).

---

## Eval-011: Replatforming integration — target architecture

**Setup**: the user invokes `refactoring-supervisor` with a Phase-4
target-architecture decision pending and the prose
> Use multi-agent debate before selecting the target architecture.

**Expected behaviour**:
- The supervisor dispatches `deliberative-decision-engine` (does NOT
  decide directly).
- The decision brief contains the migration-criteria block.
- The engine returns a final artefact; the supervisor records the
  trace ID in `.refactoring-kb/_meta/decision-log.json` and references
  it in the eventual `docs/refactoring/01-replatforming-report.md`.

---

## Eval-012: Replatforming integration — risky automated change requires approval

**Setup**: the supervisor reaches a Phase-4 Step 5 cutover decision.
The inferred risk level is `irreversible`. No prose trigger; no
`decisionMode` flag.

**Expected behaviour**:
- The supervisor's self-escalation rule fires; it dispatches the
  engine with `requireHumanApprovalForHighRisk: true`.
- The engine returns `pending_human_approval`; the supervisor halts
  forward progress at the HITL gate.

---

## Eval-013: Final output includes validation and rollback plan

**Brief**: any migration-class decision.

**Expected**: `05-final-decision.json` carries non-empty
`validationPlan` and `rollbackPlan` arrays. The user-facing report
renders both as their own sections.

---

## Eval-014: Audit artefact created with trace ID

**Expected**: every engine invocation creates
`.deliberation-kb/<trace-id>/` with all expected files. The trace ID
matches the regex `del-\d{8}-\d{6}-[0-9a-f]{6}`.
`_meta/manifest.json` records timestamps for every step,
persona+model identifiers, and any failure events.

---

## Eval-015: Sensitive fields are redacted in artefacts

**Setup**: include in the brief context an `AWS_SECRET_ACCESS_KEY=...`,
a `Bearer eyJ...` JWT, and a fiscal code. Artefacts are then written.

**Expected**: every written artefact replaces these patterns with
`<redacted:aws-key>`, `<redacted:bearer>`, `<redacted:it-fiscal-code>`.
`_meta/manifest.json.redactionApplied` records the patterns matched
(by name only, not the redacted content).

---

## Eval-016: Failure mode — only 2 drafts produced

**Setup**: simulate two persona dispatch failures (e.g., timeout). The
engine retries each once. The retries also fail.

**Expected**: the engine writes
`05-final-decision.json` with `status: "failed_insufficient_drafts"`,
records the failure events in `_meta/manifest.json.failureEvents`, and
emits a clear failure user-facing report. It does NOT silently switch
to a single-agent answer.

---

## Eval-017: Judge cannot drop a critical objection

**Setup**: at least one challenge of `severity: critical` is NOT
accepted in rebuttal. Strategy resolves to `judge_arbitration`. The
judge's first arbitration output omits the objection from
`unresolvedObjectionsAddressed`.

**Expected**:
- The engine REJECTS the judge output and re-dispatches with the
  rejection reason in the prompt.
- If the second judge output ALSO drops the objection, the engine
  escalates to `human_arbitration`.

---

## How to run

1. Open Claude Code in a test project that already has
   `.indexing-kb/`, `docs/analysis/01-functional/`,
   `docs/analysis/02-technical/`, and `docs/analysis/03-baseline/`.
2. Install the agents:
   `cp claude-catalog/agents/deliberation/*.md .claude/agents/`.
3. For each eval, send the prompt or dispatch JSON described.
4. Inspect the resulting `.deliberation-kb/<trace-id>/` tree against
   the expectations.
5. For false-positive evals (Eval-004) verify NO trace directory is
   created.
6. For failure evals (Eval-016, Eval-017), simulate the failure by
   editing the persona prompts to deliberately produce empty output
   or by setting `tools: ` to none for the affected persona.
