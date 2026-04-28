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
      indexing/                pipeline for indexing legacy Python codebases (8 agents)
      functional-analysis/     pipeline for AS-IS functional analysis Phase 1 (6 agents)
      technical-analysis/      pipeline for AS-IS technical analysis Phase 2 (11 agents)
      baseline-testing/        pipeline for AS-IS baseline testing Phase 3 (8 agents)
      (other agents at root level)
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

### Agents (48)

| Name | Tier | Description |
|------|------|-------------|
| `software-architect` | stable | Architectural analysis, ADRs, trade-off evaluation |
| `functional-analyst` | stable | Requirements, use cases, business processes |
| `developer-java-spring` | stable | Java/Spring Boot enterprise development |
| `orchestrator` | beta | Meta-orchestrator (opus): discovers installed agents dynamically, decomposes multi-domain tasks, dispatches specialists in parallel, synthesises results |
| `refactoring-supervisor` | beta | **Refactoring workflow supervisor (opus)**: top-level workflow for end-to-end refactoring/migration. Delegates phases sequentially to dedicated supervisors (Phase 0 indexing, Phase 1 functional analysis, Phase 2 technical analysis, Phase 3 baseline testing). Strict human-in-the-loop with schematic preview before each phase and execution-timing recap after. |
| `indexing-supervisor` | beta | **Indexing pipeline supervisor (opus)**: indexes legacy Python codebases (with optional Streamlit) into a markdown KB at `.indexing-kb/`. Dispatches 7 sub-agents in 4 phases. |
| `codebase-mapper` | beta | Indexing sub-agent: structural inventory (tree, LOC, packages, entrypoints) |
| `dependency-analyzer` | beta | Indexing sub-agent: external deps + internal import graph + circular deps |
| `streamlit-analyzer` | beta | Indexing sub-agent: pages, session_state, widgets, caching, anti-patterns |
| `module-documenter` | beta | Indexing sub-agent: per-package API documentation (parallel fan-out) |
| `data-flow-analyst` | beta | Indexing sub-agent: DB, external APIs, file I/O, env vars, configuration |
| `business-logic-analyst` | beta | Indexing sub-agent: domain concepts, validation rules, business rules, state machines |
| `synthesizer` | beta | Indexing sub-agent: final consolidation (overview, bounded contexts, hotspots) |
| `functional-analysis-supervisor` | beta | **Functional Analysis supervisor (opus)**: Phase 1 AS-IS functional analysis. Reads `.indexing-kb/`, dispatches 5 sub-agents in 3 waves (+ optional challenger), produces `docs/analysis/01-functional/`. Streamlit-aware, strictly AS-IS. |
| `actor-feature-mapper` | beta | Functional-analysis sub-agent (W1): actors, roles, personas, feature map, Actor×Feature matrix |
| `ui-surface-analyst` | beta | Functional-analysis sub-agent (W1): screens, navigation graph, component tree (Streamlit-aware) |
| `io-catalog-analyst` | beta | Functional-analysis sub-agent (W1): inputs, outputs, transformation matrix (functional perspective) |
| `user-flow-analyst` | beta | Functional-analysis sub-agent (W2): use cases, user flows, Mermaid sequence diagrams with reruns |
| `implicit-logic-analyst` | beta | Functional-analysis sub-agent (W2): hidden validation, state machines, callback chains, magic numbers |
| `functional-analysis-challenger` | beta | Functional-analysis sub-agent (W3, opt-in): adversarial review for gaps, contradictions, AS-IS violations |
| `technical-analysis-supervisor` | beta | **Technical Analysis supervisor (opus)**: Phase 2 AS-IS technical analysis. Reads `.indexing-kb/` + Phase 1, dispatches 8 W1 sub-agents (parallel/batched/sequential — adaptive) + W2 synthesizer + W3 challenger, then exports PDF + PPTX. Streamlit-aware. Strictly AS-IS. |
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
| `baseline-testing-supervisor` | beta | **Baseline Testing supervisor (opus)**: Phase 3 AS-IS baseline regression suite. Reads `.indexing-kb/` + Phase 1 + Phase 2, dispatches 7 sub-agents in 4 waves (W0 fixtures + W1 fan-out per UC + W2 execution and oracle capture + W3 challenger). Adaptive execution policy (write+execute or write-only). Per-step timing recap. Streamlit-aware. Strictly AS-IS. |
| `fixture-builder` | beta | Baseline-testing sub-agent (W0): conftest.py with seed/time/network determinism + minimal/realistic/edge fixtures |
| `usecase-test-writer` | beta | Baseline-testing sub-agent (W1, fan-out per UC): pytest module per use case (happy + alternative + edge), Streamlit AppTest where applicable |
| `integration-test-writer` | beta | Baseline-testing sub-agent (W1): DB / file system / outbound API tests (mocked) |
| `benchmark-writer` | beta | Baseline-testing sub-agent (W1): pytest-benchmark + memory profiling — AS-IS performance oracle |
| `service-collection-builder` | beta | Baseline-testing sub-agent (W1, conditional): Postman 2.1 collection for services exposed by the AS-IS app |
| `baseline-runner` | beta | Baseline-testing sub-agent (W2): executes the suite, captures snapshots/benchmark JSON/coverage; applies failure policy (xfail/skip/escalate) |
| `baseline-challenger` | beta | Baseline-testing sub-agent (W3, always ON): adversarial review (coverage, AS-IS source modifications, determinism, oracle integrity, severity-mismatch, Streamlit/Postman) |
| `technical-analyst` | beta | Technical debt, security, vulnerable dependencies |
| `developer-python` | beta | Python/FastAPI development |
| `developer-frontend` | beta | Multi-framework frontend development (Angular, React, Vue, Qwik, Vanilla) |
| `code-reviewer` | beta | Structured code review on PRs or changed files |
| `test-writer` | beta | JUnit 5, Mockito, Testcontainers, pytest tests |
| `debugger` | beta | Bug diagnosis from stack traces, logs, and code |
| `api-designer` | beta | REST API design and review, OpenAPI specs |
| `documentation-writer` | beta | READMEs, runbooks, architectural guides |
| `presentation-creator` | beta | Accenture-branded slides (.pptx) from project documents |
| `document-creator` | beta | Accenture-branded documents (PDF/DOCX) from project documents |

### Skills

Skills are atomic knowledge providers shared across multiple agents. They are not
autonomous agents: they are invoked by agents to retrieve standards and conventions.
The `setup-capabilities.sh` script installs them automatically as dependencies.

| Name | Used by | Contents |
|------|---------|----------|
| `java-spring-standards` | developer-java-spring, code-reviewer, test-writer | Package structure, layering, testing, error handling, logging, security, Micrometer |
| `testing-standards` | developer-java-spring, test-writer, code-reviewer, developer-python | Principles, scenario taxonomy, naming, JUnit 5 / pytest / Jest templates |
| `rest-api-standards` | developer-java-spring, api-designer, code-reviewer | Resource modelling, HTTP methods, status codes, RFC 7807, OpenAPI 3.1 |
| `accenture-branding` | presentation-creator, document-creator | Colour palette, python-pptx constants, CSS PDF template, typography |
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
