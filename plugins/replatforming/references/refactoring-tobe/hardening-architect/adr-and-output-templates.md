# Hardening ADRs + output templates

> Reference doc for `hardening-architect`. Read at runtime when emitting
> the deliverables (Method steps 8–10) and the final reporting block.

## Goal

Verbatim ADR skeletons (ADR-004 observability, ADR-005 security baseline),
the hardening summary README, and the agent's reporting block.

---

## 8. ADR-004 — Observability

`docs/adr/ADR-004-observability.md`:

```markdown
---
agent: hardening-architect
generated: <ISO-8601>
sources: [...]
related_ucs: []
related_bcs: []  (cross-cutting)
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# ADR-004 — Observability

## Status
proposed | accepted

## Context

Phase 2 resilience-map identified <N> logging inconsistencies in AS-IS
(some modules use print, some logging.getLogger; no correlation-id;
plain text format). The TO-BE introduces structured JSON logging with
correlation-id propagation, Prometheus metrics, and OpenTelemetry
tracing as a baseline.

## Decision

- **Logging**: SLF4J + Logback with logstash-logback-encoder for JSON
  format. MDC carries `correlationId` (set by CorrelationIdFilter from
  X-Request-Id header). Levels: INFO at root, WARN for hibernate.SQL,
  configurable per package via /actuator/loggers.
- **Metrics**: Micrometer + Prometheus registry. Endpoints exposed at
  /actuator/prometheus. Standard HTTP server requests, JVM metrics,
  data source metrics by default. Custom domain metrics via
  DomainMetrics bean.
- **Tracing**: OpenTelemetry Spring Boot starter. Auto-instrumentation
  for spring-webmvc, spring-data, jdbc. Domain spans via @WithSpan on
  service methods.
- **Correlation**: X-Request-Id header propagated end-to-end. FE
  generates UUID per request; BE preserves and propagates to outbound
  calls.

## Consequences

- All logs are machine-parseable from day one (no migration cost
  later).
- Production runtime exposes /actuator/prometheus for scraping (gated
  by ROLE_ADMIN — see ADR-005).
- OTel exporter target configurable via OTEL_EXPORTER_OTLP_ENDPOINT.
- Frontend network tab shows X-Request-Id for debug.

## Alternatives considered

- **ELK without OTel**: rejected; tracing is non-negotiable for
  distributed debugging.
- **Logstash agent vs JSON logback encoder**: chose encoder for
  zero-overhead in-process JSON.

## References
- Phase 2 resilience-map: docs/analysis/02-technical/07-resilience/
- Phase 2 perf hotspots (informs metric tags): docs/analysis/02-technical/06-performance/
```

---

## 9. ADR-005 — Security baseline

`docs/adr/ADR-005-security-baseline.md`:

```markdown
---
agent: hardening-architect
generated: <ISO-8601>
sources:
  - docs/analysis/02-technical/08-security/
  - docs/adr/ADR-003-auth-flow.md
related_ucs: []
related_bcs: []  (cross-cutting)
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# ADR-005 — Security Baseline

## Status
proposed | accepted

## Context

Phase 2 OWASP Top 10 coverage flagged: <key gaps from Phase 2>.
ADR-003 chose the auth scheme. This ADR fixes the production-grade
hardening baseline that complements ADR-003.

## Decision

### Backend
- HTTP security headers per OWASP Secure Headers Project:
  X-Content-Type-Options, X-Frame-Options DENY, HSTS (1 year + subdomains),
  Referrer-Policy, COOP, COEP, CORP.
- CSRF: disabled (stateless JWT in Authorization header per ADR-003).
- /actuator/* gated (only health/info public; metrics/loggers ROLE_ADMIN).
- CORS: allowlist FE origin via FRONTEND_ORIGIN env; no wildcard;
  credentials false.
- Idempotency-Key required on POST endpoints with side effects
  (enforced via aspect; persisted in idempotency_keys table).

### Frontend
- CSP via meta tag (default-src 'self'; connect-src restricted to API
  origin; frame-ancestors none; form-action 'self').
- Token storage: sessionStorage for access token (15 min TTL); refresh
  via dedicated endpoint with httpOnly cookie OR rotated refresh token
  in sessionStorage (decided in ADR-003).

### Secrets
- All secrets via environment variables; .env.example committed,
  .env gitignored.
- Production: secrets manager (Vault / AWS SM / Azure Key Vault) — not
  configured in scaffold; deployment-time concern.
- No secrets in logs (Phase 2 RISK-RES-NN flagged AS-IS leakage; TO-BE
  redacts via Logback layout).

### Rate limiting
- Hook in place at filter chain (Bucket4j or Spring Cloud Gateway in
  front); concrete config out of scaffold scope, documented as
  follow-up.

## Consequences

- Browser security score: A+ (verified manually post-deploy).
- API requires Bearer JWT on all non-public endpoints.
- Frontend connects only to allowlisted API origins.
- Operations team must provision a secrets manager before prod deploy.

## Alternatives considered

- **Cookie-based session** (rejected: ADR-003 chose stateless JWT;
  CSRF complexity on top of CSP not warranted).
- **Wildcard CORS** (rejected: trivial to misuse; explicit allowlist
  always).
- **CSRF tokens for state-changing endpoints** (rejected: stateless
  JWT eliminates the need; CSRF requires session cookies).

## References
- OWASP Secure Headers Project
- Phase 2 security-findings.md
- ADR-003 auth flow
```

