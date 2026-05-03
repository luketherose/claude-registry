# Deliberation — dispatch prompt templates

Boilerplate the engine uses when dispatching personas via the `Agent`
tool. Copy-adapt; do not paraphrase the hard rules.

## Step 2 — independent draft (5-persona dispatch, parallel)

The engine sends ONE message with five `Agent` calls (one per persona).
Each call is fully self-contained. Order in the message is irrelevant —
they run concurrently.

```
You are dispatched as <role> in a multi-agent deliberation.

Trace ID: del-20260503-143022-a3f9c1
Working directory: /path/to/repo
Step: 2 (independent draft)
Round: 1
Deliberation policy: <effective policy JSON>

ANTI-ANCHORING — HARD RULE
You MUST NOT read any of these files in this step:
  .deliberation-kb/del-.../01-drafts/<other-role>.json
Reading another persona's draft is a protocol violation.

Read these files first:
  - .deliberation-kb/del-.../00-decision-brief.json (always)
  - any source-of-truth files cited in the brief

Then write your draft to:
  .deliberation-kb/del-.../01-drafts/<role>.json

Schema: see claude-catalog/docs/deliberation/schemas.md
        § "01-drafts/<role>.json"

Persona-specific blocks required for <role>:
  - proposer: rationale, evidence, tradeoffs, openQuestions
  - critic: assumption audit, failure modes, edge cases, evidence audit
  - replatforming-specialist: migrationCriteria block
  - risk-reviewer: riskFlags, complianceAssessment
  - operations-reviewer: operationalAssessment

Confidence: 0.0–1.0; confidenceRationale required;
            conditionsForChangingMind required.

Return only:
  WROTE: <artefact-path>
```

## Step 3 — judge summarisation (single dispatch, sequential)

```
You are debate-judge dispatched in SUMMARISER mode.

Trace ID: del-...
Step: 3
Round: n/a

Read every file under:
  .deliberation-kb/del-.../01-drafts/

Then write the structured evidence summary to:
  .deliberation-kb/del-.../02-evidence-summary.json

HARD RULE: do NOT recommend an option, do NOT pick a winner, do NOT
resolve any disagreement. Your job is to make the disagreement legible.

Schema: see claude-catalog/docs/deliberation/schemas.md
        § "02-evidence-summary.json"

Return only:
  WROTE: <artefact-path>
```

## Step 4 — challenge round (parallel dispatch)

The engine sends ONE message with N `Agent` calls (one per persona).

```
You are dispatched as <role> in a multi-agent deliberation.

Trace ID: del-...
Step: 4 (challenge)
Round: <1 or 2>

Read these files:
  - .deliberation-kb/del-.../00-decision-brief.json
  - .deliberation-kb/del-.../01-drafts/*.json (all of them now)
  - .deliberation-kb/del-.../02-evidence-summary.json
  - if round 2: also .deliberation-kb/del-.../04-rebuttals/*.json

Then write your challenges to:
  .deliberation-kb/del-.../03-challenges/<role>.r<round>.json

Schema: see claude-catalog/docs/deliberation/schemas.md
        § "03-challenges/<role>.r<N>.json"

HARD RULE: every challenge must have targetClaim, issue, severity,
evidenceOrReasoning, suggestedCorrection. Severity is one of
{low, medium, high, critical}.

Return only:
  WROTE: <artefact-path>
```

## Step 5 — rebuttal round (parallel dispatch)

```
You are dispatched as <role> in a multi-agent deliberation.

Trace ID: del-...
Step: 5 (rebuttal)
Round: 1

Read these files:
  - .deliberation-kb/del-.../00-decision-brief.json
  - .deliberation-kb/del-.../01-drafts/<role>.json (your own draft)
  - the challenges that target you (filter
    .deliberation-kb/del-.../03-challenges/*.json by targetRole == "<role>")

Then write your rebuttal to:
  .deliberation-kb/del-.../04-rebuttals/<role>.json

Schema: see claude-catalog/docs/deliberation/schemas.md
        § "04-rebuttals/<role>.json"

HARD RULE: respond to every challenge aimed at you. State accepted
true/false explicitly. Do not capitulate on a critical objection without
new evidence.

Return only:
  WROTE: <artefact-path>
```

## Step 6 — judge arbitration (single dispatch, sequential)

Only when the chosen `finalDecisionStrategy == "judge_arbitration"`.

```
You are debate-judge dispatched in ARBITRATION mode.

Trace ID: del-...
Step: 6 (final synthesis)

Read every file under .deliberation-kb/del-.../ — drafts, evidence
summary, all challenge rounds, all rebuttals, the manifest.

Then write the final decision to:
  .deliberation-kb/del-.../05-final-decision.json

Schema: see claude-catalog/docs/deliberation/schemas.md
        § "05-final-decision.json"

HARD RULE: every challenge of severity high|critical that survived
rebuttal MUST appear in unresolvedObjectionsAddressed. If you cannot
address one on the available evidence, set addressedBy: "escalation"
and requiredHumanApproval: true with the explicit humanApprovalQuestion.

HARD RULE: dissentingOpinions must list every persona whose
finalPosition differs from selectedOption. Do not fake consensus.

HARD RULE: respect requiresHumanArbitration: true if any persona's
draft set it.

Return only:
  WROTE: <artefact-path>
```

## Failure-handling templates

### Persona retry (after first dispatch failure)

```
RETRY — your previous dispatch (step <N>, round <R>) failed with:
  <failure reason from manifest>

Rerun the same step. Same anti-anchoring rules. Address the failure
reason explicitly in the artefact.
```

### Judge re-dispatch after dropped objection

```
REJECTED — your previous arbitration output dropped these objections:
  - <fromRole>: <objection> (severity: <severity>)
  - ...

Re-emit the final decision with each of these in
unresolvedObjectionsAddressed. If you cannot address one on the
evidence, set addressedBy: "escalation" and produce a
pending_human_approval artefact.
```
