# Claude Registry

The team's Claude Code **plugin marketplace**. Agents, skills and supporting material,
published as plugins that install and update themselves.

## Install

Add the marketplace once, then enable the plugins you need:

```bash
/plugin marketplace add luketherose/claude-registry
```

```bash
/plugin install dev-standards@claude-registry
```

Plugins update in the background when the resolved version changes. There is no script to
run and no manual sync step.

### Per-project setup

To make a project pull the marketplace and enable a fixed set of plugins for everyone on
the team, commit this into the project's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "claude-registry": {
      "source": { "source": "github", "repo": "luketherose/claude-registry" }
    }
  },
  "enabledPlugins": {
    "dev-standards@claude-registry": true,
    "analysis-architecture@claude-registry": true
  }
}
```

The marketplace is added automatically when a teammate trusts the project, and the listed
plugins are enabled by default.

### Which plugins to enable

Enable only what the project needs. Every enabled subagent description competes for the
same 15000-token delegation budget, and a smaller enabled set produces sharper routing.

| Situation | Enable |
|---|---|
| Day-to-day development | `dev-standards` |
| Architecture and analysis work | `analysis-architecture` |
| A legacy migration project | `replatforming`, plus `analysis-architecture` |
| Producing client deliverables | `docs-branding` |
| A hard, irreversible decision | `deliberation` |

## Repository structure

```
.claude-plugin/marketplace.json   the marketplace manifest
plugins/<plugin>/                 the distribution unit
  .claude-plugin/plugin.json      manifest: name, description, version, component wiring
  agents/                         subagents
  skills/<name>/SKILL.md          Agent Skills with references/ scripts/ assets/
  references/                     shared reference material for the plugin's agents
  evals/ examples/                evaluations and worked examples
  .mcp.json                       optional MCP servers
