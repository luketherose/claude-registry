# Deliberation — final-decision strategy selection

Authoritative rules for `deliberative-decision-engine` Step 6. Maps
`(decisionType, riskLevel, residualDisagreement, criticalObjections)` to
a `finalDecisionStrategy`.

## Inputs to the selector

- `decisionType` from Step 0: `reasoning | architecture | migration |
  knowledge-heavy | compliance | security | risk | operational |
  unknown`.
- `riskLevel` from Step 0: `low | medium | high | irreversible`.
- `residualDisagreement`: `none | minor | material | split` —
  computed from final positions in `04-rebuttals/*.json`. `split` ⇒
  no clear majority option after rebuttals.
- `unresolvedHighSeverity`: count of challenges with `severity: high |
  critical` that were NOT accepted in rebuttal.
- `requireHumanApprovalForHighRisk`: from policy.
- `requiresHumanArbitration` flag from `debate-risk-reviewer.json`.

## Hard rules (apply first, in order)

1. If `requiresHumanArbitration == true` (set by risk-reviewer) →
   `human_arbitration`.
2. If `riskLevel == "irreversible"` AND `requireHumanApprovalForHighRisk
   == true` → `human_arbitration`.
3. If `decisionType ∈ {compliance, security}` AND `unresolvedHighSeverity
   > 0` → `human_arbitration`.
4. If `decisionType ∈ {compliance, security}` AND `unresolvedHighSeverity
   == 0` → `consensus` first; if consensus not reached →
   `judge_arbitration`; if judge arbitration drops a critical objection
   on retry → `human_arbitration`.
5. If `unresolvedHighSeverity > 0` (any decision type) →
   `judge_arbitration`. If judge arbitration drops a critical
   objection on retry → `human_arbitration`.
6. If overall confidence in any synthesised answer would be `< 0.5` →
   `human_arbitration`.

## Soft rules (apply if no hard rule matched)

| Decision type | Risk | Disagreement | Strategy |
|---|---|---|---|
| `reasoning` | low | none / minor | `majority_vote` |
| `reasoning` | low / medium | material | `confidence_weighted_vote` |
| `reasoning` | high | any | `consensus` then `judge_arbitration` |
| `architecture` | low / medium | none / minor | `majority_vote` |
| `architecture` | medium | material | `confidence_weighted_vote` |
| `architecture` | high | any | `judge_arbitration` |
| `architecture` | irreversible | any | `human_arbitration` |
| `migration` | low / medium | none / minor | `majority_vote` |
| `migration` | medium | material | `confidence_weighted_vote` |
| `migration` | high | any | `judge_arbitration` |
| `migration` | irreversible | any | `human_arbitration` |
| `knowledge-heavy` | any | none / minor | `consensus` |
| `knowledge-heavy` | any | material / split | `judge_arbitration` |
| `risk` | high / irreversible | any | `judge_arbitration` then human if needed |
| `operational` | low / medium | none / minor | `majority_vote` |
| `operational` | high / irreversible | any | `judge_arbitration` |
| `unknown` | any | any | `judge_arbitration` (judge synthesises across the disagreement) |

## Scoring rules per strategy

### `majority_vote`

Each persona's `finalPosition` is mapped to one option. A persona that
sets `finalPosition` to a verbatim option label votes for that option.
A persona whose `finalPosition` does not map to a declared option
abstains. The option with the most votes wins. Tie ⇒ escalate to
`confidence_weighted_vote`.

### `confidence_weighted_vote`

Each persona's vote is weighted by `finalConfidence`. The option with
the largest summed weight wins. If the winning option has `confidence
< 0.6` aggregate ⇒ escalate to `consensus` if feasible, else
`judge_arbitration`.

Reject the strategy if any persona has `finalConfidence > 0.85` AND
the critic flagged that persona's draft for unsupported overconfidence
in challenge round. In that case escalate to `judge_arbitration`.

### `consensus`

All personas converge on the same `finalPosition`. If any one
persona's `finalPosition` differs ⇒ no consensus ⇒ escalate to
`judge_arbitration`.

The judge produces an explicit consensus-reached artefact when this
strategy succeeds, with each persona's `finalConfidence` cited.

### `judge_arbitration`

The engine dispatches `debate-judge` in arbitration mode. The judge
must address every `severity: high|critical` challenge that survived
rebuttal in the `unresolvedObjectionsAddressed` field. The engine
rejects a judge output that drops one and retries. After one
rejection, escalation to `human_arbitration`.

### `human_arbitration`

The engine produces a `pending_human_approval` final artefact with:

- the `decisionQuestion` (verbatim from the brief);
- the options still viable;
- the unresolved objections;
- the recommended question for the human (`humanApprovalQuestion`);
- the redacted decision-criteria matrix from the evidence summary;
- the pointer to the audit trail (`auditTrailId` and full path tree).

The engine does not commit a decision. The user-facing report
explicitly states "Pending human approval — see audit trail".

## Commit-protocol selection

| Environment | `commitProtocol` |
|---|---|
| Standard local repo, single-team | `local_transactional` (default) |
| Trusted distributed environment with a registered Raft adapter | `raft` |
| Consortium / partially adversarial environment with a registered PBFT adapter | `pbft` |
| `policy.commitProtocol == "none"` | `none` (record-only, no commit) |
| `human_arbitration` strategy | `none` until human approves, then re-run commit step |

If the policy requests `raft` or `pbft` but no adapter is registered
in the calling environment, the engine falls back to
`local_transactional`, records the gap in the manifest's
`failureEvents`, and surfaces it in the final user-facing report.
Faking distributed consensus is forbidden.

## Worked examples

### Architecture decision, medium risk, balanced disagreement

`(architecture, medium, material, 0)` → `confidence_weighted_vote`.
Proposer 0.75 votes A, replatforming-specialist 0.7 votes A,
critic 0.65 votes B, risk-reviewer 0.6 votes A,
operations-reviewer 0.55 votes B. Sum A = 2.05; Sum B = 1.20. A wins.
Aggregate confidence ≈ 0.66 ⇒ accept.

### Migration decision, irreversible, no unresolved critical

`(migration, irreversible, _, 0)` → `human_arbitration`.

### Compliance decision, no unresolved critical

`(compliance, _, none, 0)` → `consensus` first; if reached, commit.

### Architecture decision, unresolved critical from critic

`(_, _, _, ≥1)` → `judge_arbitration`. Judge must address each
`severity: critical` objection in `unresolvedObjectionsAddressed`.
