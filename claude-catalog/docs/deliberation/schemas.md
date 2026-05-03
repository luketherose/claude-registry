# Deliberation — artefact schemas

Authoritative JSON schemas for every artefact under
`<repo>/.deliberation-kb/<trace-id>/`. The engine and personas validate
against these.

## Trace ID

Format: `del-YYYYMMDD-HHMMSS-<6hex>` (UTC, 6 hex chars from
`/dev/urandom`). Example: `del-20260503-143022-a3f9c1`.

## Directory tree

```
<repo>/.deliberation-kb/<trace-id>/
├── 00-decision-brief.json
├── 01-drafts/
│   ├── proposer.json
│   ├── critic.json
│   ├── replatforming-specialist.json   (5-persona only)
│   ├── risk-reviewer.json
│   └── operations-reviewer.json        (5-persona only)
├── 02-evidence-summary.json
├── 03-challenges/
│   ├── proposer.r1.json
│   ├── critic.r1.json
│   ├── ...
│   └── (round 2 if debateRounds: 2 — *.r2.json)
├── 04-rebuttals/
│   ├── proposer.json
│   ├── critic.json
│   └── ...
├── 05-final-decision.json
└── _meta/
    ├── manifest.json
    └── triggers.json
```

## Schemas

### `00-decision-brief.json`

```json
{
  "schemaVersion": "1.0",
  "traceId": "del-...",
  "decisionQuestion": "...",
  "context": "...",
  "options": [{"id": "A", "label": "...", "summary": "..."}],
  "constraints": ["..."],
  "successCriteria": ["..."],
  "knownFacts": [{"fact": "...", "source": "..."}],
  "unknowns": ["..."],
  "risks": [{"risk": "...", "likelihood": "low|med|high", "impact": "low|med|high"}],
  "reversibility": "reversible | partially_reversible | irreversible",
  "requiredEvidence": ["..."],
  "humanApprovalRequired": false,
  "decisionType": "reasoning | architecture | migration | knowledge-heavy | compliance | security | risk | operational | unknown",
  "riskLevel": "low | medium | high | irreversible",
  "policy": { /* deliberationPolicy after overrides */ },
  "migrationCriteria": {                         // optional, for replatforming
    "targetArchitecture": "...",
    "sourcePlatformConstraints": ["..."],
    "targetPlatformConstraints": ["..."],
    "dataMigrationRisk": "low|med|high",
    "integrationRisk": "low|med|high",
    "compatibilityRisk": "low|med|high",
    "downtimeOrCutoverRisk": "low|med|high",
    "securityComplianceImpact": "low|med|high",
    "rollbackStrategyRequired": true,
    "operationalBurdenAfter": "...",
    "testingValidationEffort": "...",
    "modernizationVsLiftAndShiftTradeoff": "...",
    "longTermMaintainability": "..."
  }
}
```

### `01-drafts/<role>.json`

```json
{
  "schemaVersion": "1.0",
  "agentRole": "proposer | critic | replatforming-specialist | risk-reviewer | operations-reviewer",
  "model": "claude-...-opus-...",
  "writtenAt": "2026-05-03T14:30:22Z",
  "recommendation": "...",
  "rationale": ["..."],
  "evidence": [{"claim": "...", "source": "<file:line | doc-path | metric-id>", "kind": "code|doc|metric|prior-decision"}],
  "assumptions": ["..."],
  "risks": [{"risk": "...", "likelihood": "low|med|high", "impact": "low|med|high", "mitigation": "..."}],
  "tradeoffs": [{"axis": "...", "pro": "...", "con": "..."}],
  "openQuestions": ["..."],
  "confidence": 0.0,
  "confidenceRationale": "...",
  "conditionsForChangingMind": ["..."],

  // Optional, persona-specific blocks:
  "migrationCriteria": { /* see 00-brief schema */ },
  "riskFlags": {
    "requiresJudgeArbitration": false,
    "requiresHumanArbitration": false,
    "reasons": ["..."]
  },
  "complianceAssessment": [
    {"regime": "GDPR|HIPAA|PCI|SOX|contractual|...", "articles": ["..."], "verdict": "compliant|conditional|non-compliant", "evidence": "..."}
  ],
  "operationalAssessment": [
    {"option": "...", "slo": "...", "capacity": {"peakRps": 0, "headroomFactor": 0},
     "rto": "...", "rpo": "...", "observabilityRequirements": ["..."],
     "knownFailureModes": ["..."], "operationalCostUsdMonthly": 0}
  ]
}
```

Required fields for every draft: `schemaVersion`, `agentRole`, `model`,
`writtenAt`, `recommendation`, `rationale`, `evidence`, `assumptions`,
`risks`, `confidence`, `confidenceRationale`,
`conditionsForChangingMind`. Persona-specific blocks are required for
their owning persona (e.g. `riskFlags` is required from
`debate-risk-reviewer`).

### `02-evidence-summary.json`

