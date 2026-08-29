# Decomposition-architect — ADR templates

> Reference doc for `decomposition-architect`. Nygard-format ADR skeletons for
> ADR-001 (architecture style) and ADR-002 (target stack). Decision logic and
> evaluation criteria stay in `## Method` §4 / §5 in the agent body.

---

## File 4: `docs/adr/ADR-001-architecture-style.md`

```markdown
---
agent: decomposition-architect
generated: <ISO-8601>
sources: [...]
related_ucs: [...]
related_bcs: [...]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# ADR-001 — Architecture Style

## Status
proposed | accepted | superseded

## Context

The AS-IS application is a Streamlit + Python monolith. We need to
decide whether the TO-BE will be a modular monolith (single deployable
with strong package boundaries) or a microservices architecture.

Evidence (from prior phases):
- Phase 1: <N> use cases across <M> bounded contexts
- Phase 2: <N> outbound integrations, <M> inbound (exposed services)
- Phase 2 risk register: <key risks affecting deployment topology>
- Team size and ops capability: <if known; otherwise placeholder>

## Decision

We adopt a **modular monolith** (or **microservices**), structured as
follows:
- one Maven module per bounded context (or one Spring Boot service)
- shared kernel package for common types
- explicit anti-corruption layers between BCs (no direct domain
  references across BC boundaries)
- internal events via Spring ApplicationEventPublisher (or Kafka,
  depending on style)

## Consequences

- Faster delivery vs microservices (or stronger isolation).
- Operational complexity: <single deployable | per-service deployable>.
- Team boundaries align with packages/services.
- Future-proofing: a BC can be extracted into its own service without
  cross-cutting refactor (because the package boundary is already
  enforced via ArchUnit tests).

## Alternatives considered

- **Microservices** (rejected because <reason>): higher ops cost
  unjustified for current team / domain.
- **Layered monolith** (rejected because <reason>): doesn't enforce BC
  boundaries.

## References
- Phase 1 use case inventory: docs/analysis/01-functional/
- Phase 2 risk register: docs/analysis/02-technical/09-synthesis/
```

---

## File 5: `docs/adr/ADR-002-target-stack.md`

```markdown
---
agent: decomposition-architect
generated: <ISO-8601>
sources: [...]
related_ucs: [...]
related_bcs: [...]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# ADR-002 — Target Stack

## Status
proposed | accepted | superseded

## Context

We must define the target technology stack for the TO-BE migration of
the AS-IS Python/Streamlit application.

## Decision

| Layer | Technology | Version | Rationale |
|---|---|---|---|
| JVM | Java | 21 LTS | latest LTS |
| Backend framework | Spring Boot | 3.4 | mature, ecosystem |
| Build tool | Maven | 3.9+ | standard, IDE support |
| Persistence | Spring Data JPA + Hibernate | 6.x | productivity |
| Database | PostgreSQL | 16 | matches AS-IS (Phase 2 detection) |
| Migrations | Liquibase | 4.x | YAML changelogs, immutable changesets, contexts |
| Frontend framework | Angular | 18 | per workflow target |
| Frontend build | Angular CLI / esbuild | — | standard |
| Frontend tests | Jest + Angular Testing Library + Playwright | — | unit + E2E |
| Backend tests | JUnit 5 + Mockito + Testcontainers | — | standard for Spring |
| Logging | SLF4J + Logback (JSON) | — | observability (ADR-004) |
| Metrics | Micrometer + Prometheus | — | (ADR-004) |
| Tracing | OpenTelemetry | — | (ADR-004) |
| API contract | OpenAPI | 3.1 | (ADR-003 details) |

## Consequences

- All workers downstream MUST honor these versions. Conflicts → revisit
  this ADR.
- Java 21 + Spring Boot 3.x: virtual threads available by default.
- PostgreSQL choice ties Phase 5 testing to Testcontainers + PG image.
- Angular 18: standalone components by default; signals available.

## Alternatives considered

- Java 17 (rejected: 21 is the current LTS at decision time)
- Quarkus / Micronaut (rejected: Spring is the workflow target;
  ecosystem familiarity)
- React (rejected: workflow specifies Angular)
- MyBatis (rejected: JPA standard for the team's skill profile)

## References
- Workflow definition (target stack constraint)
- Phase 2 access-pattern-map.md (DB engine detected)
```
