#!/usr/bin/env python3
"""Replace the auto-generated `## When to invoke` blocks on the 47 pipeline-
   worker agents with bespoke content. Detects the auto-generated form by its
   template signature (`**Phase X dispatch.** Invoked by`) so the 20 bespoke
   sections written earlier are left intact.

   The 47 entries in BESPOKE were authored by hand (one per agent) using the
   four archetypes the registry-auditor recommended:
     - analyst / mapper:    findings + map outputs
     - writer / scaffolder: code/tests/docs generators
     - runner:              executes a suite, captures oracle
     - challenger:          adversarial gate at end of wave
     - synthesizer:         consolidates upstream outputs

   Idempotent: re-running on a file whose section is already bespoke is a no-op.
"""
from pathlib import Path
import re

ROOT = Path("/Users/luca.la.rosa/dev/claude-registry/claude-catalog/agents")

# Regex matches only the auto-generated block (template signature on first bullet)
AUTOGEN_RE = re.compile(
    r"## When to invoke\n\n- \*\*Phase \d+ dispatch\.\*\* Invoked by .*?\n\n---\n\n",
    re.DOTALL,
)

BESPOKE = {
    # ────────────────────────── BASELINE-TESTING (7) ─────────────────────────
    "baseline-testing/baseline-challenger.md": """## When to invoke

- **W3 challenger gate.** When `baseline-testing-supervisor` has finished W0–W2 and needs an adversarial review before declaring Phase 3 complete. Looks for coverage holes, AS-IS source modifications, non-determinism, oracle-integrity issues, severity-mismatch, and Streamlit/Postman pitfalls.
- **Pre-Phase-4 gate.** When the user is about to start Phase 4 and wants a final pass on the baseline before the AS-IS oracle is frozen.

Do NOT use this agent for: writing the actual tests (use `usecase-test-writer` / `integration-test-writer`), executing the suite (use `baseline-runner`), or fixing the issues found (the agent only flags).

---

""",
    "baseline-testing/baseline-runner.md": """## When to invoke

- **W2 execution wave.** When fixtures (W0) and tests (W1) are in place and the suite must be executed to capture the AS-IS oracle: snapshots, benchmark JSON, coverage report. Applies the failure policy (`xfail` / `skip` / `escalate`).
- **Re-run after fixture refresh.** When `tests/baseline/conftest.py` was regenerated (DB seed change, time-freeze update) and the oracle must be re-captured without re-authoring the tests.

Do NOT use this agent for: writing tests (use the W1 writers), running the TO-BE suite (use `tobe-test-runner`), or debugging individual failures (use `debugger`).

---

""",
    "baseline-testing/benchmark-writer.md": """## When to invoke

- **W1 performance authoring (per hot endpoint).** When the supervisor identifies hot endpoints from `docs/analysis/02-technical/` and dispatches one instance of this agent per endpoint to author `pytest-benchmark` scripts and memory profiling probes. Output: the AS-IS performance oracle for Phase 5 comparison.
- **Throughput probe (where applicable).** When the AS-IS app exposes services with measurable throughput (HTTP, queue consumers), this agent emits throughput probes alongside the latency benchmarks.

Do NOT use this agent for: functional regression tests (use `usecase-test-writer`), executing the benchmarks (use `baseline-runner`), or comparing AS-IS vs TO-BE (use `performance-comparator`).

---

""",
    "baseline-testing/fixture-builder.md": """## When to invoke

- **W0 deterministic foundation.** First wave of Phase 3; produces `tests/baseline/conftest.py` with seed/time/network determinism plus minimal/realistic/edge fixture sets that downstream W1 writers consume.
- **Determinism refresh.** When a flaky test or environment drift is traced to non-deterministic seeds, time, or network — regenerate the fixtures alone without touching the test suite.

Do NOT use this agent for: writing tests (use the W1 writers), executing (use `baseline-runner`), or producing TO-BE fixtures (Phase 5 has its own).

---

""",
    "baseline-testing/integration-test-writer.md": """## When to invoke

- **W1 integration coverage.** When the AS-IS app touches a database, file system, outbound API, or message queue; this agent writes mocked integration tests for each external boundary identified in `docs/analysis/02-technical/data-access-analyst.md` and `integration-analyst.md`.
- **Boundary-only re-author.** When a specific external integration (e.g., a single REST client) is added or changed in the AS-IS, regenerate the integration tests for that boundary alone.

Do NOT use this agent for: per-UC functional tests (use `usecase-test-writer`), benchmarks (use `benchmark-writer`), or live (non-mocked) integration (out of scope for the baseline).

---

""",
    "baseline-testing/service-collection-builder.md": """## When to invoke

- **W1 service-surface inventory (conditional).** When the AS-IS app exposes a non-trivial set of services (REST endpoints, gRPC, etc.) the supervisor dispatches this agent to emit a Postman 2.1 collection covering every public operation. Output: `tests/baseline/<app>.postman_collection.json`.
- **Surface refresh.** When new endpoints land mid-baseline, regenerate the collection without re-running the whole baseline pipeline.

Do NOT use this agent for: apps without an exposed service layer (the supervisor will skip this agent), authoring HTTP integration tests (use `integration-test-writer`), or running the collection.

---

""",
    "baseline-testing/usecase-test-writer.md": """## When to invoke

- **W1 fan-out per UC.** The supervisor dispatches one instance per use case from `docs/analysis/01-functional/`; this agent produces a single pytest module covering the happy path, alternative paths, and 1–2 representative edge cases for that UC alone.
- **Streamlit-aware UC.** When the UC surface includes Streamlit pages, the output uses `streamlit.testing.v1.AppTest` instead of HTTP assertions.

Do NOT use this agent for: integration boundaries (use `integration-test-writer`), benchmarks (use `benchmark-writer`), or executing the suite.

---

""",
    # ─────────────────────── FUNCTIONAL-ANALYSIS (6) ─────────────────────────
    "functional-analysis/actor-feature-mapper.md": """## When to invoke

- **W1 actor-feature foundation.** First wave of Phase 1; reads `.indexing-kb/` and produces the actor list, role/persona definitions, the full feature map of the application, and the Actor×Feature matrix at `docs/analysis/01-functional/actor-feature-map.md`. Downstream W2 agents consume this.
- **Actor coverage audit.** When an existing functional report needs verification — does every feature have a defined actor? Does every actor have at least one feature?

Do NOT use this agent for: implicit business logic (use `implicit-logic-analyst`), UI surface mapping (use `ui-surface-analyst`), or use-case sequence diagrams (use `user-flow-analyst`).

---

""",
    "functional-analysis/functional-analysis-challenger.md": """## When to invoke

- **W3 challenger gate (Streamlit default ON).** When all W1+W2 outputs are written; looks for gaps, contradictions, unverified claims, and AS-IS rule violations in the functional analysis. Default-ON for Streamlit codebases (where implicit-logic risk is high), opt-in otherwise.
- **Pre-deliverable gate.** When the user is about to ship the functional report PDF/PPTX and wants a final adversarial pass.

Do NOT use this agent for: writing the analysis (use the W1+W2 workers), making the fixes (the agent only flags), or technical analysis (Phase 2 has its own challenger).

---

""",
    "functional-analysis/implicit-logic-analyst.md": """## When to invoke

- **W2 deep-logic extraction (Streamlit-critical).** Reads sources flagged by `actor-feature-mapper` and extracts IMPLICIT business and validation logic embedded in widget parameters, conditional rendering, state-driven branches, callback chains, and cross-screen state mutations. Highest value in Streamlit codebases where UI/state/logic are interleaved.
- **Targeted re-run after a Streamlit refactor.** When a Streamlit screen was refactored mid-analysis, re-extract implicit logic for that screen alone.

Do NOT use this agent for: explicit business rules (those are surfaced by other Phase-1 agents), source-code refactoring (read-only), or TO-BE work.

---

""",
    "functional-analysis/io-catalog-analyst.md": """## When to invoke

- **W1 input/output inventory.** Catalogues every functional input the user/system provides and every output the application returns, plus the transformation matrix linking them. Functional perspective — not infrastructure perspective. Output at `docs/analysis/01-functional/io-catalog.md`.
- **Contract audit before Phase 4.** When the team wants to know exactly what data crosses the application boundary before designing the TO-BE API contract.

Do NOT use this agent for: data-access patterns (use `data-access-analyst` in Phase 2), implementation-side I/O concerns (use `data-flow-analyst` in Phase 0), or TO-BE OpenAPI design.

---

""",
    "functional-analysis/ui-surface-analyst.md": """## When to invoke

- **W1 UI inventory.** Catalogues every screen, the navigation map between screens, and the component tree per screen. Streamlit-aware — treats each page-script as a screen and widgets as first-class components.
- **Screen-by-screen audit.** When the team wants to verify UI completeness against the feature map before progressing to Phase 4.

Do NOT use this agent for: UI logic embedded in callbacks (use `implicit-logic-analyst`), TO-BE UI design (use `frontend-scaffolder` in Phase 4), or pixel-level styling.

---

""",
    "functional-analysis/user-flow-analyst.md": """## When to invoke

- **W2 use-case + flow synthesis.** Reads `actor-feature-map.md`, `ui-surface.md`, and `io-catalog.md` from W1 and derives use cases, user flows, and Mermaid sequence diagrams per UC. Streamlit-aware — handles reactive rerun-driven flows that have no explicit routing.
- **UC re-derivation after a feature change.** When a single feature's behaviour changed, re-derive the affected UCs without re-running W1.

Do NOT use this agent for: implicit logic capture (use `implicit-logic-analyst`), the actor or feature lists themselves (those are W1 inputs to this agent), or TO-BE flow design.

---

""",
    # ────────────────────────────── INDEXING (7) ──────────────────────────────
    "indexing/business-logic-analyst.md": """## When to invoke

- **Phase 0 deep-dive.** When the supervisor has the structural map and dependency graph and dispatches this agent to extract domain concepts (glossary), validation rules, business rules, and state machines from the source. Output at `.indexing-kb/05-business-logic/`.
- **Domain glossary refresh.** When new domain terms appear after a major source change.

Do NOT use this agent for: structural mapping (use `codebase-mapper`), data flow (use `data-flow-analyst`), or TO-BE domain modelling.

---

""",
    "indexing/codebase-mapper.md": """## When to invoke

- **Phase 0 entry — stack detection + structural map.** First Phase-0 agent; auto-detects primary language, frameworks, build tools, and test frameworks from the filesystem and dependency manifests, writes the canonical `stack.json`, then produces the directory tree, file/LOC counts, top-level package map, and entrypoint inventory at `.indexing-kb/02-structure/`.
- **Polyglot disambiguation.** When the repo contains multiple languages and the supervisor needs the primary stack identified before gating downstream framework-specific analyzers.

Do NOT use this agent for: dependency graphs (use `dependency-analyzer`), business logic (use `business-logic-analyst`), or any TO-BE work.

---

""",
    "indexing/data-flow-analyst.md": """## When to invoke

- **Phase 0 boundary inventory.** Identifies every place where data crosses the application boundary: database access, external API calls, file I/O, environment variables, configuration sources. Does not interpret what the data means — only WHERE it crosses. Output at `.indexing-kb/06-data-flow/`.
- **Pre-migration data audit.** When the team needs the full external-touchpoint inventory before designing Phase 4's TO-BE persistence and integration layers.

Do NOT use this agent for: business semantics of the data (use `business-logic-analyst`), per-module API documentation (use `module-documenter`), or implicit logic embedded in UI.

---

""",
    "indexing/dependency-analyzer.md": """## When to invoke

- **Phase 0 dependency mapping.** Extracts external dependencies from `pyproject.toml`/`requirements.txt`/`setup.py`/`Pipfile` and builds the internal module-import graph. Detects circular dependencies and standalone packages. Output at `.indexing-kb/03-dependencies/`.
- **Pre-Phase-4 dependency audit.** When the team wants the dependency posture before Phase 4 to inform target-stack ADRs.

Do NOT use this agent for: dependency-security CVE scanning (use `dependency-security-analyst` in Phase 2), data-flow inventory (use `data-flow-analyst`), or version bumps.

---

""",
    "indexing/module-documenter.md": """## When to invoke

- **Phase 0 module fan-out.** One invocation per top-level package in the repo, run in parallel. Documents each module end-to-end at the API level: purpose, public interface (exported classes/functions), key data structures, internal organisation. Output at `.indexing-kb/04-modules/<package-name>.md`.
- **Per-module refresh.** When a single package was significantly refactored and only its module doc needs regenerating.

Do NOT use this agent for: cross-module synthesis (use `synthesizer`), business-logic extraction (use `business-logic-analyst`), or TO-BE module design.

---

""",
    "indexing/streamlit-analyzer.md": """## When to invoke

- **Phase 0 Streamlit-specific audit (gated).** Runs only when `streamlit ∈ stack.frameworks`; analyses pages, `session_state` usage, widgets, caching (`@st.cache_data` / `@st.cache_resource`), navigation patterns, custom components, and Streamlit-specific anti-patterns. Critical for migration since Streamlit's reactive script-as-page model has no Angular equivalent.
- **Targeted Streamlit re-run.** When Streamlit pages were refactored mid-analysis.

Do NOT use this agent for: non-Streamlit Python apps (the supervisor skips this agent automatically), structural mapping (use `codebase-mapper`), or TO-BE UI design.

---

""",
    "indexing/synthesizer.md": """## When to invoke

- **Phase 0 closing wave (sequential).** Final agent of Phase 0; runs only after all other Phase-0 agents complete. Reads every prior KB output and produces the system overview, bounded-context hypothesis, complexity-hotspot map, and the index page at `.indexing-kb/00-overview.md`.
- **Re-synthesise after a partial Phase-0 refresh.** When one or more upstream KB sections were regenerated, re-synthesise the overview without re-running the workers.

Do NOT use this agent for: any individual analysis output (those are inputs to this agent), Phase-1 functional synthesis (different supervisor), or TO-BE architecture decisions.

---

""",
    # ─────────────────────────── REFACTORING-TOBE (9) ─────────────────────────
    "refactoring-tobe/api-contract-designer.md": """## When to invoke

- **W2 OpenAPI authoring.** After bounded-context decomposition (W1) is approved; produces the OpenAPI 3.1 contract as the single source of truth, the TO-BE Postman collection, and ADR-003 (auth flow). Downstream W3 BE+FE scaffolders consume the contract.
- **Contract-only refresh.** When the bounded-context map changed but the rest of Phase 4 work is in progress; regenerate just the contract + Postman collection.

Do NOT use this agent for: authoring controllers from the contract (use `backend-scaffolder`), client SDKs (use `frontend-scaffolder`), or AS-IS API documentation.

---

""",
    "refactoring-tobe/backend-scaffolder.md": """## When to invoke

- **W3 BE step 1 — Spring Boot 3 scaffold.** Reads the OpenAPI contract from W2; produces the Maven scaffold, controllers (one per OpenAPI tag), DTOs, services with TODOs, an RFC 7807 error handler, and a Spring Security baseline. The skeleton runs but every business method emits `TODO: implement` for `logic-translator` to fill.
- **Re-scaffold after contract change.** When the OpenAPI contract is renegotiated and the scaffold must be regenerated without re-running data mapping.

Do NOT use this agent for: per-UC business-logic translation (use `logic-translator`), JPA entities (use `data-mapper`), or front-end scaffolding (use `frontend-scaffolder`).

---

""",
    "refactoring-tobe/data-mapper.md": """## When to invoke

- **W3 BE step 2 — JPA + Liquibase.** Reads the AS-IS data model from `.indexing-kb/06-data-flow/` and the bounded contexts from W1; produces JPA entities, value objects, enums, Liquibase YAML changelogs, and Spring Data JPA repositories. DDD-honouring — aggregates and value objects respect the bounded-context boundaries.
- **Schema-only re-run.** When the AS-IS data model was re-indexed and the TO-BE persistence layer must be regenerated.

Do NOT use this agent for: Flyway migrations (forbidden — Liquibase only), business-logic translation (use `logic-translator`), or REST DTO design (DTOs come from `backend-scaffolder` via the contract).

---

""",
    "refactoring-tobe/decomposition-architect.md": """## When to invoke

- **W1 Phase-4 entry.** Reads every prior phase output and produces the bounded-context decomposition (DDD), the aggregate inventory, the AS-IS↔TO-BE module map, and ADR-001 (architecture style) + ADR-002 (target stack). This is the structural foundation downstream waves consume.
- **Bounded-context re-evaluation.** When the team wants to re-evaluate context boundaries after stakeholder feedback.

Do NOT use this agent for: API contract design (use `api-contract-designer`), logic translation (use `logic-translator`), or AS-IS analysis.

---

""",
    "refactoring-tobe/frontend-scaffolder.md": """## When to invoke

- **W3 FE — Angular 17+ workspace.** Reads the OpenAPI contract from W2 and the UI surface from Phase 1; produces a standalone-component Angular workspace with lazy modules per bounded context, an OpenAPI-typed client, plus translations of any Streamlit page surfaces into Angular routes/components.
- **FE re-scaffold after contract change.** When the OpenAPI contract changed and the typed client + module skeleton need regenerating.

Do NOT use this agent for: actual TS business logic per component (handled in implementation, not scaffold), backend work (use `backend-scaffolder`), or design-system theming (use the `design-expert` skill).

---

""",
    "refactoring-tobe/hardening-architect.md": """## When to invoke

- **W4 cross-cutting concerns.** After backend + frontend scaffolds are in place; produces observability (JSON logging + correlation-id, Micrometer + Prometheus, OpenTelemetry) and security (Spring Security 6 baseline, OWASP headers, CSP). Emits ADR-004 (observability) and ADR-005 (security).
- **Hardening refresh.** When a security or observability standard tightens and the cross-cutting concerns must be re-derived.

Do NOT use this agent for: feature-level code (W3 work), migration timing (use `migration-roadmap-builder`), or TO-BE testing.

---

""",
    "refactoring-tobe/logic-translator.md": """## When to invoke

- **W3 BE step 3 — fan-out per UC.** One invocation per UC: reads the AS-IS Python source for that UC, the matching Phase-1 use-case spec, and the Phase-3 baseline test for that UC; produces the Java/Spring service implementation that fills the `TODO: implement` left by `backend-scaffolder`. Strictly UC-scoped — never touches another UC's code.
- **UC re-translation.** When the AS-IS source for a single UC was refactored and the TO-BE translation must be regenerated for that UC alone.

Do NOT use this agent for: scaffolding new endpoints (use `backend-scaffolder`), JPA mapping (use `data-mapper`), or AS-IS source modifications.

---

""",
    "refactoring-tobe/migration-roadmap-builder.md": """## When to invoke

- **W5 strangler-fig roadmap.** After all Phase-4 implementation waves are complete; produces the per-bounded-context migration roadmap with milestones, rollback plans, go-live criteria, and AS-IS bug carry-over. Designed for staged cutover, not big-bang.
- **Roadmap revision.** When operational constraints (release windows, dependencies) change and the roadmap must reflect the new sequence.

Do NOT use this agent for: actual implementation work, performance comparison (use `performance-comparator` in Phase 5), or AS-IS analysis.

---

""",
    "refactoring-tobe/phase4-challenger.md": """## When to invoke

- **W6 Phase-4 challenger gate (always ON).** Final wave of Phase 4; produces the AS-IS↔TO-BE traceability matrix and runs 8 adversarial checks: coverage, OpenAPI↔code drift, ADR completeness, performance hypothesis, security regression, equivalence, AS-IS-only leak, and one cross-cutting probe.
- **Pre-Phase-5 gate.** When the user is about to start TO-BE testing and wants final assurance the Phase-4 outputs are coherent.

Do NOT use this agent for: writing the artefacts (use the W1–W5 workers), fixing the issues found (the agent only flags), or Phase-5 equivalence (use `tobe-testing-challenger`).

---

""",
    # ─────────────────────────── TECHNICAL-ANALYSIS (10) ──────────────────────
    "technical-analysis/code-quality-analyst.md": """## When to invoke

- **W1 code-quality scan.** Reads `.indexing-kb/` and produces the codebase map findings, duplication report, complexity hotspots, and monolith-decomposition smells. Output at `docs/analysis/02-technical/code-quality.md`.
- **Hotspot drill-down.** When a specific module is suspected of being a hotspot and the team wants targeted complexity metrics for that module alone.

Do NOT use this agent for: security or performance findings (use the dedicated W1 analysts), TO-BE refactor recommendations (Phase 4), or fixing the issues.

---

""",
    "technical-analysis/data-access-analyst.md": """## When to invoke

- **W1 data-access patterns.** Inventories how the AS-IS app reads/writes data: DB access patterns, file system, cache, serialization. Recognises Liquibase, Flyway, Django, and Rails migrations as a data point — Phase 4 will rebuild with Liquibase regardless.
- **N+1 audit.** When the team wants the inventory of suspected N+1 query patterns before Phase-3 benchmarks measure them.

Do NOT use this agent for: integration with external APIs (use `integration-analyst`), data semantics (use `business-logic-analyst` in Phase 0), or TO-BE persistence design.

---

""",
    "technical-analysis/dependency-security-analyst.md": """## When to invoke

- **W1 dependency posture.** Produces the dependency inventory, CVE register, deprecation watch, license posture, and an SBOM-lite JSON. May shell out to dependency scanners — that is the justified use of `Bash` access.
- **Pre-go-live security audit.** When a release is imminent and the dependency posture must be re-checked against the latest CVE feed.

Do NOT use this agent for: source-code security findings (use `security-analyst`), runtime CVE detection (this is static analysis), or vendoring decisions.

---

""",
    "technical-analysis/integration-analyst.md": """## When to invoke

- **W1 external integrations.** Inventories every outbound integration (REST, gRPC, MQ, file drop), captures auth/timeout/retry/circuit-breaker patterns per integration, and produces an integration map.
- **Pre-Phase-4 integration audit.** When the team needs the full external-touchpoint catalogue before designing TO-BE clients.

Do NOT use this agent for: data-access patterns (use `data-access-analyst`), API design (use `api-designer`), or TO-BE client implementation.

---

""",
    "technical-analysis/performance-analyst.md": """## When to invoke

- **W1 static performance scan.** Identifies N+1 candidates, hot loops, blocking I/O, and caching gaps via static analysis (no execution). Findings feed Phase-3 benchmark prioritisation.
- **Module-level perf audit.** When a single module is suspected of being a hot path and the team wants static-analysis findings for that scope.

Do NOT use this agent for: dynamic benchmarks (use `benchmark-writer` + `baseline-runner` in Phase 3), TO-BE/AS-IS comparison (use `performance-comparator` in Phase 5), or capacity planning.

---

""",
    "technical-analysis/resilience-analyst.md": """## When to invoke

- **W1 resilience scan.** Audits error handling, logging quality, silent failures, fallback chains. Identifies places where exceptions are swallowed or logs are missing context.
- **Failure-mode audit.** When the team needs the inventory of resilience holes before Phase-4 hardening.

Do NOT use this agent for: security findings (use `security-analyst`), runtime error tracking (this is static analysis), or implementing fixes.

---

""",
    "technical-analysis/risk-synthesizer.md": """## When to invoke

- **W2 unified risk register.** After all W1 analysts complete; consolidates findings into a unified risk register (MD/JSON/CSV), severity matrix, and remediation priority. Cross-domain — surfaces defects visible only when reasoning across multiple W1 outputs (e.g., security + observability + runtime).
- **Risk-only refresh.** When one or more W1 outputs were regenerated and the risk register must be re-synthesised without re-running W1.

Do NOT use this agent for: producing the W1 findings (those are inputs), making the fixes, or Phase-1 functional risk.

---

""",
    "technical-analysis/security-analyst.md": """## When to invoke

- **W1 security scan.** Audits OWASP Top 10 vulnerabilities, input validation, and secrets-in-code; produces a STRIDE threat model. Output at `docs/analysis/02-technical/security.md`.
- **Pre-release security gate.** When the team needs a focused security pass before a deployment.

Do NOT use this agent for: dependency CVEs (use `dependency-security-analyst`), runtime intrusion detection, or implementing fixes.

---

""",
    "technical-analysis/state-runtime-analyst.md": """## When to invoke

- **W1 runtime state audit.** Inventories session state, globals, and side effects; produces a state-flow diagram. Streamlit-aware — surfaces `session_state` patterns that have no direct Angular equivalent.
- **Session-state audit.** When a Streamlit refactor is being considered and the team needs the full session-state map.

Do NOT use this agent for: business-logic semantics (use `business-logic-analyst` in Phase 0), TO-BE state-management design, or implementation fixes.

---

""",
    "technical-analysis/technical-analysis-challenger.md": """## When to invoke

- **W3 challenger gate (always ON).** When all W1+W2 outputs are written; looks for gaps, contradictions, AS-IS violations, and unverified claims in the technical analysis.
- **Pre-deliverable gate.** When the user is about to ship the Phase-2 PDF/PPTX and wants a final adversarial pass.

Do NOT use this agent for: writing findings (use the W1 analysts), making fixes, or Phase-1 functional gap detection.

---

""",
    # ────────────────────────────── TOBE-TESTING (8) ──────────────────────────
    "tobe-testing/backend-test-writer.md": """## When to invoke

- **W1 TO-BE backend coverage.** Reads the OpenAPI contract and the Spring Boot 3 scaffold; emits JUnit 5 + Mockito + Testcontainers tests + Spring Cloud Contract per `operationId`. Coverage targets: >80% line, >70% branch.
- **Per-operationId re-author.** When a specific endpoint signature changed in the OpenAPI contract and only its tests need regenerating.

Do NOT use this agent for: AS-IS baseline tests (Phase 3), equivalence tests (use `equivalence-test-writer`), or front-end testing.

---

""",
    "tobe-testing/equivalence-synthesizer.md": """## When to invoke

- **W4 equivalence synthesis with PO sign-off.** Reads every Phase-5 test result (W1+W2+W3 outputs) and produces the deliverable `01-equivalence-report.md` with the equivalence matrix, severity-classified deltas, perf-comparison summary, security findings, and the PO sign-off block. This is the final go-live gate.
- **Report regeneration after a Phase-5 iteration.** When `tobe-testing-supervisor` re-dispatches with `Resume mode: iterate`; recompute the equivalence report from the latest results without re-running the tests.

Do NOT use this agent for: producing tests, executing tests, or AS-IS analysis.

---

""",
    "tobe-testing/equivalence-test-writer.md": """## When to invoke

- **W1 fan-out per UC.** One instance per UC from `docs/analysis/01-functional/`; produces a pytest harness that drives the deployed TO-BE and compares output against the Phase-3 AS-IS snapshot. HTTP-based for direct UCs, Playwright-based for Streamlit-derived UCs.
- **UC equivalence re-author.** When a single UC's behaviour changed in the TO-BE and its harness must be regenerated.

Do NOT use this agent for: backend-only tests (use `backend-test-writer`), executing the harness (use `tobe-test-runner`), or AS-IS work.

---

""",
    "tobe-testing/frontend-test-writer.md": """## When to invoke

- **W1 TO-BE frontend coverage.** Reads the Angular workspace from Phase 4; emits unit tests per component (RTL/Vitest/Jasmine depending on stack) plus Playwright E2E flows derived from `user-flow-analyst` outputs. Coverage target: >70% statement.
- **Component-only re-author.** When a single component's signature changed and only its tests need regenerating.

Do NOT use this agent for: backend tests (use `backend-test-writer`), equivalence tests (use `equivalence-test-writer`), or AS-IS work.

---

""",
    "tobe-testing/performance-comparator.md": """## When to invoke

- **W2 perf delta vs AS-IS baseline.** Reads the Phase-3 benchmark JSON and runs the same operations against the deployed TO-BE; emits a per-operation delta report (latency, throughput, memory). Required for the equivalence report's perf section.
- **Targeted operation comparison.** When a single hot path was optimised and the team wants the perf delta for that operation alone.

Do NOT use this agent for: writing benchmarks (use `benchmark-writer` in Phase 3), authoring functional tests, or AS-IS analysis.

---

""",
    "tobe-testing/security-test-writer.md": """## When to invoke

- **W1 TO-BE security coverage.** Reads the Phase-2 security findings and the Phase-4 hardening ADR; emits security-focused tests (auth bypass, injection, secret leakage, header presence) for the TO-BE deployment.
- **Per-finding re-author.** When a specific security finding was escalated/de-escalated and the matching test must be regenerated.

Do NOT use this agent for: dependency CVE scanning (use `dependency-security-analyst` in Phase 2), runtime monitoring, or AS-IS security analysis.

---

""",
    "tobe-testing/tobe-test-runner.md": """## When to invoke

- **W3 TO-BE execution wave.** When all Phase-5 W1+W2 tests are authored; this agent executes the full suite against the deployed TO-BE, captures snapshots, compares against the Phase-3 AS-IS oracle, and applies the failure policy (critical/high → escalate; medium/low → TBUG registry with `xfail`).
- **Iterative re-run on failures.** When the supervisor dispatches with `Resume mode: iterate, Iteration scope: failures-only`, re-run only the failing tests.

Do NOT use this agent for: writing tests, fixing the failures (the agent only reports), or AS-IS execution (use `baseline-runner` in Phase 3).

---

""",
    "tobe-testing/tobe-testing-challenger.md": """## When to invoke

- **W5 Phase-5 challenger gate.** Final wave of Phase 5; runs an adversarial review on the equivalence harness coverage, AS-IS oracle integrity, severity-classification consistency, and the PO sign-off block readiness.
- **Pre-go-live gate.** When the user is about to sign off `01-equivalence-report.md` and wants a final adversarial pass.

Do NOT use this agent for: writing tests, executing tests, or fixing the issues found.

---

""",
}


def main() -> None:
    rewritten, missing_signature, missing_bespoke = 0, [], []
    for rel_path, new_block in BESPOKE.items():
        p = ROOT / rel_path
        if not p.exists():
            missing_bespoke.append(rel_path)
            continue
        text = p.read_text(encoding="utf-8")
        if not AUTOGEN_RE.search(text):
            # Either already bespoke or never had the auto-gen block
            missing_signature.append(rel_path)
            continue
        new_text = AUTOGEN_RE.sub(new_block, text, count=1)
        p.write_text(new_text, encoding="utf-8")
        rewritten += 1
        print(f"  ✓ {rel_path}")
    print(f"\nDone: {rewritten}/{len(BESPOKE)} rewritten")
    for r in missing_signature:
        print(f"  - {r}: no auto-gen signature (already bespoke?)")
    for r in missing_bespoke:
        print(f"  ! {r}: file does not exist")


if __name__ == "__main__":
    main()
