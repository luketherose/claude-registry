# Claude Registry

Governance infrastructure for shared Claude Code capabilities across the team.

The registry lets you define, review, version, and distribute specialised subagents —
exactly like a shared code library, but for Claude's behaviour.

---

## Read the operational guide first

Everything you need to use or contribute to the registry is in the guide:

```
guida-operativa.pdf   (in the root of this repository)
```

The guide covers:
- **Part 1 — Using capabilities**: prerequisites, installation via script, verification, updates
- **Part 2 — Contributing**: creating a new capability, writing the system prompt, testing, opening a PR, handling review, publishing

If you just want to install capabilities in your project without reading everything:

```bash
./claude-catalog/scripts/setup-capabilities.sh /path/to/your-project
```

---

## Repository structure

```
claude-registry/
  claude-catalog/          ← source (development and review)
    agents/                  subagent .md files with YAML frontmatter
      indexing/                pipeline for indexing a legacy codebase (8 agents)
      functional-analysis/     pipeline for AS-IS functional analysis Phase 1 (6 agents)
      technical-analysis/      pipeline for AS-IS technical analysis Phase 2 (11 agents)
      baseline-testing/        pipeline for AS-IS baseline testing Phase 3 (8 agents)
      refactoring-tobe/        pipeline for TO-BE refactoring Phase 4 (10 agents)
      tobe-testing/            pipeline for TO-BE testing & equivalence verification Phase 5 (9 agents)
      developers/              language-specific developer agents (9: Java/Spring, Python, Frontend, Go, Rust, Kotlin, C#, Ruby, PHP)
      (other agents at root level — orchestrator, role-based agents, etc.)
    skills/                  reusable knowledge providers (shared across agents)
      orchestrators/           backend, frontend, documentation orchestrator skills
      (other skills grouped by topic)
    examples/                example invocations for capabilities
    evals/                   validation scenarios
    hooks/                   scripts and configurations for Claude Code hooks
    settings/                reference settings.json for projects
    mcp/                     MCP server configuration examples
    policies/                remaining conventions (not yet migrated to skills)
    templates/               output templates (ADR, report, API contract)
    docs/                    internal documentation for contributors
    scripts/
      setup-capabilities.sh  installs capabilities into a project (resolves dependencies)
      new-capability.sh      scaffolds a new capability or skill
    how-to-write-a-capability.md
    CONTRIBUTING.md
    GOVERNANCE.md
    CHANGELOG.md

  claude-marketplace/      ← distribution (approved capabilities only)
    stable/                  production-ready capabilities
    beta/                    new or experimental capabilities
    skills/                  shared skills (installed automatically as dependencies)
    catalog.json             manifest with versions, metadata, and dependencies

  guida-operativa.pdf      ← read this first
  pitch-claude-registry.pptx
```

---

## Available capabilities

### Agents (65)

