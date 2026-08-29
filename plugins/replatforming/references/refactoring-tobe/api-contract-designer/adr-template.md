# API contract designer — ADR-003 (auth flow) template

> Reference doc for `api-contract-designer`. Read at runtime when authoring
> `docs/adr/ADR-003-auth-flow.md`. The agent body keeps the decision logic
> (which scheme to choose based on Phase 2 findings); this doc holds the
> ADR skeleton.

## Skeleton

```markdown
---
agent: api-contract-designer
generated: <ISO-8601>
sources: [...]
related_ucs: [UC-01, UC-04]   (auth-related UCs)
related_bcs: [BC-01]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# ADR-003 — Authentication Flow

## Status
proposed | accepted

## Context

The AS-IS authentication mechanism (per Phase 2 SEC findings):
<summary of AS-IS auth model and its gaps>

The TO-BE must close any AS-IS auth gaps and provide a unified scheme
for both browser-based (Angular FE → BE) and server-to-server
(integrations → BE) calls.

## Decision

<chosen scheme — one of:>
- **OAuth2 Authorization Code with PKCE** for FE
- **Bearer JWT** for service-to-service
- **Spring Security 6** as the implementation framework
- **Stateless JWT** (no Spring Session) — or **Spring Session** if
  AS-IS used cookies and migration cost is high

Token strategy:
- access token TTL: 15 min
- refresh token TTL: 24h (rotated on use)
- claims: sub (userId), tenantId, roles[], scope[]

CSRF posture:
- stateless JWT in Authorization header → no CSRF token needed
- if cookie-based: SameSite=Lax + CSRF token

CORS:
- allowlist FE origins
- credentials: false (token in Authorization header)

## Consequences

- All endpoints (except `/auth/*` and `/health`) require Bearer JWT.
- FE handles login redirect + PKCE; sets token in axios/HttpClient
  interceptor.
- BE has a global `JwtAuthenticationFilter` that validates token
  signature and expiry.
- Service-to-service callers obtain tokens via client credentials grant.

## Alternatives considered

- **Spring Session + cookie** (rejected: CSRF complexity, less mobile-
  friendly; if AS-IS used cookies, document migration path).
- **API Keys** (rejected: insufficient auth granularity for user
  context).
- **mTLS** (rejected for now: ops complexity; could be added for
  high-security service-to-service).

## References
- Phase 2 security findings: docs/analysis/02-technical/08-security/
- Workflow target: Spring Security 6 baseline
```
