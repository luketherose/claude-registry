# refactoring-supervisor — deliberative decision integration

When a decision in any phase (1–4) must be made through structured
multi-agent debate instead of the supervisor's normal single-agent
answer, route the decision to `deliberative-decision-engine`.

## Activation paths

1. **Explicit user prose** matched by the trigger lexicon at confidence
   ≥ 0.7. Triggers include (IT) `decidi con dibattito`, `usa modalità
   dibattito`, `usa multi-agente`, `fai criticare la decisione`,
   `fammi una decisione robusta`, `valuta pro e contro`; (EN) `debate
   mode`, `multi-agent debate`, `deliberative decision`, `decision
   review`, `red team this decision`, `robust decision`. Confidence
   0.4–0.7 ⇒ ask one focused clarifying question. Full lexicon and
   scoring rules in `claude-catalog/docs/deliberation/trigger-lexicon.md`.
2. **Programmatic flag** in the dispatch JSON (`decisionMode:
   "deliberative"` or `useDeliberativeDecision: true`, optionally with
   a `deliberationPolicy` block). When present at supervisor entry,
   deliberation applies for the whole workflow.
3. **Self-escalation** by the supervisor when the inferred risk level
   is `irreversible`, the decision is production-impacting, or it is
   compliance-/security-sensitive — even without an explicit trigger.
   Self-escalation also applies for Phases 1–3 when an iteration
   adjustment conflicts with a prior sub-agent output and resolution
   is subjective (e.g., "is admin one actor or two?", "is this security
   finding high or critical severity?").

## Dispatch protocol

For each routed decision, build a self-contained decision brief per the
schema at `claude-catalog/docs/deliberation/schemas.md` § "00-decision-
brief.json" — including the migration-criteria block when relevant —
and dispatch `deliberative-decision-engine` via the `Agent` tool. The
engine writes its full audit trail under
`<repo>/.deliberation-kb/<trace-id>/` and returns a final-decision
artefact path. Read the artefact, render the user-facing report (the
engine ships a Markdown render at `06-user-report.md`), and either
proceed (when `requiredHumanApproval == false`) or halt at the HITL
gate (when `true`). The Phase-4 final replatforming report
(`docs/refactoring/01-replatforming-report.md`) MUST cross-reference
every deliberation trace ID consumed during the phase.

## Default policy

When the caller provides no policy:
`agentCount: 5`, `debateRounds: 1` (2 if risk is `high`/`irreversible`
or task is highly ambiguous), `requireIndependentDrafts: true`,
`requireStructuredEvidenceSummary: true`, `requireDissentingOpinion:
true`, `finalDecisionStrategy: "auto"`, `commitProtocol: "auto"`,
`prioritizeQualityOverCost: true`, `preferredModelTier: "opus"`,
`requireHumanApprovalForHighRisk: true`.

## Hard rules

- **Never silently fall back to a single-agent answer** when deliberation
  was requested and could not complete. Surface the failure artefact and
  ask the user how to proceed.
- **Default behaviour stays single-agent.** Do NOT auto-deliberate on
  routine answers. The three activation paths above are the only entry
  conditions.
- **Decision points eligible for deliberation** are listed in
  `claude-catalog/docs/deliberation/integration-replatforming.md`:
  - § "Decision points (Phase 4)" — target architecture, migration
    approach (lift-and-shift vs refactor vs rearchitect vs rebuild vs
    replace), target cloud / runtime / platform, sequencing of
    migration waves, dependency conflicts, data-migration strategy,
    cutover, rollback, conflicting modernization recommendations, risky
    automated changes, security/compliance-sensitive changes.
  - § "Decision points (Phases 1–3)" — contested actor/feature/use-case
    definitions, contested risk severity, contested test scope,
    scope-of-iteration disputes when the user's adjustments require
    interpretation.