| Name | Tier | Description |
|------|------|-------------|
| `software-architect` | stable | Architectural analysis, ADRs, trade-off evaluation |
| `functional-analyst` | stable | Requirements, use cases, business processes |
| `developer-java` | stable | Java/Spring Boot enterprise development |
| `orchestrator` | beta | Meta-orchestrator (opus): discovers installed agents dynamically, decomposes multi-domain tasks, dispatches specialists in parallel, synthesises results |
| `refactoring-supervisor` | beta | **Refactoring workflow supervisor (opus, v2.0.0)**: top-level workflow for end-to-end refactoring/migration. Delegates phases sequentially to dedicated supervisors (Phase 0 indexing, Phase 1 functional analysis, Phase 2 technical analysis, Phase 3 baseline testing, Phase 4 TO-BE refactoring, Phase 5 TO-BE testing & equivalence verification). Strict human-in-the-loop with schematic preview before each phase and execution-timing recap after. **v2.0.0**: MAJOR milestone — workflow now covers the full AS-IS→TO-BE→validation journey (Phases 0–5); Phase 5 is the final go-live gate with PO sign-off on the equivalence report. v1.2.0: when Phase 1 or 2 analysis is complete but the PDF/PPTX export is missing, offers a `regenerate-exports` choice that runs only the export wave. v1.1.0: bootstrap asks the user explicitly per phase to skip / re-run / revise (no more silent auto-skip). |
| `indexing-supervisor` | beta | **Indexing pipeline supervisor (opus, v0.2.0)**: indexes legacy Python codebases (with optional Streamlit) into a markdown KB at `.indexing-kb/`. Dispatches 7 sub-agents in 4 phases. v0.2.0: bootstrap detects existing `.indexing-kb/` and asks the user explicitly skip / re-run / revise before proceeding. |
| `codebase-mapper` | beta | Indexing sub-agent: structural inventory (tree, LOC, packages, entrypoints) |
| `dependency-analyzer` | beta | Indexing sub-agent: external deps + internal import graph + circular deps |
| `streamlit-analyzer` | beta | Indexing sub-agent: pages, session_state, widgets, caching, anti-patterns |
| `module-documenter` | beta | Indexing sub-agent: per-package API documentation (parallel fan-out) |
| `data-flow-analyst` | beta | Indexing sub-agent: DB, external APIs, file I/O, env vars, configuration |
| `business-logic-analyst` | beta | Indexing sub-agent: domain concepts, validation rules, business rules, state machines |
| `synthesizer` | beta | Indexing sub-agent: final consolidation (overview, bounded contexts, hotspots) |
| `functional-analysis-supervisor` | beta | **Functional Analysis supervisor (opus, v0.3.0)**: Phase 1 AS-IS functional analysis. Reads `.indexing-kb/`, dispatches 5 sub-agents in 3 waves (+ optional challenger) followed by a parallel export wave (`document-creator` + `presentation-creator`, always ON) producing Accenture-branded PDF + PPTX in `_exports/`. Output at `docs/analysis/01-functional/`. v0.3.0 adds `exports-only` resume mode: regenerate just the missing PDF/PPTX without re-running the analysis. Streamlit-aware, strictly AS-IS. |
| `actor-feature-mapper` | beta | Functional-analysis sub-agent (W1): actors, roles, personas, feature map, Actor×Feature matrix |
| `ui-surface-analyst` | beta | Functional-analysis sub-agent (W1): screens, navigation graph, component tree (Streamlit-aware) |
| `io-catalog-analyst` | beta | Functional-analysis sub-agent (W1): inputs, outputs, transformation matrix (functional perspective) |
| `user-flow-analyst` | beta | Functional-analysis sub-agent (W2): use cases, user flows, Mermaid sequence diagrams with reruns |
| `implicit-logic-analyst` | beta | Functional-analysis sub-agent (W2): hidden validation, state machines, callback chains, magic numbers |
| `functional-analysis-challenger` | beta | Functional-analysis sub-agent (W3, opt-in): adversarial review for gaps, contradictions, AS-IS violations |
| `technical-analysis-supervisor` | beta | **Technical Analysis supervisor (opus, v0.2.0)**: Phase 2 AS-IS technical analysis. Reads `.indexing-kb/` + Phase 1, dispatches 8 W1 sub-agents (parallel/batched/sequential — adaptive) + W2 synthesizer + W3 challenger, then exports PDF + PPTX. v0.2.0 adds `exports-only` resume mode: regenerate just the missing PDF/PPTX without re-running the analysis. Streamlit-aware. Strictly AS-IS. |
| `code-quality-analyst` | beta | Technical-analysis sub-agent (W1): codebase map, duplication, complexity hotspots, monolith smells |
| `state-runtime-analyst` | beta | Technical-analysis sub-agent (W1): session state, globals, side effects, state-flow diagram (Streamlit-aware) |
| `dependency-security-analyst` | beta | Technical-analysis sub-agent (W1): dependency inventory, CVEs, deprecation watch, license posture, SBOM-lite JSON |
| `data-access-analyst` | beta | Technical-analysis sub-agent (W1): data flow, DB/file/cache/serialization patterns |
| `integration-analyst` | beta | Technical-analysis sub-agent (W1): external integrations, auth/timeout/retry, integration map |
| `performance-analyst` | beta | Technical-analysis sub-agent (W1): N+1, hot loops, blocking I/O, caching gaps (static analysis) |
| `resilience-analyst` | beta | Technical-analysis sub-agent (W1): error handling, logging, silent failures, fallback chains |
| `security-analyst` | beta | Technical-analysis sub-agent (W1): OWASP Top 10, input validation, secrets in code, STRIDE threat model |
| `risk-synthesizer` | beta | Technical-analysis sub-agent (W2): unified risk register MD/JSON/CSV, severity matrix, remediation priority |
| `technical-analysis-challenger` | beta | Technical-analysis sub-agent (W3, always ON): adversarial review for gaps, contradictions, AS-IS violations |
| `baseline-testing-supervisor` | beta | **Baseline Testing supervisor (opus, v0.2.0)**: Phase 3 AS-IS baseline regression suite. Reads `.indexing-kb/` + Phase 1 + Phase 2, dispatches 7 sub-agents in 4 waves (W0 fixtures + W1 fan-out per UC + W2 execution and oracle capture + W3 challenger). Adaptive execution policy (write+execute or write-only). Per-step timing recap. v0.2.0: bootstrap detects existing baseline outputs and asks the user explicitly skip / re-run / revise (default `skip` because the oracle drives Phase 5 equivalence). Streamlit-aware. Strictly AS-IS. |
| `fixture-builder` | beta | Baseline-testing sub-agent (W0): conftest.py with seed/time/network determinism + minimal/realistic/edge fixtures |
| `usecase-test-writer` | beta | Baseline-testing sub-agent (W1, fan-out per UC): pytest module per use case (happy + alternative + edge), Streamlit AppTest where applicable |
| `integration-test-writer` | beta | Baseline-testing sub-agent (W1): DB / file system / outbound API tests (mocked) |
| `benchmark-writer` | beta | Baseline-testing sub-agent (W1): pytest-benchmark + memory profiling — AS-IS performance oracle |
| `service-collection-builder` | beta | Baseline-testing sub-agent (W1, conditional): Postman 2.1 collection for services exposed by the AS-IS app |
| `baseline-runner` | beta | Baseline-testing sub-agent (W2): executes the suite, captures snapshots/benchmark JSON/coverage; applies failure policy (xfail/skip/escalate) |
| `baseline-challenger` | beta | Baseline-testing sub-agent (W3, always ON): adversarial review (coverage, AS-IS source modifications, determinism, oracle integrity, severity-mismatch, Streamlit/Postman) |
| `refactoring-tobe-supervisor` | beta | **Refactoring TO-BE supervisor (opus, v0.2.0)**: Phase 4 — first phase with target tech (Spring Boot 3 + Angular). Reads Phases 0–3, dispatches 9 sub-agents in 6 waves (decomposition + ADRs → OpenAPI → BE+FE parallel scaffolds + per-UC translation → hardening → roadmap → challenger). Strict dependency chain with 3 HITL checkpoints. Adaptive verification (mvn compile + ng build). v0.2.0: bootstrap detects existing TO-BE outputs and asks the user explicitly skip / re-run / revise (default `skip` to protect hand-edited generated code). |
| `decomposition-architect` | beta | Refactoring-tobe sub-agent (W1): bounded-context decomposition (DDD), aggregates, AS-IS↔TO-BE module map, ADR-001 (architecture style) + ADR-002 (target stack) |
| `api-contract-designer` | beta | Refactoring-tobe sub-agent (W2): OpenAPI 3.1 contract (single source of truth), Postman TO-BE collection, ADR-003 (auth flow) |
| `backend-scaffolder` | beta | Refactoring-tobe sub-agent (W3 BE step 1): Spring Boot 3 Maven scaffold (controllers from OpenAPI, DTOs, services with TODOs, error handler RFC 7807, security baseline) |
| `data-mapper` | beta | Refactoring-tobe sub-agent (W3 BE step 2): JPA entities, value objects, enums, Flyway migrations, Spring Data JPA repositories (DDD-honoring) |
| `logic-translator` | beta | Refactoring-tobe sub-agent (W3 BE step 3, fan-out per UC): translates one UC from AS-IS Python to Java/Spring; never touches AS-IS source |
| `frontend-scaffolder` | beta | Refactoring-tobe sub-agent (W3 FE): Angular 17+ workspace (standalone components, lazy modules per BC, OpenAPI typed client, Streamlit translations) |
| `hardening-architect` | beta | Refactoring-tobe sub-agent (W4): observability (JSON logging + correlation-id, Micrometer + Prometheus, OpenTelemetry) and security (Spring Security 6 baseline, OWASP headers, CSP), ADR-004 + ADR-005 |
| `migration-roadmap-builder` | beta | Refactoring-tobe sub-agent (W5): strangler-fig roadmap with per-BC milestones, rollback plans, go-live criteria, AS-IS bug carry-over |
| `phase4-challenger` | beta | Refactoring-tobe sub-agent (W6, always ON): AS-IS↔TO-BE traceability matrix + 8 adversarial checks (coverage, OpenAPI↔code drift, ADR completeness, perf hypothesis, security regression, equivalence, AS-IS-only leak) |
| `tobe-testing-supervisor` | beta | **TO-BE Testing supervisor (opus, v0.1.0)**: Phase 5 — final go-live gate. Validates the TO-BE codebase against the AS-IS baseline (Phase 3). Dispatches 8 sonnet workers in 5 waves: equivalence/backend/frontend/security tests authoring (W1) → performance comparison vs Phase 3 baseline (W2) → execution & oracle capture (W3) → equivalence synthesis with PO sign-off (W4) → adversarial challenger (W5). Adaptive execution policy (mvn/ng/playwright). Failure policy: critical/high escalate; medium/low → TBUG registry with xfail. AS-IS and TO-BE source code stay read-only. Produces the deliverable `01-equivalence-report.md`. |
| `equivalence-test-writer` | beta | TO-BE-testing sub-agent (W1, fan-out per UC): pytest harness driving the TO-BE deployment and comparing output against the Phase 3 AS-IS snapshot (HTTP for direct UCs, Playwright for Streamlit-derived UCs) |
| `backend-test-writer` | beta | TO-BE-testing sub-agent (W1): JUnit 5 + Mockito + Testcontainers + Spring Cloud Contract per OpenAPI operationId; > 80% line, > 70% branch coverage targets |
| `frontend-test-writer` | beta | TO-BE-testing sub-agent (W1): Jest + Angular Testing Library component tests + Playwright E2E specs derived from Phase 1 user-flows |
| `security-test-writer` | beta | TO-BE-testing sub-agent (W1): OWASP Top 10 (A01-A10) coverage, auth/authz tests, headers/CORS, optional ZAP baseline scan; cross-references Phase 2 SEC-NN findings |
| `performance-comparator` | beta | TO-BE-testing sub-agent (W2): Gatling/k6 load tests; p95/p99 deltas vs Phase 3 baseline; flags > +10% (PO sign-off) and > +25% (escalate) |
| `tobe-test-runner` | beta | TO-BE-testing sub-agent (W3): executes the suites; captures coverage, contract verifier results, perf JSON; classifies failures and adds xfail markers (the only worker permitted to do so); never modifies production code |
| `equivalence-synthesizer` | beta | TO-BE-testing sub-agent (W4): consolidates all Phase 5 outputs into `01-equivalence-report.md` (DELIVERABLE — PO sign-off) with per-UC verdict table, accepted-differences register, quality gate, sign-off slots |
| `tobe-testing-challenger` | beta | TO-BE-testing sub-agent (W5, always ON): 8 adversarial checks (UC coverage gaps, OpenAPI↔TO-BE drift, AS-IS/TO-BE source modifications forbidden, mocks-when-shouldn't, equivalence claim integrity, PO sign-off completeness, perf gate compliance) |
| `technical-analyst` | beta | Technical debt, security, vulnerable dependencies |
| `developer-python` | beta | Python/FastAPI development |
| `developer-frontend` | beta | Multi-framework frontend development (Angular, React, Vue, Qwik, Vanilla) |
| `developer-go` | beta | Production-ready Go (net/http, chi, gin, cobra); standard library first, table-driven tests, log/slog, context propagation, errors-as-values |
| `developer-rust` | beta | Production-ready Rust on stable (axum, actix-web, clap, tokio); thiserror/anyhow boundaries, structured concurrency, tracing |
| `developer-kotlin` | beta | Production-ready Kotlin for JVM (Spring Boot 3 with Kotlin idioms or Ktor); coroutines, sealed hierarchies, value classes, no `!!` in production |
| `developer-csharp` | beta | Production-ready C#/.NET 8+ (ASP.NET Core controllers + minimal APIs); nullable reference types, records, IOptions<T> with validation, EF Core |
| `developer-ruby` | beta | Production-ready Ruby on Rails 7+ with service/form/query objects; Sidekiq idempotent jobs, RSpec + factory_bot, RuboCop |
| `developer-php` | beta | Production-ready PHP 8.2+ (Laravel 10/11 layered or Symfony 6/7 data-mapper); strict_types, readonly classes, enums, PHPStan level 8 |
| `code-reviewer` | beta | Structured code review on PRs or changed files |
| `test-writer` | beta | JUnit 5, Mockito, Testcontainers, pytest tests |
| `debugger` | beta | Bug diagnosis from stack traces, logs, and code |
| `api-designer` | beta | REST API design and review, OpenAPI specs |
| `documentation-writer` | beta | READMEs, runbooks, architectural guides |
| `wiki-writer` | beta | GitHub wikis organized around the Diataxis framework (Tutorials, How-to, Reference, Explanation); writes wiki/*.md for PR review, never auto-pushes |
| `presentation-creator` | beta | Accenture-branded slides (.pptx) from project documents |
| `document-creator` | beta | Accenture-branded documents (PDF/DOCX) from project documents |

### Skills

Skills are atomic knowledge providers shared across multiple agents. They are not
autonomous agents: they are invoked by agents to retrieve standards and conventions.
The `setup-capabilities.sh` script installs them automatically as dependencies.

| Name | Used by | Contents |
|------|---------|----------|
| `java-spring-standards` | developer-java, code-reviewer, test-writer | Package structure, layering, testing, error handling, logging, security, Micrometer |
| `testing-standards` | developer-java, test-writer, code-reviewer, developer-python | Principles, scenario taxonomy, naming, JUnit 5 / pytest / Jest templates |
| `rest-api-standards` | developer-java, api-designer, code-reviewer | Resource modelling, HTTP methods, status codes, RFC 7807, OpenAPI 3.1 |
| `accenture-branding` | presentation-creator, document-creator | Colour palette, python-pptx constants, CSS PDF template, typography |
| `unicredit-design-system` | developer-frontend (auto-loaded when the client is UniCredit) | UniCredit brand & Bricks DS — logo rules, palette (`#E30613` red + neutrals + states), typography fallback stack, 8 px spacing grid, ready-to-paste `--uc-*` CSS tokens, ~70 Bricks components, EN 301 549 / WCAG 2.1 AA accessibility targets, tone of voice |
| `functional-reconstruction` | developer-frontend, functional-analyst (agent) | Functional behaviour reconstruction, feature lists, user flows, business rules |
| + 36 frontend and backend skills | developer-frontend | Angular, React, Vue, Qwik, Vanilla, Python, Java, database, refactoring, orchestrators |

---

## Governance

- The `main` branch is protected: every change goes through a Pull Request with review
- GitHub Actions validates structure and completeness of every capability (catalog check first, then marketplace)
- SemVer versioning: PATCH = fix, MINOR = new behaviours, MAJOR = breaking change
- Promotion from `beta` to `stable` requires use in at least two projects and 30 days without critical issues

Details in [`claude-catalog/GOVERNANCE.md`](claude-catalog/GOVERNANCE.md).

---

## Useful links

| Resource | Path |
|----------|------|
| Operational guide (PDF) | [`guida-operativa.pdf`](guida-operativa.pdf) |
| How to write a capability | [`claude-catalog/how-to-write-a-capability.md`](claude-catalog/how-to-write-a-capability.md) |
| PR review checklist | [`claude-catalog/review-checklist.md`](claude-catalog/review-checklist.md) |
| Release process | [`claude-catalog/release-process.md`](claude-catalog/release-process.md) |
| Changelog | [`claude-catalog/CHANGELOG.md`](claude-catalog/CHANGELOG.md) |
| Team pitch (PPTX) | [`pitch-claude-registry.pptx`](pitch-claude-registry.pptx) |