---

## 10. Hardening summary

`docs/refactoring/4.7-hardening/README.md`:

```markdown
---
agent: hardening-architect
generated: <ISO-8601>
sources: [...]
related_ucs: []
related_bcs: []
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# Hardening summary

## Backend
- Logging: JSON, MDC correlationId
- Metrics: Micrometer + Prometheus at /actuator/prometheus
- Tracing: OpenTelemetry Spring Boot starter
- Security: ADR-005 headers, CSRF off, /actuator gated
- Secrets: env-driven; .env.example provided

## Frontend
- CSP via meta tag
- Correlation-id interceptor
- Auth interceptor (Bearer JWT)
- Error interceptor (RFC 7807 → app-level event)

## ADRs added
- ADR-004 Observability
- ADR-005 Security Baseline

## Open questions
- Production deploy: secrets manager (Vault / AWS / Azure) — TBD with ops
- Rate-limiting strategy: edge (gateway) vs in-app (Bucket4j) — TBD
```

---

## Outputs catalogue

### Files (edited)
- `<backend-dir>/pom.xml` (added logstash-logback-encoder, OpenTelemetry)
- `<backend-dir>/src/main/resources/application.yml`
- `<backend-dir>/src/main/resources/logback-spring.xml` (new)
- `<backend-dir>/src/main/java/com/<org>/<app>/shared/config/SecurityConfig.java` (refined)
- `<backend-dir>/src/main/java/com/<org>/<app>/shared/metrics/DomainMetrics.java` (new)
- `<backend-dir>/.env.example` (new)
- `<backend-dir>/.gitignore` (new or updated)
- `<frontend-dir>/src/index.html` (CSP)
- `<frontend-dir>/src/app/core/interceptors/correlation-id.interceptor.ts` (verified / refined)
- `<frontend-dir>/src/app/core/interceptors/auth.interceptor.ts` (header comment / TODO refined)

### Files (new)
- `docs/adr/ADR-004-observability.md`
- `docs/adr/ADR-005-security-baseline.md`
- `docs/refactoring/4.7-hardening/README.md`

---

## Reporting (text response)

```markdown
## Files written / edited
<list>

## ADRs added
- ADR-004 Observability
- ADR-005 Security Baseline

## Backend updates
- Logging:        JSON via logstash encoder
- Metrics:        Micrometer + Prometheus
- Tracing:        OTel Spring Boot starter
- Security:       OWASP headers, /actuator gating, CORS allowlist
- Secrets:        env-driven (.env.example)

## Frontend updates
- CSP:            meta tag with API origin allowlist
- Interceptors:   verified (auth, error, correlation-id)

## Compile / build readiness
- mvn compile: expected to pass (verify)
- ng build: expected to pass (verify)

## Confidence
high | medium | low

## Duration (wall-clock)
<seconds>

## Open questions
- ...
```