docs/registry/                    governance and authoring documentation
templates/ policies/ hooks/       scaffolding and shared configuration
scripts/                          maintenance tooling
archive/                          superseded material kept for provenance
```

## Contributing

Read [docs/registry/how-to-write-a-capability.md](docs/registry/how-to-write-a-capability.md)
first. It is the authoritative guide and it covers the decision that matters most: whether
what you are building is an agent, a skill or a command.

```bash
python3 .github/scripts/validate_registry.py
claude plugin validate .
```

Both run in CI on every pull request. The validator gates the subagent description budget,
`SKILL.md` body length, frontmatter correctness, reference link resolution and
`${CLAUDE_PLUGIN_ROOT}` path resolution.

## Available capabilities

### `replatforming`

AS-IS to TO-BE application replatforming pipeline: codebase indexing, functional and technical analysis, baseline testing, TO-BE scaffolding, and equivalence verification.

```bash
/plugin install replatforming@claude-registry
```

**Agents (58)**

| Agent | Model | Use when |
|---|---|---|
| `baseline-challenger` | opus | Use this agent to perform an adversarial review of Phase 3 Baseline Testing outputs. Reads all worker outputs (fixtures, test files, benchmarks,... |
| `baseline-runner` | sonnet | Use this agent to execute the AS-IS baseline regression suite produced in Wave 1 and capture the oracle artifacts: snapshots, benchmark JSON,... |
| `baseline-testing-supervisor` | opus | Use this agent when running Phase 3 — AS-IS Baseline Testing — of a refactoring or migration workflow. Single entrypoint that reads `.indexing-kb/`,... |
| `benchmark-writer` | sonnet | Use this agent to write the baseline performance benchmarks for the AS-IS codebase: per-UC pytest-benchmark scripts, memory profiling probes, and... |
| `fixture-builder` | sonnet | Use this agent to produce the test data layer of the AS-IS baseline regression suite: minimal, realistic, and edge fixtures for use cases plus a... |
| `integration-test-writer` | sonnet | Use this agent to write the baseline integration tests for the AS-IS codebase: DB access, file system I/O, external API consumption (mocked), cache... |
| `service-collection-builder` | sonnet | Use this agent to produce a Postman 2.1 collection for the services exposed by the AS-IS app, so they can be regression-tested end-to-end against the... |
| `usecase-test-writer` | sonnet | Use this agent to write the baseline pytest module for ONE use case from Phase 1 AS-IS. Each invocation handles one UC: produces... |
| `actor-feature-mapper` | sonnet | Use this agent to extract actors, roles, personas, and the full feature map of an application AS-IS from an existing knowledge base at .indexing-kb/.... |
| `functional-analysis-challenger` | opus | Use this agent to cross-validate the full set of Phase 1 outputs by looking for gaps, contradictions, unverified claims, and AS-IS violations.... |
| `functional-analysis-supervisor` | opus | Use this agent when running Phase 1 — AS-IS Functional Analysis — of a refactoring or migration workflow. Single entrypoint that reads an existing... |
| `functional-traceability-auditor` | opus | Use this agent when validating evidence traceability, negative space, and AS-IS purity in Phase 1 functional analysis outputs. Reads... |
| `implicit-logic-analyst` | sonnet | Use this agent to extract IMPLICIT business and validation logic that is not surfaced in the explicit business rules — embedded in widget parameters,... |
| `io-catalog-analyst` | sonnet | Use this agent to inventory all functional inputs, outputs, and the transformation matrix between them in an application AS-IS. Functional... |
| `ui-surface-analyst` | sonnet | Use this agent to inventory the UI surface of an application AS-IS: screens, navigation map, component tree. Strong Streamlit awareness — treats each... |
| `user-flow-analyst` | sonnet | Use this agent to derive use cases, user flows, and Mermaid sequence diagrams from already-extracted actors, features, UI surface, and I/O catalog.... |
| `business-logic-analyst` | sonnet | Use this agent to extract business rules, validation logic, and domain concepts from a codebase in any language. Produces a domain-level view... |
| `codebase-mapper` | sonnet | Use this agent to produce a structural inventory of any codebase: directory tree, file counts, language statistics, top-level package map,... |
| `data-flow-analyst` | sonnet | Use this agent to identify all data crossings between the application and the outside world: database access, external API calls, file I/O,... |
| `dependency-analyzer` | sonnet | Use this agent to extract external dependencies and build the internal module dependency graph for a codebase in any language. Reads the project's... |
| `indexing-auditor` | opus | Use this agent when auditing Phase 0 indexing output quality after the indexing pipeline completes. Reads bronze/, silver/, gold/, graph/, and... |
| `indexing-supervisor` | opus | Use this agent when indexing any legacy codebase into a markdown knowledge base inside the repository. Language-agnostic — autodetects the AS-IS... |
| `module-documenter` | sonnet | Use this agent to document one package or module of a codebase end-to-end at the API level: purpose, public interface (exported classes/functions),... |
| `streamlit-analyzer` | sonnet | Use this agent to analyze Streamlit-specific concerns: pages, session_state usage, widgets, caching, navigation, custom components, and... |
| `synthesizer` | sonnet | Use this agent to consolidate all prior phase outputs as the final step of the indexing-supervisor pipeline. Reads all prior phase outputs from the... |
| `refactoring-supervisor` | opus | Use this agent when running an end-to-end APPLICATION REPLATFORMING workflow on a codebase. Top-level workflow orchestrator (capability formerly... |
| `api-contract-designer` | sonnet | Use this agent to produce the OpenAPI 3.1 contract for the TO-BE backend, the authentication-flow ADR, and a TO-BE Postman collection (mirroring the... |
| `backend-scaffolder` | sonnet | Use this agent to produce the Spring Boot 3 backend scaffold (Maven project, package structure per bounded context, controller skeletons from the... |
| `data-mapper` | sonnet | Use this agent to produce the JPA persistence layer for the TO-BE backend: entity classes (one aggregate at a time), Liquibase YAML changelogs,... |
| `decomposition-architect` | sonnet | Use this agent to produce the bounded-context decomposition for the TO-BE architecture and the foundational ADRs (architecture style, target stack).... |
| `frontend-scaffolder` | sonnet | Use this agent to produce the Angular workspace for the TO-BE frontend: app scaffold, core/shared layers (interceptors, guards, base API service,... |
| `hardening-architect` | sonnet | Use this agent to apply observability and security hardening to the TO-BE scaffold produced in Wave 3: structured JSON logging with correlation-id,... |
| `logic-translator` | sonnet | Use this agent to translate the AS-IS Python business logic for ONE use case into Java/Spring code in the TO-BE backend. Reads the Phase 1 UC spec,... |
| `migration-roadmap-builder` | sonnet | Use this agent to produce the migration roadmap for the TO-BE rollout: strangler fig plan with milestones (one per bounded context or grouping),... |
| `phase4-challenger` | opus | Use this agent to perform an adversarial review of all Phase 4 outputs. Produces the AS-IS↔TO-BE traceability matrix and ten adversarial checks:... |
| `refactoring-tobe-supervisor` | opus | Use this agent when running Phase 4 — TO-BE Refactoring — of a refactoring or migration workflow. First phase in which target technologies (Spring... |
| `test-data-seeder` | sonnet | Use this agent when a TO-BE application has been built and tests are green, but the runtime database is empty and the UI cannot be meaningfully... |
| `code-quality-analyst` | sonnet | Use this agent to analyze code quality of a codebase AS-IS: structural map of the codebase (entrypoints, packages, modules, naming conventions),... |
| `data-access-analyst` | sonnet | Use this agent to analyze data flow and data access patterns of a codebase AS-IS: origin of data (sources), transformations, validations, sinks; how... |
| `dependency-security-analyst` | sonnet | Use this agent to analyze the external dependency posture of a codebase AS-IS: pinned vs unpinned versions, deprecated libraries, known... |
| `integration-analyst` | sonnet | Use this agent to analyze external integrations of a codebase AS-IS: outbound HTTP/API calls, third-party services, message queues, webhooks, and... |
| `performance-analyst` | sonnet | Use this agent to analyze performance posture of a codebase AS-IS via static analysis: hot loops, N+1 query patterns, blocking I/O on critical paths,... |
| `resilience-analyst` | sonnet | Use this agent to analyze resilience and error-handling posture of a codebase AS-IS: try/except patterns, logging quality, silent failures, fallback... |
| `risk-synthesizer` | sonnet | Use this agent to consolidate the findings of all Wave 1 technical-analysis workers into a unified risk register, severity matrix, and ordered... |
| `security-analyst` | sonnet | Use this agent to analyze code-level security posture of a codebase AS-IS: OWASP Top 10 coverage (injection, broken auth, sensitive data exposure,... |
| `state-runtime-analyst` | sonnet | Use this agent to analyze application state and runtime behavior of a codebase AS-IS: session state, module-level globals, side effects, execution... |
| `technical-analysis-challenger` | opus | Use this agent to perform an adversarial review of Phase 2 Technical Analysis outputs. Reads all Wave 1 artifacts plus the synthesized risk register... |
| `technical-analysis-supervisor` | opus | Use this agent when running Phase 2 — AS-IS Technical Analysis — of a refactoring or migration workflow. Single entrypoint that reads `.indexing-kb/`... |
| `technical-evidence-auditor` | opus | Use this agent when validating that Phase 2 technical findings are evidence-grounded and free of AS-IS purity violations. Reads... |
| `backend-test-writer` | sonnet | Use this agent to write the TO-BE backend test suite for a Spring Boot 3 codebase scaffolded in Phase 4. Sub-agent of tobe-testing-supervisor (Wave... |
| `equivalence-synthesizer` | sonnet | Use this agent to synthesize the deliverable equivalence report (Phase 5). Sub-agent of tobe-testing-supervisor (Wave 4, sequential). Reads all Phase... |
| `equivalence-test-writer` | sonnet | Use this agent to write the TO-BE equivalence pytest harness for ONE use case. Sub-agent of tobe-testing-supervisor (Wave 1, fan-out per UC). One... |
| `frontend-test-writer` | sonnet | Use this agent to write the TO-BE frontend test suite for an Angular 17+ codebase scaffolded in Phase 4. Sub-agent of tobe-testing-supervisor (Wave... |
| `performance-comparator` | sonnet | Use this agent to compare TO-BE performance against the AS-IS benchmark from Phase 3. Sub-agent of tobe-testing-supervisor (Wave 2). Authors... |
| `security-test-writer` | sonnet | Use this agent to write the TO-BE security test suite covering OWASP Top 10 and the security baseline established by Phase 4 hardening. Sub-agent of... |
| `tobe-test-runner` | sonnet | Use this agent to execute the TO-BE test suites authored in Wave 1 and the load scenarios from Wave 2, capture coverage and contract verifier... |
| `tobe-testing-challenger` | opus | Use this agent to perform an adversarial review of Phase 5 outputs and surface gaps the test writers missed. Sub-agent of tobe-testing-supervisor... |
| `tobe-testing-supervisor` | opus | Use this agent when running Phase 5 — TO-BE Testing & Equivalence Verification — of a refactoring or migration workflow. Single entrypoint that reads... |

**Skills (4)**

| Skill | Provides |
|---|---|
| `python-to-angular-migration-expert` | This skill should be used when replacing a Python server-rendered UI (Django templates, Jinja2, Flask, Streamlit) with an Angular single-page... |
| `python-to-java-migration-expert` | This skill should be used when translating a Python application to Java on Spring Boot: mapping Python concepts to Java idioms, finding library... |
| `python-to-react-migration-expert` | This skill should be used when replacing a Python server-rendered UI (Django templates, Jinja2, Flask-Jinja2, Streamlit) with a React single-page... |
| `test-data-seeding-standards` | This skill should be used when an agent (`test-data-seeder`, `fixture-builder`, a developer agent producing demo or seed data) needs both the design... |

### `dev-standards`

Production code standards, developer agents and test authoring for Java/Spring, Python, Go, Rust, Kotlin, C#, PHP, Ruby, Streamlit and frontend frameworks (Angular, React, Vue, Qwik, Vanilla), plus REST API design and bug diagnosis.

```bash
/plugin install dev-standards@claude-registry
```

**Agents (12)**

| Agent | Model | Use when |
|---|---|---|
| `api-designer` | inherit | Use this agent when designing or reviewing REST API contracts: resource modeling, HTTP method and status code selection, URL structure,... |
| `debugger` | inherit | Use this agent when diagnosing a bug, error, or unexpected behavior in code. Reads error messages, stack traces, logs, and relevant source files to... |
| `developer-csharp` | inherit | Use this agent when writing, reviewing, or refactoring C# / .NET code. Produces production-ready C# for ASP.NET Core 8+ Web APIs, minimal APIs, and... |
| `developer-frontend` | inherit | Use this agent when writing, reviewing, or refactoring frontend code. Supports Angular, React (+ Next.js, TanStack Start, TanStack Query, TanStack... |
| `developer-go` | inherit | Use this agent when writing, reviewing, or refactoring Go code. Produces production-ready Go following effective-go conventions, the standard project... |
| `developer-java` | inherit | Use this agent when writing, reviewing, or refactoring Java code. Produces production-ready code with clean architecture, proper layering,... |
| `developer-kotlin` | inherit | Use this agent when writing, reviewing, or refactoring Kotlin code. Produces production-ready Kotlin for JVM backends (Spring Boot 3 with Kotlin... |
| `developer-php` | inherit | Use this agent when writing, reviewing, or refactoring PHP code. Targets PHP 8.2+ with strict_types, typed properties, readonly classes, enums, and... |
| `developer-python` | inherit | Use this agent when writing, reviewing, or refactoring Python code. Produces production-ready Python following PEP 8, type hints, pytest testing,... |
| `developer-ruby` | inherit | Use this agent when writing, reviewing, or refactoring Ruby code. Produces production-ready Ruby for Rails 7+ web applications, Sinatra services,... |
| `developer-rust` | inherit | Use this agent when writing, reviewing, or refactoring Rust code. Produces production-ready Rust following the Rust API guidelines, idiomatic... |
| `test-writer` | inherit | Use this agent when writing tests for existing code: unit tests, integration tests, or end-to-end tests. Reads the production code, identifies test... |

**Skills (29)**

| Skill | Provides |
|---|---|
| `angular-expert` | This skill should be used when the user works on Angular 17+ code — writing or reviewing components, applying the smart/dumb split, configuring... |
| `backend-orchestrator` | ALWAYS use this skill when a backend task spans more than one Java/Spring layer — the user asks to add a new endpoint end-to-end, design a module... |
| `browser-automation` | This skill should be used when controlling a real browser — navigating pages, taking screenshots, clicking elements, filling forms, switching tabs,... |
| `css-expert` | This skill should be used when writing, refactoring, or reviewing CSS/SCSS — design tokens, BEM naming, specificity rules, modularity, mobile-first... |
| `dependency-resolver` | This skill should be used when a dependency conflict blocks progress — the user reports `NoSuchMethodError`, \"works locally fails in CI\",... |
| `design-expert` | This skill should be used when designing layouts, mockups, or style specifications BEFORE implementing a new frontend component. Trigger phrases:... |
| `frontend-orchestrator` | ALWAYS use this skill when a frontend task spans multiple concerns — the user asks to design a feature mixing routing, state management, styling, and... |
| `java-expert` | This skill should be used when working with Java 17+ language features outside the Spring layer — records, sealed classes, Optional, Stream API,... |
| `java-spring-standards` | This skill should be used when an agent (developer-java, code-reviewer, test-writer) needs the canonical Java/Spring Boot standards: package... |
| `nextjs` | This skill should be used when working with Next.js 14+ App Router — React Server Components, Server Actions, file-based routing, metadata API,... |
| `ngrx-expert` | This skill should be used when the user designs, reviews, or refactors NgRx state management — store design, event-driven actions, pure reducers,... |
| `postgresql-expert` | This skill should be used when the user works with PostgreSQL — designing tables, writing or reviewing SQL, picking indices, tuning queries,... |
| `python-expert` | This skill should be used when writing, reviewing, or refactoring Python code outside Streamlit — mandatory type hints, project structure, Pydantic... |
| `qwik-expert` | This skill should be used when working on a Qwik or Qwik City app — resumability, lazy components, signals, server-side loaders/actions, file-based... |
| `react-expert` | This skill should be used when working with React 18+ — component architecture, hooks, TypeScript prop typing, performance optimisation... |
| `refactoring-expert` | This skill should be used when refactoring code in any language to improve internal structure without changing behaviour. Trigger phrases: \"refactor... |
| `rest-api-standards` | This skill should be used when an agent (api-designer, developer, code-reviewer) needs the canonical REST API design standards: resource modeling,... |
| `rxjs-expert` | This skill should be used when working with RxJS in an Angular project — naming conventions, flattening strategies... |
| `spring-architecture` | This skill should be used when designing or reviewing the LAYERING of a Spring Boot module — Controller/Service/Repository/Entity boundaries,... |
| `spring-data-jpa` | This skill should be used when working with JPA/Hibernate inside a Spring project — entity design, relations, fetch strategies, N+1 fixes,... |
| `spring-expert` | This skill should be used when working with Spring Boot 3.x configuration and runtime concerns — IoC/DI, auto-configuration, profiles,... |
| `streamlit-expert` | This skill should be used when developing or maintaining a Streamlit web app — page structure, session_state management, caching (`@st.cache_data`,... |
| `tanstack-query` | This skill should be used when working with TanStack Query v5 in a React app — useQuery, useMutation, useInfiniteQuery, QueryClient configuration,... |
| `tanstack-start` | This skill should be used when building a full-stack React application with TanStack Start — SSR, Server Functions, streaming, file-based routing,... |
| `tanstack` | This skill should be used when adding type-safe routing to a React app with TanStack Router — file-based routes, route definitions, loaders, search... |
| `testing-standards` | This skill should be used when an agent (test-writer, developer, code-reviewer) needs the canonical testing standards: principles, scenario taxonomy,... |
| `unicredit-design-system` | ALWAYS use this skill when the project end client is UniCredit (UC banking group, including UniCredit Bank Italy/Germany/Austria/CEE). Trigger... |
| `vanilla-expert` | This skill should be used when building independent widgets, reusable libraries, or projects where a framework would be overkill — Web Components, ES... |
| `vue-expert` | This skill should be used when working with Vue 3 Composition API — components, composables, Pinia state management, Vue Router 4, TypeScript... |

### `deliberation`

Multi-agent deliberative decision engine: structured debate with independent personas, challenge rounds, rebuttals, and auditable final-decision artefacts for high-stakes or irreversible decisions.

```bash
/plugin install deliberation@claude-registry
```

**Agents (7)**

| Agent | Model | Use when |
|---|---|---|
| `debate-critic` | opus | Use this agent when the `deliberative-decision-engine` dispatches the Skeptical Critic persona in Step 2 of a multi-agent debate. Reads the decision... |
| `debate-judge` | opus | Use this agent when the `deliberative-decision-engine` dispatches the neutral judge persona — in Step 3 (summarisation mode, no decision) or Step 6... |
| `debate-operations-reviewer` | opus | Use this agent when the `deliberative-decision-engine` dispatches the Operations / Reliability Reviewer persona in Step 2 of a multi-agent debate.... |
| `debate-proposer` | opus | Use this agent when the `deliberative-decision-engine` dispatches the Primary Architect / Proposer persona in Step 2 of a multi-agent debate. Reads... |
| `debate-replatforming-specialist` | opus | Use this agent when the `deliberative-decision-engine` dispatches the Migration / Replatforming Specialist persona in Step 2 of a multi-agent debate.... |
| `debate-risk-reviewer` | opus | Use this agent when the `deliberative-decision-engine` dispatches the Security / Compliance / Risk Reviewer persona in Step 2 of a multi-agent... |
| `deliberative-decision-engine` | opus | Use this agent when a complex, high-stakes, irreversible, or replatforming-relevant decision must be made through a structured multi-agent debate... |

### `docs-branding`

Technical documentation authoring and Accenture-branded deliverable generation: READMEs, wikis, runbooks, LaTeX docs, PDF/DOCX documents, and PowerPoint presentations.

```bash
/plugin install docs-branding@claude-registry
```

**Agents (4)**

| Agent | Model | Use when |
|---|---|---|
| `document-creator` | inherit | Use this agent when you need to create an Accenture-branded technical document or PDF from project documents, estimation files, or source materials.... |
| `documentation-writer` | inherit | Use this agent when writing or improving technical documentation: README files, API guides, architecture overviews, runbooks, onboarding guides, or... |
| `presentation-creator` | inherit | Use this agent when you need to create an Accenture-branded PowerPoint presentation (.pptx) from project documents, estimation files, or any set of... |
| `wiki-writer` | inherit | Use this agent when authoring or restructuring a GitHub wiki for a software project. Reads the codebase, README, CHANGELOG, ADRs, and existing docs... |

**Skills (7)**

| Skill | Provides |
|---|---|
| `accenture-branding` | This skill should be used when an agent (presentation-creator, document-creator) generates an Accenture-branded deliverable and needs the brand... |
| `backend-documentation` | This skill should be used when generating enterprise technical documentation for a Java/Spring Boot backend, typically as part of a... |
| `doc-expert` | This skill should be used when producing technical or functional documentation for a Python/Streamlit, Java/Spring Boot, or Angular project. Trigger... |
| `documentation-orchestrator` | ALWAYS use this skill when generating enterprise technical documentation for a full-stack project — it interprets a Word template, coordinates... |
| `frontend-documentation` | This skill should be used when generating enterprise technical documentation for an Angular frontend, typically as part of a... |
| `functional-document-generator` | This skill should be used when converting existing functional documentation into an enterprise LaTeX deliverable for stakeholders. Trigger phrases:... |
| `uml-diagram-generator` | This skill should be used when producing UML diagrams for documentation, architecture design, system modeling, or code-structure explanation. Trigger... |

### `analysis-architecture`

System architecture design, ADR authoring, functional requirement extraction, technical debt assessment, capability-registry auditing, and multi-domain task orchestration.

```bash
/plugin install analysis-architecture@claude-registry
```

**Agents (5)**

| Agent | Model | Use when |
|---|---|---|
| `functional-analyst` | inherit | Use this agent when extracting functional requirements from specifications, user stories, or existing code; documenting use cases and business... |
| `orchestrator` | opus | Use this agent when a task spans multiple domains, requires several specialists, or is ambiguous in scope. Dynamically discovers available agents,... |
| `registry-auditor` | opus | Use this agent when the user asks to audit, evaluate, score, or check a Claude Code agent/skill registry against Anthropic's official quality... |
| `software-architect` | inherit | Use this agent when analyzing or designing system architecture, evaluating technology choices, reviewing integration patterns, writing Architecture... |
| `technical-analyst` | inherit | Use this agent when producing a technical analysis of an existing system: technology stack assessment, technical debt inventory, security posture... |

**Skills (2)**

| Skill | Provides |
|---|---|
| `functional-reconstruction` | This skill should be used when the user asks to reconstruct, document, or describe the existing functional behaviour of a codebase before a... |
| `tech-analyst` | This skill should be used when an analysis, migration, or architecture-understanding pipeline starts and the codebase needs a structural map first.... |

### `caveman`

Token-efficient communication mode: terse, direct output with no filler, applied to prose, commit messages, and code-review comments.

```bash
/plugin install caveman@claude-registry
```

**Skills (3)**

| Skill | Provides |
|---|---|
| `caveman-commit` | This skill should be used when the user asks for a commit message — triggers include \"write a commit\", \"commit message for this\", \"conventional... |
| `caveman-review` | This skill should be used when the user asks for code-review comments or PR review — triggers include \"review this PR\", \"review the diff\",... |
| `caveman` | This skill should be used when the user asks for terser, more direct output — explicit triggers include \"caveman mode\", \"caveman... |

## Governance

| Document | Covers |
|---|---|
| [how-to-write-a-capability.md](docs/registry/how-to-write-a-capability.md) | Authoring agents, skills, commands and plugins |
| [CONTRIBUTING.md](docs/registry/CONTRIBUTING.md) | Branching, review and merge process |
| [GOVERNANCE.md](docs/registry/GOVERNANCE.md) | Ownership and decision rights |
| [NAMING-CONVENTIONS.md](docs/registry/NAMING-CONVENTIONS.md) | Naming rules |
| [ANTI-PATTERNS.md](docs/registry/ANTI-PATTERNS.md) | Things that were tried and did not work |
| [release-process.md](docs/registry/release-process.md) | Versioning and publishing |
| [review-checklist.md](docs/registry/review-checklist.md) | What a reviewer checks |
| [evals-guide.md](docs/registry/evals-guide.md) | Writing evaluations |
| [CHANGELOG.md](docs/registry/CHANGELOG.md) | History |

## Useful links

- [Agent Skills best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
