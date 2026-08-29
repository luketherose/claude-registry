# Deliberative Decision Engine: Supervisor Protocol

Read this document when executing any step of the 7-step deliberative
pipeline. It contains: inputs contract, default policy, full per-step
execution rules, final-report schema, failure-handling rules, and hard
constraints. Do not preemptively load. Read on demand per step.

---

## Contents

- [Pipeline state](#pipeline-state): the `pipeline-state.yaml` file, its bootstrap and update protocol, and its schema.
- [Inputs contract](#inputs-contract): what the caller must supply: decision question, context, options and the optional policy.
- [Default deliberation policy](#default-deliberation-policy): the default policy object, and the rule that any override is documented in the manifest.
- [Step 0: Trigger detection and task classification](#step-0-trigger-detection-and-task-classification): trigger detection against the IT/EN lexicon, and classification of the decision type.
- [Step 1: Decision framing (decision brief)](#step-1-decision-framing-decision-brief): producing the structured decision brief.
- [Step 2: Independent persona drafts (anti-anchoring)](#step-2-independent-persona-drafts-anti-anchoring): the parallel persona dispatch that keeps drafts unanchored.
- [Step 3: Neutral structured evidence summary](#step-3-neutral-structured-evidence-summary): the judge in summariser mode, producing evidence without deciding.
- [Step 4: Challenge round](#step-4-challenge-round): each persona attacks the others, given the brief, the summary and every draft.
- [Step 5: Rebuttal round](#step-5-rebuttal-round): each persona answers the challenges addressed at it.
- [Step 6: Convergence and final decision](#step-6-convergence-and-final-decision): strategy selection and the hard rules that force human arbitration.
- [Final user-facing report (mandatory)](#final-user-facing-report-mandatory): the mandatory Markdown report sections, in order.
- [Failure handling](#failure-handling): retries, the minimum viable draft count, and the abort conditions.
- [Constraints (hard rules)](#constraints-hard-rules): the non-negotiables: model tier, draft isolation and artefact immutability.

## Pipeline state

**File**: `.deliberation-kb/<trace-id>/pipeline-state.yaml`

The deliberation engine uses a step-based state (not wave-based). The `trace-id` is generated at trigger detection (Step 0) and used for all outputs of that deliberation run.

### Bootstrap protocol
1. Check for an existing `.deliberation-kb/` directory with an incomplete trace.
   - Found with `status: in-progress` → ask user: resume / restart. Never auto-resume.
   - Not found → generate `trace-id` (timestamp + 8-char hex), create directory and state file at Step 0.
2. Each step updates `current_step` and `steps.<N>.status` before and after execution.

### Update protocol
Write `pipeline-state.yaml` after each step completes. Step outputs (drafts, challenges, rebuttals, final decision) are individual files in `.deliberation-kb/<trace-id>/`; the state file is the index.

### Schema
```yaml
phase: "Deliberation"
trace_id: "<timestamp>-<8hex>"
decision_brief: ".deliberation-kb/<trace-id>/00-decision-brief.json"
started_at: "<ISO 8601>"
last_updated_at: "<ISO 8601>"
status: "in-progress"        # pending | in-progress | complete | aborted
current_step: 2
persona_count: 3             # 3 or 5
steps:
  "0":
    name: trigger-detection
    status: complete
  "1":
    name: decision-framing
    status: complete
    output: .deliberation-kb/<trace-id>/00-decision-brief.json
  "2":
    name: independent-drafts
    status: in-progress
    personas: [debate-proposer, debate-critic, debate-risk-reviewer]
    outputs: []
  "3":
    name: evidence-summary
    status: pending
    output: .deliberation-kb/<trace-id>/02-evidence-summary.json
  "4":
    name: challenge-round
    status: pending
  "5":
    name: rebuttal-round
    status: pending
  "6":
    name: convergence
    status: pending
    strategy: null            # majority | confidence_weighted | consensus | judge_arbitration | human
    output: .deliberation-kb/<trace-id>/06-final-decision.json
require_human_approval: false
```

---

## Inputs contract

- **Decision question** (string, required): what must be decided.
- **Context** (string, required): the situation and what you have read.
- **Options** (list, optional): if pre-enumerated; otherwise the proposer enumerates.
- **Constraints** (list, optional): hard limits on viable options.
- **Risk level** (`low | medium | high | irreversible`, optional, inferred otherwise).
- **`deliberationPolicy`** (object, optional; see schema below; defaults applied if omitted).

Read all available repository state relevant to the decision before framing:
`.indexing-kb/`, `docs/analysis/01-functional/`, `docs/analysis/02-technical/`,
`docs/analysis/03-baseline/`, `docs/refactoring/`, ADRs, and any source files
cited by the caller.

---

## Default deliberation policy

```yaml
enabled: true                          # always when this agent is invoked
agentCount: 5                          # 3 if decision is simple/well-scoped
debateRounds: 1                        # 2 for high-risk or highly ambiguous
requireIndependentDrafts: true
requireStructuredEvidenceSummary: true
requireDissentingOpinion: true
finalDecisionStrategy: "auto"          # selected per task type + risk
commitProtocol: "auto"                 # local_transactional unless infra exists
prioritizeQualityOverCost: true
preferredModelTier: "opus"
requireHumanApprovalForHighRisk: true
```

Override only when the caller passes an explicit `deliberationPolicy` object.
Document any override in the audit manifest.

---

## Step 0: Trigger detection and task classification

When invoked from raw user prose, run the trigger detector before anything
else. Match against the IT/EN trigger lexicon in
`${CLAUDE_PLUGIN_ROOT}/references/deliberation/trigger-lexicon.md`. Output a JSON detection
record:

```json
{
  "deliberativeModeRequested": true,
  "matchedTriggers": ["dibattito", "critica"],
  "confidence": 0.92,
  "source": "user_prose | programmatic_flag | high_risk_escalation"
}
```

Refuse to over-trigger on casual mentions ("we should debate this later",
"the team is critical of X"). Trigger only when the user is clearly asking
the system to use deliberation, debate, critique, red-team review,
multi-agent decision-making, or a robust decision process. If unsure, state
the ambiguity and proceed standard. Do not auto-deliberate.

If `decisionMode: deliberative` is set in the dispatch JSON, skip prose
detection and treat the request as confirmed.

Then classify the decision type:

| Type | Examples |
|---|---|
| `reasoning` | Algorithmic / analytical question with a verifiable answer |
| `architecture` | Component decomposition, integration pattern, target stack |
| `migration` | Lift-and-shift vs refactor vs rearchitect, sequencing, cutover |
| `knowledge-heavy` | Factual / regulatory / framework-specific synthesis |
| `compliance` | GDPR, HIPAA, PCI, SOX, contractual obligations |
| `security` | Authn/authz design, secrets, threat-model decisions |
| `risk` | Operational / financial / reputational risk trade-off |
| `operational` | Capacity, SLO, observability, runtime topology |
| `unknown` | Mixed or insufficient signal |

Determine `riskLevel`: `low | medium | high | irreversible`. Production-impacting,
regulated-data-impacting, contractual-impacting, or data-loss-capable decisions
are at minimum `high`.

Pick `agentCount` (3 for simple/well-scoped lower-risk decisions; 5 by default
and always for `high` / `irreversible`) and `debateRounds` (1 default; 2 for
`high` / `irreversible` or for highly ambiguous tasks with `unknown` type). Pick
`finalDecisionStrategy` and `commitProtocol` per the rules in
`docs/deliberation/strategy-selection.md`.

---

## Step 1: Decision framing (decision brief)

Produce the structured brief at
`<repo>/.deliberation-kb/<trace-id>/00-decision-brief.json`. Schema in
`docs/deliberation/schemas.md`. For replatforming-relevant decisions add the
migration-specific criteria block (target architecture, source/target platform
constraints, data migration risk, integration risk, compatibility risk, cutover
risk, security/compliance impact, reversibility / rollback strategy, operational
burden, testing/validation effort, modernization vs lift-and-shift trade-off,
long-term maintainability).

The brief is the single source of truth for every persona. They read it before
drafting; you never let them anchor on each other's output.

---

## Step 2: Independent persona drafts (anti-anchoring)

Dispatch 3 or 5 personas **in a single message with multiple Agent calls in
parallel**. Each persona receives only the decision brief, never any other
persona's output. Personas are dispatched as separate `Agent` calls so they
cannot see each other's running context.

5-persona default roster:
- `debate-proposer`: Primary Architect / Proposer
- `debate-critic`: Skeptical Critic
- `debate-replatforming-specialist`: Migration / Replatforming Specialist
- `debate-risk-reviewer`: Security / Compliance / Risk Reviewer
- `debate-operations-reviewer`: Operations / Reliability Reviewer

3-persona reduced roster (only when policy `agentCount: 3`):
- `debate-proposer`
- `debate-critic`
- `debate-risk-reviewer` (acts as combined risk + replatforming reviewer)

Each persona writes its draft to
`<repo>/.deliberation-kb/<trace-id>/01-drafts/<role>.json` following the draft
schema in `docs/deliberation/schemas.md`.

Anti-anchoring rule (hard): never share a draft until **all** drafts of this
round are on disk. If any persona fails to produce a draft, retry once with the
same prompt; if it still fails, record the failure in the manifest and either
continue with the remaining personas (only if `agentCount` stays ≥ 3) or abort
with a failure artefact (never silently proceed with fewer than 3 drafts).

---

## Step 3: Neutral structured evidence summary

Dispatch `debate-judge` in summariser mode. It reads all drafts and produces
`02-evidence-summary.json` per the schema. The judge does **not** decide at
this stage. It only structures areas of agreement, disagreement, strongest /
weakest evidence, unsupported claims, critical risks, decision-criteria matrix,
options still viable, options rejected, and missing information. Refuse a judge
output that contains a recommendation in this step; reject and retry.

---

## Step 4: Challenge round

Dispatch all personas in parallel again, this time giving each one (a) the
decision brief, (b) the evidence summary, (c) every other persona's draft. Each
produces a challenge artefact at `03-challenges/<role>.json` per the challenge
schema in `docs/deliberation/schemas.md`. Severity must be
`low | medium | high | critical`.

If `debateRounds == 2`, run a second challenge round after Step 5 rebuttals so
personas can challenge the rebuttals. Both rounds are stored under
`03-challenges/` with round suffixes (`<role>.r1.json`, `<role>.r2.json`).

---

## Step 5: Rebuttal round

Dispatch all personas again, in parallel. Each receives the challenges addressed
at it and produces a rebuttal artefact at `04-rebuttals/<role>.json` per the
rebuttal schema. Each rebuttal records which challenges were accepted, the impact
on the recommendation, the final position, and the final confidence.

---

## Step 6: Convergence and final decision

Pick the final-decision strategy according to the rules in
`docs/deliberation/strategy-selection.md`. Hard rules:

- **Compliance / security / legal / privacy / irreversible / production-impacting**
  decisions: use `consensus` plus `judge_arbitration`. If consensus is not reached,
  escalate to `human_arbitration`.
- **Architecture / migration with unresolved high-severity objections**: use
  `judge_arbitration`. If a judge arbitration ignores an unresolved critical
  objection, reject the judge output and escalate to human.
- **Reasoning-heavy / lower-risk / well-defined options / no unresolved critical
  objections**: `majority_vote` or `confidence_weighted_vote` (latter only if
  confidence rationales are explicit and not obviously overconfident).
- **Knowledge-heavy with factual uncertainty**: `consensus` or
  `judge_arbitration`; do not rely only on simple voting.
- **Low confidence / insufficient evidence**: the final output must say so; do
  not produce an overconfident answer.

For `judge_arbitration`, dispatch `debate-judge` in arbitration mode with all
artefacts. The judge produces a synthesis that explicitly addresses each
unresolved high-severity objection. Refuse a judge output that silently drops
one.

For `human_arbitration`, produce the final artefact in `pending_human_approval`
status with the unresolved objections, the options still viable, and the
recommended question for the human. Do not issue a decision.

Write the final decision to `05-final-decision.json` per the final-decision
schema. Required fields: `decision`, `decisionType`, `selectedOption`,
`rejectedOptions`, `rationale`, `evidenceSummary`, `majorDisagreements`,
`dissentingOpinions`, `riskAssessment`, `confidence`, `confidenceRationale`,
`requiredHumanApproval`, `validationPlan`, `rollbackPlan`, `implementationPlan`,
`commitProtocol`, `auditTrailId`. Dissent is **mandatory** when any persona's
final position differs from the selected option. Never claim consensus when it
does not exist.

Then run the **decision committer** for the chosen `commitProtocol`. The
committer is an abstraction (`docs/deliberation/commit-protocol.md`): default
`local_transactional`, with `raft` and `pbft` extension points that must not be
faked. Record the actual protocol in the artefact.

Finally, append a manifest entry at `_meta/manifest.json` with: trace ID,
timestamps per step, persona model identifiers, policy used (after overrides),
failure events, and the path to every artefact.

---

## Final user-facing report (mandatory)

After Step 6, output a Markdown report to the user with these sections, in this
order:

1. **Decision**: what was decided (one-liner).
2. **Why**: rationale, evidence summary.
3. **Alternatives considered**: option-by-option with why-rejected.
4. **Objections raised**: by severity, who raised them, what happened.
5. **Objections that changed the decision**: explicit list (or "none").
6. **Dissenting opinions**: preserved verbatim, with persona identity.
7. **Residual risks**: what remains after the decision.
8. **Validation plan**: how we will know it worked.
9. **Rollback plan**: how we revert if it didn't.
10. **Human approval**: required (yes/no) and why; if pending, the explicit
    question for the human.
11. **Audit trail**: the trace ID and the path tree.

Never compress this report on grounds of cost / latency.

---

## Failure handling

- **Persona dispatch failure**: retry once. If still failing, record in
  manifest. Continue only if remaining drafts are ≥ 3. Otherwise abort with a
  failure artefact at `05-final-decision.json` with status
  `failed_insufficient_drafts` and a clear explanation. Never silently fall back
  to single-agent decisioning.
- **Judge ignores unresolved objection**: reject the judge output, retry once
  with explicit instruction to address the objection, then escalate to
  `human_arbitration` if the second pass also fails.
- **Trigger ambiguity**: if the prose trigger detector returns
  `confidence < 0.7`, ask the user one focused clarifying question
  ("Vuoi che usi il dibattito multi-agente o una risposta diretta?"). Do not
  auto-trigger.
- **Deliberative mode requested but cannot complete** (e.g., file system
  read-only, persona unavailable): produce a failure artefact and a clear
  user-facing message. Never pretend the decision was made.

---

## Constraints (hard rules)

- Default model tier for every persona is `opus`. Override only via explicit
  policy.
- Personas never see each other's drafts in Step 2.
- Drafts, challenges, rebuttals, summaries, and the final decision are all
  written to disk before responding to the user.
- Dissent is preserved when present; consensus is not faked.
- Commit protocol `raft` / `pbft` is only honoured if the repository or caller
  environment provides a real adapter; otherwise the engine records the request,
  falls back to `local_transactional`, and surfaces the gap in the audit
  artefact.
- Sensitive content (secrets, credentials, regulated personal data) is redacted
  from all artefacts using whatever redaction utility the repository already
  provides; if none exists, redact obvious patterns (`AWS_*`, `password=`,
  `Bearer `, JWT-like blobs, RFC 5322 emails when flagged as PII by the caller)
  and note the limitation in the manifest.
