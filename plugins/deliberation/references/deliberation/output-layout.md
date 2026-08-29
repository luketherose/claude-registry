# Deliberation — output layout

The full artefact tree under `<repo>/.deliberation-kb/<trace-id>/`,
file frontmatter contracts, and audit-trail conventions.

## Tree

```
<repo>/.deliberation-kb/
└── del-20260503-143022-a3f9c1/
    ├── 00-decision-brief.json
    ├── 01-drafts/
    │   ├── proposer.json
    │   ├── critic.json
    │   ├── replatforming-specialist.json     (5-persona)
    │   ├── risk-reviewer.json
    │   └── operations-reviewer.json          (5-persona)
    ├── 02-evidence-summary.json
    ├── 03-challenges/
    │   ├── proposer.r1.json
    │   ├── critic.r1.json
    │   ├── replatforming-specialist.r1.json  (5-persona)
    │   ├── risk-reviewer.r1.json
    │   └── operations-reviewer.r1.json       (5-persona)
    │   └── *.r2.json                         (only when debateRounds: 2)
    ├── 04-rebuttals/
    │   ├── proposer.json
    │   ├── critic.json
    │   ├── replatforming-specialist.json     (5-persona)
    │   ├── risk-reviewer.json
    │   └── operations-reviewer.json          (5-persona)
    ├── 05-final-decision.json
    ├── 06-user-report.md                     (the rendered report)
    └── _meta/
        ├── manifest.json                     (the audit-trail spine)
        ├── triggers.json                     (Step 0 detection record)
        └── failures.log                      (one line per failure event)
```

## Audit trail and manifest

`_meta/manifest.json` is the audit-trail spine. It MUST be updated:

- after Step 0 (trigger + classification recorded);
- after Step 1 (brief written);
- after each persona returns in Step 2, 4, 5;
- after Step 3 (judge summary written);
- after Step 6 (final decision written + commit result recorded).

The manifest MUST record:
- trace ID;
- timestamps per step (`startedAt`, `endedAt`);
- effective `policy` (after overrides);
- every persona's role + agent name + model identifier returned by the
  dispatch;
- every artefact's relative path + SHA-256;
- failure events (retry, fallback, judge rejection, etc.);
- redaction operations applied (with the pattern names, not the
  redacted content).

## Redaction

Sensitive content (secrets, credentials, regulated personal data) is
redacted from all artefacts before they are written. If the calling
environment provides a redaction utility, use it. Otherwise, redact
these patterns:

- `AWS_*=...`, `AZURE_*=...`, `GOOGLE_APPLICATION_CREDENTIALS=...`
- `password=`, `passwd=`, `secret=`, `token=`, `api[_-]?key=`
- `Bearer <eyJ...>`, JWT-shaped values
- RFC 5322 emails when flagged as PII by the caller
- IBAN, IT/EU fiscal codes, US SSN-shaped strings, credit-card numbers
  matching the standard 13–19 digit pattern with Luhn

Replace with `<redacted:<pattern-name>>` (e.g., `<redacted:bearer>`).

The list of redaction patterns applied is recorded in the manifest's
`redactionApplied` field. The redacted patterns themselves are NEVER
recorded in plaintext.

## Re-runs

Re-running the engine for the same decision (for instance after a
human approver returns the decision to the engine for one more round)
creates a NEW trace ID. The previous trace is preserved on disk.
Cross-link in the manifest:

```json
"previousTraceId": "del-20260503-090000-fe10ab",
"reason": "human-arbitration-returned-with-new-evidence"
```

## Cleanup

Trace directories are NOT auto-deleted. Operators decide retention
based on their compliance regime. The engine writes a `.gitkeep`-style
marker to make the directory visible; the actual artefacts are JSON
files that the caller's normal git workflow can commit or .gitignore
as appropriate to the project.

For repos using the `refactoring-supervisor` workflow, the suggested
default in `.gitignore` is:

```
.deliberation-kb/                  # comment in or out per policy
```

By default, deliberation artefacts ARE checked in alongside the rest
of the refactoring KB so that the audit trail follows the code.
