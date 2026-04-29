<!--
audience: end-user
diataxis: reference
last-verified: 2026-04-28
verified-against: 1e9445a
-->

# Capability catalog

The list of agents and skills currently shipped. The authoritative source
is [`claude-marketplace/catalog.json`](https://github.com/luketherose/claude-registry/blob/main/claude-marketplace/catalog.json);
this page mirrors it with grouping and prose. Counts and versions match
the manifest at the date in the page footer.

## Agents

### Top-level role agents

| Name | Tier | Description |
|---|---|---|
| `software-architect` | stable | Architectural analysis, ADRs, trade-off evaluation across security, performance, scalability, cost, maintainability |
| `functional-analyst` | stable | Requirements, use cases, business processes, acceptance criteria |
| `developer-java-spring` | stable | Java 21 + Spring Boot 3 enterprise development |
| `developer-python` | beta | Python / FastAPI development |
| `developer-frontend` | beta | Multi-framework frontend (Angular, React + Next.js / TanStack, Vue 3, Qwik, Vanilla JS/TS) |
| `code-reviewer` | beta | Structured code review on PRs or changed files |
| `test-writer` | beta | JUnit 5 + Mockito + Testcontainers (Java), pytest (Python), Jest (TS) |
| `debugger` | beta | Bug diagnosis from stack traces, logs, code |
| `api-designer` | beta | REST API design and review, OpenAPI 3.1 |
| `documentation-writer` | beta | READMEs, runbooks, architectural guides, onboarding |
| `wiki-writer` | beta | GitHub wikis organised around the Diataxis framework; never auto-pushes |
| `presentation-creator` | beta | Accenture-branded slides (.pptx) from project documents |
| `document-creator` | beta | Accenture-branded documents (PDF / DOCX) from project documents |
| `technical-analyst` | beta | Technical debt, security posture, dependency vulnerabilities |
| `orchestrator` | beta | Meta-orchestrator (opus): discovers installed agents dynamically, decomposes multi-domain tasks, dispatches in parallel, synthesises |

### Refactoring workflow supervisor

| Name | Tier | Description |
|---|---|---|
| `refactoring-supervisor` | beta | Top-level six-phase workflow (opus). Delegates each phase sequentially with HITL between phases |

### Phase 0 — Indexing pipeline

| Name | Tier | Description |
|---|---|---|
| `indexing-supervisor` | beta | Single entrypoint (opus); dispatches 7 sub-agents in 4 phases |
| `codebase-mapper` | beta | Structural inventory: tree, LOC, packages, entrypoints |
| `dependency-analyzer` | beta | External deps + internal import graph + circular deps |
| `streamlit-analyzer` | beta | Pages, session_state, widgets, caching, anti-patterns |
| `module-documenter` | beta | Per-package API docs (parallel fan-out) |
| `data-flow-analyst` | beta | DB, external APIs, file I/O, env vars, configuration |
| `business-logic-analyst` | beta | Domain concepts, validation rules, business rules, state machines |
| `synthesizer` | beta | Final consolidation: overview, bounded contexts, hotspots |

### Phase 1 — Functional analysis pipeline

| Name | Tier | Description |
|---|---|---|
| `functional-analysis-supervisor` | beta | Single entrypoint (opus); 5 sub-agents in 3 waves + export wave |
| `actor-feature-mapper` | beta | Actors, roles, personas, feature map, Actor×Feature matrix |
| `ui-surface-analyst` | beta | Screens, navigation graph, component tree (Streamlit-aware) |
| `io-catalog-analyst` | beta | Inputs, outputs, transformation matrix (functional perspective) |
| `user-flow-analyst` | beta | Use cases, user flows, Mermaid sequence diagrams with reruns |
| `implicit-logic-analyst` | beta | Hidden validation, state machines, callback chains, magic numbers |
| `functional-analysis-challenger` | beta | Adversarial review for gaps, contradictions, AS-IS violations |

### Phase 2 — Technical analysis pipeline

| Name | Tier | Description |
|---|---|---|
| `technical-analysis-supervisor` | beta | Single entrypoint (opus); 8 W1 workers + W2 synthesizer + W3 challenger + export wave |
| `code-quality-analyst` | beta | Codebase map, duplication, complexity hotspots, monolith smells |
| `state-runtime-analyst` | beta | Session state, globals, side effects, state-flow diagram |
| `dependency-security-analyst` | beta | Dependency inventory, CVEs, deprecation watch, license posture, SBOM-lite JSON |
| `data-access-analyst` | beta | Data flow, DB / file / cache / serialization patterns |
| `integration-analyst` | beta | External integrations, auth/timeout/retry, integration map |
| `performance-analyst` | beta | N+1, hot loops, blocking I/O, caching gaps (static analysis) |
| `resilience-analyst` | beta | Error handling, logging, silent failures, fallback chains |
| `security-analyst` | beta | OWASP Top 10, input validation, secrets in code, STRIDE threat model |
| `risk-synthesizer` | beta | Unified risk register MD/JSON/CSV, severity matrix, remediation priority |
| `technical-analysis-challenger` | beta | Adversarial review for gaps, contradictions, AS-IS violations |

### Phase 3 — Baseline testing pipeline

| Name | Tier | Description |
|---|---|---|
| `baseline-testing-supervisor` | beta | Single entrypoint (opus); 7 sub-agents in 4 waves |
| `fixture-builder` | beta | conftest.py with seed/time/network determinism + minimal/realistic/edge fixtures |
| `usecase-test-writer` | beta | pytest module per use case (happy + alternative + edge), Streamlit AppTest where applicable |
| `integration-test-writer` | beta | DB / file system / outbound API tests (mocked) |
| `benchmark-writer` | beta | pytest-benchmark + memory profiling — AS-IS performance oracle |
| `service-collection-builder` | beta | Postman 2.1 collection for services exposed by the AS-IS app |
| `baseline-runner` | beta | Executes the suite, captures snapshots / benchmark JSON / coverage; applies failure policy |
| `baseline-challenger` | beta | Adversarial review (coverage, AS-IS source modifications, determinism, oracle integrity) |

### Phase 4 — TO-BE refactoring pipeline

| Name | Tier | Description |
|---|---|---|
| `refactoring-tobe-supervisor` | beta | Single entrypoint (opus); 9 sub-agents in 6 waves with 3 HITL checkpoints |
| `decomposition-architect` | beta | Bounded-context decomposition (DDD), AS-IS↔TO-BE module map, ADR-001 + ADR-002 |
| `api-contract-designer` | beta | OpenAPI 3.1 contract (single source of truth), Postman TO-BE collection, ADR-003 |
| `backend-scaffolder` | beta | Spring Boot 3 Maven scaffold (controllers from OpenAPI, DTOs, services with TODOs) |
| `data-mapper` | beta | JPA entities, value objects, enums, Flyway migrations, Spring Data JPA repositories |
| `logic-translator` | beta | Translates one UC from AS-IS Python to Java/Spring (fan-out per UC); AS-IS read-only |
| `frontend-scaffolder` | beta | Angular 17+ workspace (standalone components, lazy modules per BC, OpenAPI typed client) |
| `hardening-architect` | beta | Observability (JSON logging + correlation-id, Micrometer + Prometheus, OpenTelemetry) and security baseline |
| `migration-roadmap-builder` | beta | Strangler-fig roadmap with per-BC milestones, rollback, go-live criteria |
| `phase4-challenger` | beta | AS-IS↔TO-BE traceability matrix + 8 adversarial checks |

### Phase 5 — TO-BE testing & equivalence verification pipeline

| Name | Tier | Description |
|---|---|---|
| `tobe-testing-supervisor` | beta | Final go-live gate (opus); 8 workers in 5 waves; produces `01-equivalence-report.md` (PO sign-off) |
| `equivalence-test-writer` | beta | pytest harness driving TO-BE (HTTP or Playwright) and comparing against Phase 3 snapshots |
| `backend-test-writer` | beta | JUnit 5 + Mockito + Testcontainers + Spring Cloud Contract per OpenAPI operationId |
| `frontend-test-writer` | beta | Jest + Angular Testing Library component tests + Playwright E2E from Phase 1 user-flows |
| `security-test-writer` | beta | OWASP Top 10 coverage, auth tests, headers/CORS, optional ZAP baseline scan |
| `performance-comparator` | beta | Gatling or k6 load scenarios; p95/p99 deltas vs Phase 3 baseline |
| `tobe-test-runner` | beta | Executes mvn verify + ng test + playwright + pytest equivalence; captures all oracles |
| `equivalence-synthesizer` | beta | Consolidates Phase 5 outputs into `01-equivalence-report.md` (DELIVERABLE) |
| `tobe-testing-challenger` | beta | 8 adversarial checks (UC coverage, OpenAPI↔TO-BE drift, equivalence integrity) |

## Skills

Skills are atomic knowledge providers. They are not autonomous: they are
invoked by agents to retrieve standards and conventions. The setup
script installs them automatically as dependencies of the agents that
use them.

| Domain | Skills | Used by |
|---|---|---|
| **Backend Java/Spring** | `java-spring-standards`, `spring-expert`, `spring-architecture`, `spring-data-jpa`, `java-expert` | `developer-java-spring`, `code-reviewer`, `test-writer`, `backend-orchestrator` |
| **Backend Python** | `python-expert`, `streamlit-expert` | `developer-python`, `business-logic-analyst` |
| **Database** | `postgresql-expert` | `developer-java-spring`, `data-mapper` |
| **Frontend Angular** | `angular-expert`, `ngrx-expert`, `rxjs-expert` | `developer-frontend`, `frontend-scaffolder` |
| **Frontend React** | `react-expert`, `tanstack`, `tanstack-query`, `tanstack-start`, `nextjs` | `developer-frontend` |
| **Frontend other** | `vue-expert`, `qwik-expert`, `vanilla-expert` | `developer-frontend` |
| **Frontend cross-cutting** | `css-expert`, `design-expert` | `developer-frontend`, `frontend-scaffolder` |
| **Cross-cutting** | `testing-standards`, `rest-api-standards`, `refactoring-expert`, `tech-analyst`, `functional-reconstruction` | many |
| **Documentation** | `doc-expert`, `backend-documentation`, `frontend-documentation`, `documentation-orchestrator` | `documentation-writer`, `wiki-writer` |
| **Branding** | `accenture-branding` | `presentation-creator`, `document-creator` |

## Counts

| Type | Count |
|---|---|
| Agents | 59 |
| Skills | ~40 (see `claude-marketplace/skills/` for the live list) |
| Total capabilities | ~99 |

## How to read this catalog

- **Tier** — `stable` (used in ≥ 2 projects, 30 days no critical issues)
  or `beta` (newer, may evolve).
- **Description** — paraphrased from the agent's `description` field.
  The authoritative description (used by Claude for delegation) is in
  the `.md` file's YAML frontmatter.
- **Pipeline grouping** — agents grouped under a phase (0–5) are
  sub-agents of that phase's supervisor and are not designed for
  standalone use.

## Related

- [Architecture](Architecture) — how the phases fit together
- [Reference](Reference) — manifest fields and frontmatter contract
- [Usage](Usage) — how to invoke these capabilities
