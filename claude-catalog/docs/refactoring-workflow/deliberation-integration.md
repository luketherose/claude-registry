# Deliberation integration — `refactoring-supervisor`

> Reference doc for `refactoring-supervisor`. Read at runtime when a
> decision point may need to be routed to `deliberative-decision-engine`
> instead of being answered single-agent. Decision rules for routing
> live in `decision-rules.md` § "Deliberation routing"; this doc covers
> the activation paths, default policy, and hard rules.
>
> Related: `claude-catalog/docs/deliberation/integration-replatforming.md`
> lists the eligible decision points per phase.

## Activation paths

When a decision in any phase (1–4) must be made through structured
multi-agent debate, route to `deliberative-decision-engine` via one of
three paths:

1. **Explicit user prose** matched by the trigger lexicon at confidence
   ≥ 0.7. Triggers include (IT) `decidi con dibattito`, `usa modalità
   dibattito`, `usa multi-agente`, `fai criticare la decisione`,
   `fammi una decisione robusta`, `valuta pro e contro`; (EN) `debate
   mode`, `multi-agent debate`, `deliberative decision`, `decision
   review`, `red team this decision`, `robust decision`. Confidence
   0.4–0.7 ⇒ ask one focused clarifying question. Full lexicon and
   scoring rules in `../deliberation/trigger-lexicon.md`.
2. **Programmatic flag** in the dispatch JSON (`decisionMode:
   "deliberative"` or `useDeliberativeDecision: true`, optionally with
   a `deliberationPolicy` block). When present at supervisor entry,
   deliberation applies for the whole workflow.
3. **Self-escalation** by the supervisor when the inferred risk level
   is `irreversible`, the decision is production-impacting, or it is
   compliance-/security-sensitive — even without an explicit trigger.
   Self-escalation also applies for Phases 1–3 when an iteration
   adjustment conflicts with a prior sub-agent output and resolution
   is subjective (e.g., "is admin one actor or two?", "is this
   security finding high or critical severity?").

## Dispatch protocol

For each routed decision:

1. Build a self-contained decision brief per the schema at
   `../deliberation/schemas.md` § "00-decision-brief.json" — include
   the migration-criteria block when relevant.
2. Dispatch `deliberative-decision-engine` via the `Agent` tool.
3. The engine writes its full audit trail under
   `<repo>/.deliberation-kb/<trace-id>/` and returns a final-decision
   artefact path.
4. Read the artefact, render the user-facing report (the engine ships
   a Markdown render at `06-user-report.md`), and either:
   - proceed (when `requiredHumanApproval == false`), or
   - halt at the HITL gate (when `true`).
5. The Phase-4 final replatforming report
   (`docs/refactoring/01-replatforming-report.md`) MUST cross-reference
   every deliberation trace ID consumed during the phase.

## Default policy

When no `deliberationPolicy` block is provided by the caller, use:

```json
{
  "agentCount": 5,
  "debateRounds": 1,
  "requireIndependentDrafts": true,
  "requireStructuredEvidenceSummary": true,
  "requireDissentingOpinion": true,
  "finalDecisionStrategy": "auto",
  "commitProtocol": "auto",
  "prioritizeQualityOverCost": true,
  "preferredModelTier": "opus",
  "requireHumanApprovalForHighRisk": true
}
```

Bump `debateRounds: 2` when risk is `high`/`irreversible` or the
task is highly ambiguous.

## Hard rules

- **Never silently fall back to a single-agent answer** when
  deliberation was requested and could not complete. Surface the
  failure artefact and ask the user how to proceed.
- **Default behaviour stays single-agent.** Do NOT auto-deliberate on
  routine answers. The activation paths above are the only entry
  conditions.
- **Decision points eligible for deliberation** are listed in
  `../deliberation/integration-replatforming.md`. The doc has two
  sections: § "Decision points (Phase 4)" — target architecture,
  migration approach (lift-and-shift vs refactor vs rearchitect vs
  rebuild vs replace), target cloud / runtime / platform, sequencing
  of migration waves, dependency conflicts, data-migration strategy,
  cutover, rollback, conflicting modernization recommendations, risky
  automated changes, security/compliance-sensitive changes. §
  "Decision points (Phases 1–3)" — contested actor/feature/use-case
  definitions, contested risk severity, contested test scope,
  scope-of-iteration disputes when the user's adjustments require
  interpretation.
