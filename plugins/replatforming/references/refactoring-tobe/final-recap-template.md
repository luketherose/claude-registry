# Phase 4 — Final recap template

> Reference doc for `refactoring-tobe-supervisor`. Read at runtime when producing the closing report after Wave 6 (or after the export wave if `--with-exports` was set). Standard recap with execution timings (per-wave + per-agent within W3 fan-out + total + cumulative across phases).

```
Phase 4 TO-BE Refactoring — complete.

Output (TO-BE KB):  .refactoring-kb/
Output (docs):      docs/refactoring/
Output (backend):   <backend-dir>/
Output (frontend):  <frontend-dir>/
Output (ADRs):      docs/adr/ADR-001 .. ADR-005

Decomposition:
- Bounded contexts:           <N>
- AS-IS modules mapped:       <covered>/<total>
- Aggregates designed:        <N>

API:
- OpenAPI endpoints:          <N>
- Auth scheme:                <Bearer JWT | OAuth2 | mTLS>
- Spectral validation:        <pass | fail | unavailable>

Backend (Spring Boot):
- Java packages:              <N>
- Controllers:                <N>
- Services:                   <N>
- JPA entities:               <N>
- Liquibase changesets:       <N>
- Verification:               <mvn compile pass | fail | skipped>

Frontend (Angular):
- Lazy modules:               <N>
- Components:                 <N>
- Verification:               <ng build pass | fail | skipped>

Hardening:
- ADRs added:                 ADR-004, ADR-005
- Observability:              JSON logging, correlation-id, Micrometer, OTel

Code review (background):
- Findings (blocking):        <N>
- Findings (suggestions):     <N>
  (see _meta/code-review-findings.md)

Traceability (AS-IS↔TO-BE):
- UCs covered:                <N>/<M>
- Orphan UCs:                 <N>  (must be 0 for status: complete)
- Orphan TO-BE files:         <N>

Per-wave timings:
- Wave 1 (decomposition):     <duration>
- Wave 2 (API contract):      <duration>
- Wave 3 (implementation):    <duration>   (BE: <d>, FE: <d>, parallel envelope)
- Wave 4 (hardening):         <duration>
- Wave 5 (roadmap):           <duration>
- Wave 6 (challenger):        <duration>
- Export wave:                <duration | skipped>
- Total:                      <duration>

Quality:
- Open questions:             <N>  (see unresolved-tobe.md)
- Low-confidence sections:    <N>
- Challenger findings:        <N>  (blocking | needs-review | nice-to-have)
- AS-IS bugs carried over:    <N>  (deferred to Phase 5 with documentation)

Recommended next: review docs/refactoring/roadmap.md and
_meta/challenger-report.md before proceeding to Phase 5 (TO-BE testing).
```
