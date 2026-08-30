<!--
audience: end-user
diataxis: reference
last-verified: 2026-08-30
verified-against: c6c780a
-->

# Capability catalog

Every agent and skill that ships today, generated from the plugin tree at the commit in
the front matter above. The authoritative source is the tree itself, under
[`plugins/`](https://github.com/luketherose/claude-registry/tree/main/plugins).

## Counts

| Plugin | Version | Agents | Skills |
|---|---|---:|---:|
| [`replatforming`](#replatforming) | 1.0.0 | 58 | 4 |
| [`dev-standards`](#dev-standards) | 1.0.0 | 12 | 29 |
| [`deliberation`](#deliberation) | 1.0.0 | 7 | 0 |
| [`docs-branding`](#docs-branding) | 1.0.0 | 4 | 7 |
| [`analysis-architecture`](#analysis-architecture) | 1.0.0 | 5 | 3 |
| [`caveman`](#caveman) | 1.0.0 | 0 | 3 |
| **Total** | | **86** | **46** |

## How to read this page

- **Model** is the `model` frontmatter value. `inherit` means the agent runs on whatever
  model the session is running, which is the platform default and the policy for
  user-facing agents. `opus` is reserved for supervisors, challengers, auditors and
  deliberation personas, which also carry `effort: high`. `sonnet` is for pipeline
  workers dispatched in fan-out. See [Reference](Reference#model-policy).
- **What it does** paraphrases the agent's `description`. The authoritative text, the one
  Claude actually routes on, is the `description` field in the file.
- Agents grouped under a pipeline phase are dispatched by that phase's supervisor and are
  not meant for standalone use.
- Skills are not listed in `/agents`. Claude loads them with the `Skill` tool when a task
  touches their domain.

---

## `replatforming`

```
/plugin install replatforming@claude-registry
```

AS-IS to TO-BE application replatforming: codebase indexing, functional and technical
analysis, baseline testing, TO-BE construction and equivalence verification. 58 agents,
4 skills, and the largest body of bundled reference material in the registry
(`plugins/replatforming/references/`, 143 files across seven subdirectories).

### Workflow entrypoint

| Agent | Model | What it does |
|---|---|---|
| `refactoring-supervisor` | opus | Runs the end-to-end replatforming workflow across five phases, with a human gate between every phase and every Phase 4 step |

### Phase 0, codebase indexing

| Agent | Model | What it does |
|---|---|---|
| `indexing-supervisor` | opus | Indexes any legacy codebase into a Markdown knowledge base at `.indexing-kb/`; autodetects the AS-IS stack |
| `codebase-mapper` | sonnet | Structural inventory: directory tree, file counts, language statistics, package map, entrypoints |
| `dependency-analyzer` | sonnet | External dependencies plus the internal module dependency graph, in any language |
| `streamlit-analyzer` | sonnet | Streamlit specifics: pages, `session_state`, widgets, caching, navigation, anti-patterns |
| `module-documenter` | sonnet | Documents one package end to end at API level; dispatched as a fan-out, one call per module |
| `data-flow-analyst` | sonnet | Every data crossing between the application and the outside world: database, APIs, files, environment |
| `business-logic-analyst` | sonnet | Business rules, validation logic and domain concepts, in any language |
| `synthesizer` | sonnet | Final consolidation of all prior indexing output: overview, bounded contexts, hotspots |
| `indexing-auditor` | opus | Audits Phase 0 output quality once the pipeline completes |

### Phase 1, functional analysis

| Agent | Model | What it does |
|---|---|---|
| `functional-analysis-supervisor` | opus | Runs Phase 1 from `.indexing-kb/` into `docs/analysis/01-functional/` |
| `actor-feature-mapper` | sonnet | Actors, roles, personas and the full feature map, plus the actor by feature matrix |
| `ui-surface-analyst` | sonnet | UI surface: screens, navigation map, component tree, with strong Streamlit awareness |
| `io-catalog-analyst` | sonnet | Functional inputs, outputs and the transformation matrix between them |
| `user-flow-analyst` | sonnet | Use cases, user flows and Mermaid sequence diagrams derived from the earlier waves |
| `implicit-logic-analyst` | sonnet | Logic not stated in the explicit rules: widget parameters, callback chains, magic numbers |
| `functional-analysis-challenger` | opus | Adversarial cross-validation for gaps, contradictions, unverified claims, AS-IS violations |
| `functional-traceability-auditor` | opus | Validates evidence traceability, negative space and AS-IS purity in Phase 1 output |

### Phase 2, technical analysis

| Agent | Model | What it does |
|---|---|---|
| `technical-analysis-supervisor` | opus | Runs Phase 2 from `.indexing-kb/` into `docs/analysis/02-technical/` |
| `code-quality-analyst` | sonnet | Structural map, duplication, complexity hotspots, monolith smells |
| `state-runtime-analyst` | sonnet | Session state, module-level globals, side effects, execution order |
| `dependency-security-analyst` | sonnet | Pinned versus unpinned versions, deprecated libraries, known vulnerabilities, licence posture |
| `data-access-analyst` | sonnet | Data sources, transformations, validations and sinks; persistence and serialisation patterns |
| `integration-analyst` | sonnet | Outbound calls, third-party services, queues and webhooks, with auth, timeout and retry posture |
| `performance-analyst` | sonnet | Static analysis for hot loops, N+1 patterns, blocking I/O on critical paths, caching gaps |
| `resilience-analyst` | sonnet | Error handling, logging quality, silent failures, fallback chains |
| `security-analyst` | sonnet | OWASP Top 10 coverage, input validation, secrets in code, threat model |
| `risk-synthesizer` | sonnet | Consolidates every Wave 1 finding into one risk register, severity matrix and remediation order |
| `technical-analysis-challenger` | opus | Adversarial review of the full Phase 2 output set |
| `technical-evidence-auditor` | opus | Verifies Phase 2 findings are evidence-grounded and free of AS-IS purity violations |

### Phase 3, baseline testing

| Agent | Model | What it does |
|---|---|---|
| `baseline-testing-supervisor` | opus | Runs Phase 3, producing the AS-IS regression baseline under `tests/baseline/` |
| `fixture-builder` | sonnet | The test data layer: deterministic seed, time and network setup plus minimal, realistic and edge fixtures |
| `usecase-test-writer` | sonnet | The baseline pytest module for one use case; one invocation per use case |
| `integration-test-writer` | sonnet | Baseline integration tests: database, file system, mocked outbound APIs, cache |
| `benchmark-writer` | sonnet | Baseline performance benchmarks and memory profiling, the AS-IS performance oracle |
| `service-collection-builder` | sonnet | A Postman 2.1 collection for the services the AS-IS app exposes |
| `baseline-runner` | sonnet | Executes the suite and captures the oracle artefacts: snapshots, benchmark JSON, coverage |
| `baseline-challenger` | opus | Adversarial review of coverage, determinism, oracle integrity and AS-IS source modification |

### Phase 4, application replatforming

`refactoring-supervisor` drives Phase 4 itself rather than delegating to a phase
supervisor. The agents below are the TO-BE construction cluster.

| Agent | Model | What it does |
|---|---|---|
| `decomposition-architect` | sonnet | Bounded-context decomposition and the foundational ADRs (architecture style, target stack) |
| `api-contract-designer` | sonnet | The OpenAPI 3.1 contract, the authentication-flow ADR and a TO-BE Postman collection |
| `backend-scaffolder` | sonnet | The Spring Boot 3 Maven scaffold, with controller skeletons generated from the OpenAPI contract |
| `data-mapper` | sonnet | The JPA persistence layer: entities, value objects, enums, Liquibase changelogs, repositories |
| `logic-translator` | sonnet | Translates the AS-IS Python logic for one use case into Java on Spring; one call per use case |
| `frontend-scaffolder` | sonnet | The Angular workspace: core and shared layers, interceptors, guards, typed client from OpenAPI |
| `hardening-architect` | sonnet | Observability and security hardening on the scaffold: structured logging, correlation ids, metrics |
| `test-data-seeder` | sonnet | Seeds the runtime database so a built TO-BE application can actually be exercised through its UI |
| `migration-roadmap-builder` | sonnet | The strangler-fig rollout roadmap with per-context milestones and rollback criteria |
| `phase4-challenger` | opus | The AS-IS to TO-BE traceability matrix plus ten adversarial checks |
| `refactoring-tobe-supervisor` | opus | The earlier big-bang Phase 4 supervisor. Superseded by the incremental loop that `refactoring-supervisor` drives; retained for backward compatibility |

### TO-BE testing and equivalence verification

This cluster was the separate Phase 5 of the earlier workflow. Its work is now absorbed
into Phase 4 Step 6. The agents remain in the plugin for backward compatibility, and
their own descriptions still refer to Phase 5.

| Agent | Model | What it does |
|---|---|---|
| `tobe-testing-supervisor` | opus | Validates the TO-BE codebase against the Phase 3 AS-IS oracle and produces the equivalence report |
| `equivalence-test-writer` | sonnet | The equivalence pytest harness for one use case, comparing TO-BE output against Phase 3 snapshots |
| `backend-test-writer` | sonnet | The TO-BE backend suite: JUnit 5, Mockito, Testcontainers, Spring Cloud Contract |
| `frontend-test-writer` | sonnet | The TO-BE frontend suite: Jest, Angular Testing Library, Playwright end to end |
| `security-test-writer` | sonnet | OWASP Top 10 coverage against the security baseline set by Phase 4 hardening |
| `performance-comparator` | sonnet | Load scenarios comparing TO-BE latency against the Phase 3 benchmark |
| `tobe-test-runner` | sonnet | Executes the TO-BE suites and load scenarios, capturing coverage and contract verifier output |
| `equivalence-synthesizer` | sonnet | Consolidates the phase output into the deliverable equivalence report |
| `tobe-testing-challenger` | opus | Adversarial review of the phase, surfacing gaps the test writers missed |

### Skills

| Skill | Provides |
|---|---|
| `python-to-java-migration-expert` | Translating a Python application to Java on Spring Boot: concept mapping, library equivalents, idiom differences |
| `python-to-angular-migration-expert` | Replacing a Python server-rendered UI (Django templates, Jinja2, Flask, Streamlit) with an Angular single-page application |
| `python-to-react-migration-expert` | The same replacement, targeting React |
| `test-data-seeding-standards` | The design rules and the seeding procedure for demo and seed data. Preloaded by `test-data-seeder` |

---

## `dev-standards`

```
/plugin install dev-standards@claude-registry
```

Production code standards, developer agents and test authoring across nine languages,
plus REST API design and bug diagnosis. This is the day-to-day plugin. It ships
`plugins/dev-standards/.mcp.json`, wiring the Playwright MCP server used by
`browser-automation`.

### Agents

| Agent | Model | What it does |
|---|---|---|
| `developer-java` | inherit | Writes, reviews and refactors Java with clean layering and explicit error handling |
| `developer-python` | inherit | Writes, reviews and refactors Python: PEP 8, type hints, pytest |
| `developer-frontend` | inherit | Frontend across Angular, React (with Next.js and TanStack), Vue, Qwik and vanilla TypeScript |
| `developer-go` | inherit | Go following effective-go conventions and the standard project layout |
| `developer-rust` | inherit | Rust following the API guidelines and idiomatic error handling |
| `developer-kotlin` | inherit | Kotlin for JVM backends and Android |
| `developer-csharp` | inherit | C# and .NET for ASP.NET Core 8+ Web APIs and minimal APIs |
| `developer-php` | inherit | PHP 8.2+ with `strict_types`, typed properties, readonly classes and enums |
| `developer-ruby` | inherit | Ruby for Rails 7+ and Sinatra services |
| `test-writer` | inherit | Unit, integration and end-to-end tests for existing code |
| `debugger` | inherit | Diagnoses a bug from error messages, stack traces, logs and source |
| `api-designer` | inherit | Designs and reviews REST contracts. Preloads `rest-api-standards` on every run |

### Skills

| Skill | Provides |
|---|---|
| `java-spring-standards` | The canonical Java and Spring Boot standards: package structure, layering, error handling, observability |
| `java-expert` | Java 17+ language features outside the Spring layer: records, sealed classes, streams, concurrency |
| `spring-expert` | Spring Boot 3.x configuration and runtime: dependency injection, profiles, security, test slices |
| `spring-architecture` | Layering of a Spring module: controller, service, repository and entity boundaries, DTOs, validation |
| `spring-data-jpa` | JPA and Hibernate inside Spring: entity design, fetch strategies, N+1 resolution, transactions |
| `backend-orchestrator` | Coordination when a backend task spans more than one Java or Spring layer |
| `postgresql-expert` | PostgreSQL: table design, SQL review, index selection, query tuning, Liquibase migrations |
| `python-expert` | Python outside Streamlit: type hints, Pydantic v2, pytest, structured logging, dependency management |
| `streamlit-expert` | Streamlit apps: page structure, `session_state`, caching, reusable components, anti-patterns |
| `angular-expert` | Angular 17+: components, the smart and dumb split, OnPush, reactive forms, lazy routes |
| `ngrx-expert` | NgRx state management: store design, actions, reducers, memoised selectors, effects, facades |
| `rxjs-expert` | RxJS pipelines: flattening strategies, subscription management, stream combination, error handling |
| `react-expert` | React 18+: component architecture, hooks, prop typing, memoisation, Suspense, Testing Library |
| `nextjs` | Next.js 14+ App Router: server components, server actions, metadata, caching layers |
| `tanstack` | Type-safe routing with TanStack Router: file-based routes, loaders, search params |
| `tanstack-query` | TanStack Query v5: queries, mutations, cache invalidation, optimistic updates, prefetching |
| `tanstack-start` | Full-stack React with TanStack Start: SSR, server functions, streaming, end-to-end types |
| `vue-expert` | Vue 3 Composition API: components, composables, Pinia, Vue Router 4 |
| `qwik-expert` | Qwik and Qwik City: resumability, signals, route loaders and actions |
| `vanilla-expert` | Web Components, ES modules and framework-free widgets and libraries |
| `css-expert` | CSS and SCSS: design tokens, BEM, specificity, theming, mobile-first responsive layout |
| `design-expert` | Layouts, mockups and style specifications, produced before implementation starts |
| `unicredit-design-system` | The UniCredit design system, for engagements with that end client |
| `frontend-orchestrator` | Coordination when a frontend task spans routing, state, styling and API access at once |
| `rest-api-standards` | The canonical REST design standards: resources, methods, status codes, versioning, RFC 7807, OpenAPI 3.1 |
| `testing-standards` | The canonical testing standards: taxonomy, naming, Arrange-Act-Assert, framework templates |
| `refactoring-expert` | Structural improvement without behaviour change: SOLID, cohesion and coupling, testability |
| `dependency-resolver` | Dependency conflicts: incompatible peers, transitive clashes, breaking upgrades, deprecated APIs |
| `browser-automation` | Driving a real browser through the Playwright MCP server: navigation, screenshots, forms, end-to-end runs |

---

## `deliberation`

```
/plugin install deliberation@claude-registry
```

A multi-agent debate engine for decisions that are expensive to reverse. Every agent runs
on `opus` with `effort: high`, because a persona that concedes too early makes the whole
exercise pointless. Reference material lives in
`plugins/deliberation/references/deliberation/`.

| Agent | Model | What it does |
|---|---|---|
| `deliberative-decision-engine` | opus | The entrypoint. Frames the decision, dispatches the personas, runs challenge and rebuttal rounds, produces the auditable record |
| `debate-proposer` | opus | The primary architect persona, which puts the proposal on the table |
| `debate-critic` | opus | The sceptical critic persona |
| `debate-risk-reviewer` | opus | The security, compliance and risk persona |
| `debate-operations-reviewer` | opus | The operations and reliability persona |
| `debate-replatforming-specialist` | opus | The migration and replatforming persona |
| `debate-judge` | opus | Summarises without deciding in the middle round, and delivers the final decision in the last one |

The six personas are dispatched by the engine. Invoking one directly gives you an opinion
without the debate, which is rarely what you want.

---

## `docs-branding`

```
/plugin install docs-branding@claude-registry
```

Documentation authoring and Accenture-branded deliverables. Ships
`plugins/docs-branding/.mcp.json`, wiring the UML MCP server used by
`uml-diagram-generator`.

### Agents

| Agent | Model | What it does |
|---|---|---|
| `documentation-writer` | inherit | READMEs, API guides, architecture overviews, runbooks, onboarding guides |
| `wiki-writer` | inherit | Authors and restructures a GitHub wiki around the Diataxis framework. Writes locally, never pushes |
| `document-creator` | inherit | Accenture-branded PDF and DOCX from project material. Preloads `accenture-branding` |
| `presentation-creator` | inherit | Accenture-branded PPTX from project material. Preloads `accenture-branding` |

### Skills

| Skill | Provides |
|---|---|
| `accenture-branding` | The brand reference data: palette, typography, layout specs, HTML and CSS template for PDF |
| `doc-expert` | Documentation conventions for Python and Streamlit, Java and Spring, and Angular projects |
| `documentation-orchestrator` | Coordination of a full-stack documentation deliverable, keeping both sides consistent |
| `backend-documentation` | Enterprise technical documentation for a Java and Spring Boot backend |
| `frontend-documentation` | Enterprise technical documentation for an Angular frontend |
| `functional-document-generator` | Converts existing functional documentation into an enterprise LaTeX deliverable |
| `uml-diagram-generator` | UML diagrams for documentation, architecture design and code-structure explanation |

---

## `analysis-architecture`

```
/plugin install analysis-architecture@claude-registry
```

Architecture design, requirement extraction, technical analysis, orchestration and
registry auditing.

### Agents

| Agent | Model | What it does |
|---|---|---|
| `software-architect` | inherit | Analyses and designs architecture, evaluates technology choices, writes ADRs |
| `functional-analyst` | inherit | Extracts functional requirements and documents use cases, processes and acceptance criteria |
| `technical-analyst` | inherit | Technical analysis of an existing system: stack, technical debt inventory, security posture |
| `orchestrator` | opus | Decomposes a multi-domain or ambiguous task, dispatches specialists in parallel, synthesises |
| `registry-auditor` | opus | Audits a Claude Code agent and skill registry against Anthropic's published quality rubrics. Runs in the background |

### Skills

| Skill | Provides |
|---|---|
| `tech-analyst` | The structural map an analysis or migration pipeline needs first: modules, dependencies, bounded contexts |
| `functional-reconstruction` | Reconstructing the AS-IS functional behaviour of a codebase before a migration |
| `graphify-code-graph` | Navigating a codebase through a persistent code knowledge graph instead of ad-hoc grepping |

---

## `caveman`

```
/plugin install caveman@claude-registry
```

Output-style skills. No agents.

| Skill | Provides |
|---|---|
| `caveman` | Terse, direct prose with no filler |
| `caveman-commit` | The same register applied to commit messages |
| `caveman-review` | The same register applied to code-review comments |

---

## Capabilities that are no longer here

| What was retired | Use instead |
|---|---|
| The in-house code reviewer, removed 2026-08 | The `pr-review-toolkit` plugin from the official Anthropic marketplace. State that dependency as optional |
| The old Java and Spring developer agent name, renamed 2026-08 | `developer-java` |
| Two separate test-data skills, merged 2026-05 | `test-data-seeding-standards` |

The exact retired names are the keys of the `RETIRED` dict in
[`.github/scripts/validate_registry.py`](https://github.com/luketherose/claude-registry/blob/main/.github/scripts/validate_registry.py).
They are described here rather than quoted, because CI fails on a retired name written in
backticks anywhere outside the changelog. See
[Reference](Reference#retired-capability-names).

## Related

- [Architecture](Architecture): how the phases and the CI flow fit together
- [Usage](Usage): how to invoke these capabilities
- [Reference](Reference): frontmatter fields, gates and paths