```json
{
  "schemaVersion": "1.0",
  "writtenBy": "debate-judge",
  "model": "claude-...-opus-...",
  "writtenAt": "...",
  "areasOfAgreement": ["..."],
  "areasOfDisagreement": [
    {"topic": "...", "positions": [{"role": "proposer", "position": "..."}, ...]}
  ],
  "strongestEvidence": [{"claim": "...", "source": "...", "rating": "strong"}],
  "weakestEvidence": [{"claim": "...", "source": "...", "rating": "weak|absent"}],
  "unsupportedClaims": [{"claim": "...", "fromRole": "...", "reason": "..."}],
  "criticalRisks": [{"risk": "...", "fromRole": "...", "severity": "high|critical"}],
  "decisionCriteriaMatrix": [
    {"criterion": "...", "<optionId>": "<assessment>"}
  ],
  "optionsStillViable": ["<optionId>"],
  "optionsRejected": [{"option": "<optionId>", "reason": "...", "byRole": "..."}],
  "missingInformation": ["..."]
}
```

The summary MUST NOT contain a `recommendation`, `selectedOption`, or
any field that resolves the disagreement. The engine rejects a summary
that violates this rule.

### `03-challenges/<role>.r<N>.json`

```json
{
  "schemaVersion": "1.0",
  "agentRole": "...",
  "model": "...",
  "round": 1,
  "writtenAt": "...",
  "challenges": [
    {
      "targetRole": "proposer | critic | replatforming-specialist | risk-reviewer | operations-reviewer",
      "targetClaim": "...",
      "issue": "...",
      "severity": "low | medium | high | critical",
      "evidenceOrReasoning": "...",
      "suggestedCorrection": "..."
    }
  ],
  "revisedRecommendation": "...",
  "revisedConfidence": 0.0
}
```

### `04-rebuttals/<role>.json`

```json
{
  "schemaVersion": "1.0",
  "agentRole": "...",
  "model": "...",
  "writtenAt": "...",
  "responses": [
    {
      "challengeFrom": "<role>",
      "round": 1,
      "challenge": "...",
      "response": "...",
      "accepted": true,
      "impactOnRecommendation": "none | minor | material | changes_decision"
    }
  ],
  "finalPosition": "...",
  "finalConfidence": 0.0
}
```

### `05-final-decision.json`

```json
{
  "schemaVersion": "1.0",
  "writtenBy": "deliberative-decision-engine | debate-judge",
  "model": "...",
  "writtenAt": "...",
  "auditTrailId": "del-...",
  "status": "decided | pending_human_approval | failed_insufficient_drafts | failed_other",

  "decision": "...",
  "decisionType": "...",
  "selectedOption": "<optionId>",
  "rejectedOptions": [{"option": "<optionId>", "reason": "..."}],
  "rationale": ["..."],
  "evidenceSummary": ["..."],
  "majorDisagreements": ["..."],
  "dissentingOpinions": [{"role": "...", "finalPosition": "...", "finalConfidence": 0.0}],
  "riskAssessment": [{"risk": "...", "severity": "low|med|high|critical", "mitigation": "..."}],
  "confidence": 0.0,
  "confidenceRationale": "...",
  "requiredHumanApproval": false,
  "humanApprovalQuestion": "...",        // when requiredHumanApproval == true

  "validationPlan": ["..."],
  "rollbackPlan": ["..."],
  "implementationPlan": ["..."],

  "decisionStrategyUsed": "majority_vote | confidence_weighted_vote | consensus | judge_arbitration | human_arbitration",
  "commitProtocol": "none | local_transactional | raft | pbft",
  "commitResult": {"committedAt": "...", "committerVersion": "...", "notes": "..."},

  "unresolvedObjectionsAddressed": [
    {"fromRole": "...", "objection": "...", "severity": "high|critical",
     "addressedBy": "rebuttal | judge-synthesis | escalation", "resolution": "..."}
  ]
}
```

Required when `decisionStrategyUsed == "judge_arbitration"`:
`unresolvedObjectionsAddressed` must include every challenge of
`severity: high | critical` that survived the rebuttal round.

### `_meta/manifest.json`

```json
{
  "schemaVersion": "1.0",
  "traceId": "del-...",
  "createdAt": "...",
  "updatedAt": "...",
  "policy": { /* effective deliberationPolicy */ },
  "personas": [
    {"role": "proposer", "agent": "debate-proposer", "model": "..."}
  ],
  "steps": [
    {"step": 0, "name": "trigger-detect-classify", "startedAt": "...", "endedAt": "...", "status": "ok|failed"},
    {"step": 1, "name": "decision-framing", "startedAt": "...", "endedAt": "...", "status": "ok"},
    {"step": 2, "name": "independent-drafts", "startedAt": "...", "endedAt": "...", "status": "ok",
     "draftsCompleted": 5, "draftsFailed": 0, "retries": 0},
    {"step": 3, "name": "evidence-summary", "startedAt": "...", "endedAt": "...", "status": "ok"},
    {"step": 4, "name": "challenge-round-1", "startedAt": "...", "endedAt": "...", "status": "ok"},
    {"step": 5, "name": "rebuttal-round", "startedAt": "...", "endedAt": "...", "status": "ok"},
    {"step": 6, "name": "convergence-and-commit", "startedAt": "...", "endedAt": "...", "status": "ok"}
  ],
  "artefacts": ["00-decision-brief.json", "01-drafts/proposer.json", "..."],
  "redactionApplied": ["secret patterns redacted: AWS_*, password=, Bearer, JWT-like, ..."],
  "failureEvents": []
}
```

### `_meta/triggers.json`

```json
{
  "deliberativeModeRequested": true,
  "matchedTriggers": ["dibattito", "critica"],
  "confidence": 0.92,
  "source": "user_prose | programmatic_flag | high_risk_escalation",
  "rawUtterance": "...",                  // redacted of PII
  "decisionAt": "..."
}
```
