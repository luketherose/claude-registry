# API contract designer — output / reporting templates

> Reference doc for `api-contract-designer`. Read at runtime when assembling
> the design-rationale document and the supervisor-facing report. The agent
> body keeps the canonical list of paths under `## Outputs`; this doc holds
> the full markdown skeletons.

## File: `docs/refactoring/4.6-api/design-rationale.md`

```markdown
---
agent: api-contract-designer
generated: <ISO-8601>
sources: [...]
related_ucs: [UC-01, UC-02, ...]
related_bcs: [BC-01, BC-02, ...]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# API design rationale

## Overview
- Total endpoints: <N>
- Bounded contexts represented: <N>
- Use cases covered: <N>/<M> (gap: <K> UCs not surfaced as REST —
  documented below)
- Auth: <scheme> (see ADR-003)
- Spectral validation: pass | fail | unavailable

## Versioning
- Path-based: /v1/, /v2/...
- Bug-fix and additive changes: same version
- Breaking change: bump to /v2/

## Error format
- RFC 7807 ProblemDetail
- correlationId field for cross-cutting trace
- no internal info leaks (no stack, no SQL, no file path)

## Pagination
- Cursor-based by default
- `cursor` opaque string; servers MAY use base64-encoded sort+id
- `limit` 1–200, default 50

## Idempotency
- Required on POST endpoints with side effects
- Header `Idempotency-Key`
- Window: 24h
- Same key + same body → original response
- Same key + different body → 409 Conflict

## Use cases not exposed as REST

Some Phase 1 UCs are NOT direct REST endpoints. They are listed here
with the chosen surface:

| UC-NN | Surface | Rationale |
|---|---|---|
| UC-12 | scheduled job | batch run, no user trigger |
| UC-15 | server-side composition | multiple internal calls; no single endpoint |

## Open questions
- ...
```

## File: `docs/refactoring/4.6-api/postman-tobe.json`

Postman 2.1 schema, mirrors AS-IS collection structure (from
`tests/baseline/postman/` if present) for parity testing in Phase 5.
Every endpoint becomes a request with happy + edge cases.

## Reporting skeleton (text response to supervisor)

```markdown
## Files written
- docs/refactoring/4.6-api/openapi.yaml (<endpoint count>)
- docs/refactoring/4.6-api/design-rationale.md
- docs/refactoring/4.6-api/postman-tobe.json
- docs/adr/ADR-003-auth-flow.md

## Contract stats
- Endpoints:        <N>
- Resources:        <N>
- BCs covered:      <N>/<total>
- UCs covered:      <N>/<M>
- UCs deferred:     <K>  (reason: not REST-able — see rationale)
- Spectral:         pass | fail | unavailable

## Auth
- Scheme: <chosen>
- Token TTL: <time>

## Confidence
high | medium | low

## Duration (wall-clock)
<seconds>

## Open questions
- ...
```
