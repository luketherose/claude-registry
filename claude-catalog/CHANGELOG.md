# Changelog

All notable changes to catalog capabilities are documented here.

Format: `[name@version] - YYYY-MM-DD` for releases, `[Unreleased]` for pending changes.

## [Unreleased]
### Added
- **`wiki-writer@0.1.0` (beta)** — sonnet, authors GitHub wikis for software projects organized around the **Diataxis framework** (Tutorials, How-to guides, Reference, Explanation). Reads the codebase, README, CHANGELOG, CONTRIBUTING, ADRs, and any `docs/` folder; produces a coherent multi-page wiki under `<repo>/wiki/` ready for PR review (`Home`, `_Sidebar`, `_Footer`, plus per-topic pages). Adapts tone and depth to one of five audience profiles (`end-user`, `contributor`, `operator`, `integrator`, `mixed`). Verifies every code reference, command, file path, and CLI flag against the actual repository state before writing — `> _Needs verification_` markers and a `Stale` block in the final summary surface anything that could not be confirmed. Two non-negotiable safety rails: (1) **Push policy** — never pushes to the wiki remote (`<repo>.wiki.git`) without explicit user authorization in the same session, because the wiki is a public-facing artifact whose accidental push is hard to revert; (2) **File-writing rule** — all output via `Write`/`Edit`, never via `Bash` heredoc / echo redirect / `tee` / `printf > file` (carries the same hardening applied to all phase pipelines after the 2026-04-28 Mermaid shell-injection incident). Each page carries an HTML-comment front matter (`audience`, `diataxis`, `last-verified`, `verified-against` commit SHA) for future stale-content audits. Tools: Read, Grep, Glob, Bash, Write, Edit, WebFetch.
- **TO-BE Testing pipeline (9 new agents, beta) — Phase 5 — workflow now full-cycle (Phases 0–5)** — final go-live gate. Validates the TO-BE codebase against the AS-IS baseline and produces the deliverable equivalence report signed by the Product Owner. Reads `tests/baseline/` (Phase 3 oracle), `docs/analysis/01-functional/` (Phase 1 UCs), `docs/refactoring/api/openapi.yaml` (Phase 4 contract), and `backend/` + `frontend/` (Phase 4 codebase). Authors backend tests (JUnit 5 + Mockito + Testcontainers + Spring Cloud Contract), frontend tests (Jest + Angular Testing Library + Playwright E2E), equivalence harness (TO-BE output vs Phase 3 snapshots), security tests (OWASP Top 10), performance comparison vs Phase 3 benchmarks (p95 ≤ +10% gate). Adaptive execution policy. Failure policy: critical/high regressions escalate; medium/low go to TBUG registry with xfail. AS-IS and TO-BE source code remain read-only.
  - `tobe-testing-supervisor@0.1.0` — opus, single entrypoint, dispatches 8 workers in 5 waves with HITL checkpoint after Wave 1; resume modes (skip/re-run/revise); per-step execution timing. Final go-live gate.
  - `equivalence-test-writer@0.1.0` — sonnet (W1, fan-out per UC), pytest harness driving TO-BE (HTTP or Playwright) and comparing against Phase 3 snapshots; classification: equivalent | accepted-difference | regression
  - `backend-test-writer@0.1.0` — sonnet (W1), JUnit 5 + Mockito unit, Testcontainers integration, Spring Cloud Contract per OpenAPI operationId; > 80% line, > 70% branch coverage targets per BC
  - `frontend-test-writer@0.1.0` — sonnet (W1), Jest + Angular Testing Library component tests + Playwright E2E specs derived from Phase 1 user-flows; equivalence at user-flow level (not pixel)
  - `security-test-writer@0.1.0` — sonnet (W1), OWASP Top 10 (A01-A10) coverage, auth tests, input validation, headers/CORS, optional ZAP baseline scan automation; cross-references Phase 2 SEC-NN findings to prevent regression
  - `performance-comparator@0.1.0` — sonnet (W2), Gatling or k6 load scenarios; p95/p99 deltas vs Phase 3 benchmark; flags > +10% (PO sign-off) and > +25% (escalate); env-caveat aware
  - `tobe-test-runner@0.1.0` — sonnet (W3), executes mvn verify + ng test + playwright + pytest equivalence; captures JaCoCo + Spring Cloud Contract verifier + Playwright traces + k6/Gatling JSON; only worker permitted to add `@Disabled`/`xfail`/`skip` markers; failure policy classifies and routes
  - `equivalence-synthesizer@0.1.0` — sonnet (W4), reads all prior outputs and produces `01-equivalence-report.md` (DELIVERABLE — PO sign-off) with per-UC verdict table, accepted-differences register, quality gate (8 items), sign-off slots; no new findings, only consolidation
  - `tobe-testing-challenger@0.1.0` — sonnet (W5, always ON), 8 adversarial checks: UC coverage gaps, OpenAPI↔TO-BE drift, AS-IS source modifications (forbidden), TO-BE source modifications in Phase 5 (forbidden), mocked-when-shouldn't, equivalence claim integrity, AS-IS-bug-carry-over consistency, PO sign-off completeness, performance gate compliance
  - `refactoring-supervisor` bumped to **2.0.0** (MAJOR milestone) — workflow now covers full AS-IS→TO-BE→validation journey (Phases 0–5); registered Phase 5 in the phase registry; added Phase 5 schematic; updated bootstrap detection table with row for Phase 5 (output root + PO sign-off state); updated workflow manifest schema with phase-5 entry (test_outputs, po_signoff)
- **Explicit skip / re-run / revise prompt at bootstrap for Phases 0, 3, and 4** — extends the same pattern already in place for Phases 1 and 2 to the remaining three phase supervisors. Each one now classifies the on-disk state in three modes (`fresh`, `resume-incomplete`, `complete-eligible`) and asks the user explicitly before doing anything when prior outputs are detected. Affects:
  - `indexing-supervisor` bumped to **0.2.0** — bootstrap detects existing `.indexing-kb/` and prompts skip / re-run / revise; default recommendation `skip`. Inconsistent state (manifest=partial/failed/missing) classified separately with `re-run` recommendation. Manifest tracks a new `resume_mode` field.
  - `baseline-testing-supervisor` bumped to **0.2.0** — bootstrap detects existing `tests/baseline/` + `docs/analysis/03-baseline/`; default recommendation `skip` because the oracle (snapshots + benchmarks) is precious — re-running resets the equivalence reference for Phase 5. Per-artifact overwrite prompts (snapshots, benchmark JSON) only fire when the user chose `re-run` or `resume-incomplete`.
  - `refactoring-tobe-supervisor` bumped to **0.2.0** — bootstrap detects existing `.refactoring-kb/` + `docs/refactoring/` + `backend/` + `frontend/`; default recommendation `skip` because re-running overwrites generated code that may have been hand-edited.
- **`exports-only` resume mode for Phases 1 and 2** — when the analysis is complete but the Accenture-branded PDF/PPTX is missing, the supervisor offers to regenerate only the missing exports without re-running the full analysis pipeline. Affects:
  - `functional-analysis-supervisor` bumped to **0.3.0** — bootstrap classifies the run as `exports-only-eligible` if the manifest reports `complete` and ≥ 1 of the two export files is missing on disk; offers `exports-only / full-rerun / skip` to the user (default = `exports-only`); when chosen, skips W1/W2/W3 entirely and dispatches only `document-creator` / `presentation-creator` for the missing file(s); existing analysis is preserved untouched; manifest tracks a new `resume_mode` field.
  - `technical-analysis-supervisor` bumped to **0.2.0** — same behaviour as Phase 1.
  - `refactoring-supervisor` bumped to **1.2.0** — bootstrap detection table adds a new sub-state `complete-but-exports-missing` for Phases 1 and 2; the per-phase prompt offers a fourth choice `regenerate-exports` (alongside `skip / re-run / revise`) when the sub-state is detected; selecting it dispatches the phase supervisor with `Resume mode: exports-only`. The choice is refused for Phases 0/3/4 (no PDF/PPTX exports there).
- **Phase 1 Export Wave (Accenture-branded PDF + PPTX)** — `functional-analysis-supervisor` bumped to **0.2.0**. After Wave 3 synthesis, the supervisor now dispatches `document-creator` and `presentation-creator` in parallel (always ON) to produce `docs/analysis/01-functional/_exports/01-functional-report.pdf` and `01-functional-deck.pptx`. The PDF is the consolidated functional reference for business stakeholders (system context, actor map, feature catalogue, UI map, full UC set, user flows, sequence diagrams, I/O catalogue, implicit logic, traceability matrix, open-questions register). The PPTX is the executive deck for the steering committee. Existing exports are never silently overwritten — explicit user confirmation in bootstrap. Same export contract as Phase 2.
- **Per-phase resume prompt in `refactoring-supervisor`** — bumped to **1.1.0**. Bootstrap now presents a detection table (one row per phase 0..4 with status / detected metadata / recommendation) and asks the user explicitly per phase whether to **skip / re-run / revise** for every phase that already has outputs. Inconsistent state (manifest reports `partial`/`failed`/`in-progress` or is missing/unreadable while the output root exists) is classified separately and recommended for re-run rather than auto-resumed. Replaces the previous behaviour of silent auto-skip when a phase was complete. Adds `--no-resume-prompt` opt-in to bypass when the user wants a guaranteed fresh run. Phase 1 schematic in the supervisor's pre-phase brief updated to include the new export wave.
- **TO-BE Refactoring pipeline (10 new agents, beta) — Phase 4** — FIRST phase of the workflow with target technologies (Spring Boot 3 + Angular). Reads Phases 0–3 outputs and produces the TO-BE codebase scaffold (backend + frontend), bounded-context decomposition, OpenAPI 3.1 contract, foundational ADRs, hardening configuration, and migration roadmap (strangler fig). Strict dependency chain with three HITL checkpoints (post-decomposition, post-API-contract, post-implementation). Code-generation scope is configurable: `scaffold-todo` (default — full scaffold + data layer + TODO markers for complex business logic with AS-IS source refs), `full` (complete translation), or `structural` (skeleton only). Adaptive verification (mvn compile + ng build best-effort). Inverse drift rule: target tech allowed; AS-IS-only references must be resolved through ADR. AS-IS source code remains read-only throughout.
  - `refactoring-tobe-supervisor@0.1.0` — opus, single entrypoint, dispatches 9 workers in 6 waves with parallel BE+FE tracks in W3 and per-UC fan-out for logic-translator. Three HITL checkpoints. Adaptive verification. Configurable iteration model (one-shot default; per-BC milestone for large repos).
  - `decomposition-architect@0.1.0` — sonnet (W1), bounded-context decomposition (DDD context map), aggregates with invariants, AS-IS↔TO-BE module mapping (every Phase 0 module covered), ADR-001 (modular monolith vs microservices), ADR-002 (Java 21 + Spring Boot 3.x + Angular 17+ + target DB)
  - `api-contract-designer@0.1.0` — sonnet (W2), OpenAPI 3.1 contract (single source of truth), `x-uc-ref` extension on every operation for traceability, Postman TO-BE collection, ADR-003 (auth flow), RFC 7807 ProblemDetail for errors, cursor-based pagination, idempotency-key required on POST writes; spectral validation
  - `backend-scaffolder@0.1.0` — sonnet (W3 BE step 1), Spring Boot 3 Maven scaffold organized per BC (api/application/domain/infrastructure), controllers from OpenAPI operationIds, DTOs, services with `UnsupportedOperationException` stubs and TODO markers, error handler `@ControllerAdvice` with RFC 7807, security config baseline (Spring Security 6 stateless + OAuth2 resource server)
  - `data-mapper@0.1.0` — sonnet (W3 BE step 2), JPA entities (one per aggregate / entity / value object), enums for state machines, value objects via `@Embeddable`, Flyway migrations (V<NN>__*.sql), Spring Data JPA repositories, idempotency-key persistence; greenfield-or-migration schema strategy decided from Phase 2 evidence
  - `logic-translator@0.1.0` — sonnet (W3 BE step 3, fan-out per UC), translates one UC from AS-IS Python to Java service-method bodies; replaces scaffolder's `UnsupportedOperationException` stubs; adds state-transition methods on entities; honors Phase 2 error handling (NEVER reproduces silent failures); cross-references Phase 3 baseline tests as oracle; never modifies AS-IS source code
  - `frontend-scaffolder@0.1.0` — sonnet (W3 FE), Angular 17+ workspace with standalone components, core layer (auth/error/correlation-id interceptors, auth/role guards), shared layer, one lazy-loaded feature module per BC with screens-as-components, OpenAPI typed client (typescript-angular generator at build time), Streamlit translations documented (session_state→signals, st.cache_data→shareReplay, etc.)
  - `hardening-architect@0.1.0` — sonnet (W4), production hardening: structured JSON logging via logstash-logback-encoder + MDC correlation-id, Micrometer + Prometheus metrics, OpenTelemetry tracing, Spring Security 6 baseline (OWASP secure headers, /actuator gating, CORS allowlist), frontend CSP via meta tag, secrets via env (.env.example), ADR-004 (observability) + ADR-005 (security baseline)
  - `migration-roadmap-builder@0.1.0` — sonnet (W5), strangler-fig roadmap with per-BC milestones, cutover topology (reverse proxy / API gateway / DNS), rollback plans + triggers, go-live criteria (equivalence vs Phase 3, p95 ≤ 110% baseline, security sign-off), AS-IS bug carry-over table (deferred from Phase 3), Mermaid Gantt + topology diagrams; stakeholder-facing TL;DR ≤ 1 page
  - `phase4-challenger@0.1.0` — sonnet (W6, always ON), produces the AS-IS↔TO-BE traceability matrix as JSON (UC→endpoint→service→component) + 8 adversarial checks: coverage gaps (orphan UCs, orphan TO-BE files), OpenAPI↔code drift, ADR completeness (Nygard sections), AS-IS bug carry-over consistency, performance hypothesis sanity, security regression, equivalence claims integrity, AS-IS-only leak in TO-BE (inverse drift), AS-IS source modification detection (forbidden — flags as blocking)
- **Baseline Testing pipeline (8 new agents, beta)** — supervisor pattern for **Phase 3 AS-IS Baseline Testing** of a refactoring/migration workflow. Reads `.indexing-kb/`, `docs/analysis/01-functional/` (Phase 1), and `docs/analysis/02-technical/` (Phase 2) and produces the regression baseline suite at `tests/baseline/` (pytest, fixtures, snapshots, benchmarks, optional Postman collection if services are exposed) plus the report at `docs/analysis/03-baseline/`. The baseline serves as the AS-IS oracle for Phase 5 equivalence testing. Strictly AS-IS — never references target technologies. Adaptive execution policy: detects whether the env can run pytest and switches between write+execute and write-only. Failure policy on red tests: critical/high escalate; medium/low get xfail with AS-IS bug record; AS-IS source code is NEVER modified.
  - `baseline-testing-supervisor@0.1.0` — opus, single entrypoint, dispatches 7 sub-agents in 4 waves (W0 fixtures sequential / W1 authoring with per-UC fan-out + integration + benchmark + optional service-collection / W2 sequential execution & oracle capture / W3 challenger always ON). Per-step recap with execution timings. Strict human-in-the-loop with explicit overwrite confirmation for existing oracle artifacts.
  - `fixture-builder@0.1.0` — sonnet (W0), `conftest.py` with global determinism setup (seed=42, time freeze, network mock) + minimal/realistic/edge fixtures + pytest factories
  - `usecase-test-writer@0.1.0` — sonnet (W1, fan-out per UC), one pytest module per UC covering happy path, alternative flows, and edge cases; uses `streamlit.testing.v1.AppTest` where applicable
  - `integration-test-writer@0.1.0` — sonnet (W1), DB / file system / outbound external API tests (mocked via responses/respx); cache-correctness tests (especially user-scoped invalidation)
  - `benchmark-writer@0.1.0` — sonnet (W1), per-UC pytest-benchmark scripts + memory profiling (tracemalloc) + optional throughput probes; produces the AS-IS performance oracle for Phase 5 relative SLA gating
  - `service-collection-builder@0.1.0` — sonnet (W1, conditional — dispatched only if Phase 2 detects exposed services), Postman 2.1 collection per service with happy + edge requests, auth setup, response assertions, environment file (placeholders only — never real secrets)
  - `baseline-runner@0.1.0` — sonnet (W2), executes the suite via pytest (or validates structure-only in write-only mode), captures snapshots, benchmark JSON, coverage JSON; applies the failure policy: critical/high escalate, medium/low get xfail with `BUG-NN` reference; only worker permitted to add `xfail`/`skip` markers; never modifies AS-IS source code
  - `baseline-challenger@0.1.0` — sonnet (W3, always ON), seven adversarial checks: coverage gaps (every UC has a test), AS-IS source modifications (forbidden — flags any), determinism risks (raw network/time/random), oracle integrity (snapshots + benchmark JSON + coverage JSON exist), severity-mismatch in bug dispositions, Streamlit-specific risks (session_state leak, cache not cleared), Postman collection integrity (no real secrets, valid 2.1 schema)
- **Technical Analysis pipeline (11 new agents, beta)** — supervisor pattern for **Phase 2 AS-IS Technical Analysis** of a refactoring/migration workflow. Reads `.indexing-kb/` (Phase 0) and optionally `docs/analysis/01-functional/` (Phase 1) and produces a complete technical understanding at `docs/analysis/02-technical/`, plus an Accenture-branded PDF and PPTX export. Strictly AS-IS — never references target technologies. Stack-aware (Streamlit-aware where applicable). The supervisor adaptively chooses between parallel, batched, and sequential dispatch based on KB size and user flag:
  - `technical-analysis-supervisor@0.1.0` — opus, single entrypoint, dispatches 8 W1 workers in mode-dependent fashion + W2 synthesizer (sequential) + W3 challenger (always ON) + parallel export wave (PDF + PPTX). Decision tree for dispatch mode based on module count and LOC. Strict human-in-the-loop with explicit overwrite confirmation for existing exports.
  - `code-quality-analyst@0.1.0` — sonnet (W1), codebase map, logical-component classification, duplication report, complexity hotspots, monolith smells (Streamlit god-page detection)
  - `state-runtime-analyst@0.1.0` — sonnet (W1), session state inventory, module globals, side effects, state-flow diagram (Mermaid), execution-order analysis (Streamlit reactive-rerun aware)
  - `dependency-security-analyst@0.1.0` — sonnet (W1), dependency inventory, version pinning posture, known CVEs/GHSAs (static analysis), deprecation watch, license posture; produces SBOM-lite JSON
  - `data-access-analyst@0.1.0` — sonnet (W1), data-flow diagrams, DB/file/cache/serialization access patterns; cross-references Phase 1 transformations when available
  - `integration-analyst@0.1.0` — sonnet (W1), external integrations inventory (HTTP, message queues, webhooks); per-integration auth/timeout/retry/idempotency analysis with Mermaid integration map
  - `performance-analyst@0.1.0` — sonnet (W1), N+1 patterns, hot loops, blocking I/O, missing caching, memory-heavy operations, Streamlit rerun cost. Static analysis only.
  - `resilience-analyst@0.1.0` — sonnet (W1), error-handling audit (silent failures, secret leaks in logs), retry/circuit-breaker inventory, fallback chains, Streamlit page-level resilience
  - `security-analyst@0.1.0` — sonnet (W1), OWASP Top 10 (2021) coverage, input-validation audit, secrets in code, STRIDE threat model. Complements `dependency-security-analyst` (library CVEs)
  - `risk-synthesizer@0.1.0` — sonnet (W2), consolidates all W1 findings into unified risk register (markdown + JSON + CSV), severity matrix (likelihood × impact), ordered remediation backlog (AS-IS scope only). Cross-references Phase 1 features and use cases when available. Discovers no new findings.
  - `technical-analysis-challenger@0.1.0` — sonnet (W3, always ON), six adversarial checks: orphan IDs, contradictions, unverified claims, coverage gaps, AS-IS violations (target-tech leak detection), Streamlit-specific risks. Flags but does not rewrite.
- **Refactoring workflow supervisor (1 new agent, beta)** — top-level workflow agent for end-to-end refactoring/migration on a codebase. One layer above the phase supervisors: delegates each phase sequentially via the Agent tool, never performs analysis itself. Strict human-in-the-loop with mandatory pre-phase brief (including a schematic of the upcoming phase's parallelization) and post-phase recap (with next-phase preview). Designed for extension to later phases:
  - `refactoring-supervisor@1.0.0` — **MAJOR milestone**: workflow now covers the full AS-IS→TO-BE journey (Phases 0–4). Coordinates Phase 0 (`indexing-supervisor`), Phase 1 (`functional-analysis-supervisor`), Phase 2 (`technical-analysis-supervisor`), Phase 3 (`baseline-testing-supervisor`), and Phase 4 (`refactoring-tobe-supervisor` — first phase with target tech: Spring Boot + Angular). Bumped from 0.3.0 to 1.0.0 to mark the milestone of cross-phase coverage. Updates: registered Phase 4 in phase registry; added Phase 4 schematic; updated bootstrap detection (`.refactoring-kb/`, `backend/`, `frontend/`); inverse drift rule (target tech allowed; AS-IS-only leaks forbidden) documented from Phase 4 onward; activation examples extended.
- **Functional Analysis pipeline (6 new agents, beta)** — supervisor pattern for **Phase 1 AS-IS Functional Analysis** of a refactoring/migration workflow. Reads the knowledge base produced by Phase 0 indexing (`.indexing-kb/`) and produces a complete functional understanding at `docs/analysis/01-functional/`. Strictly AS-IS — never references target technologies. Generic and reusable across migration scenarios; Streamlit-aware where applicable:
  - `functional-analysis-supervisor@0.1.0` — opus, single entrypoint, dispatches 5 sub-agents in 3 waves (W1 discovery / W2 behavior / W3 synthesis), produces traceability matrix + unresolved questions, escalates to user on ambiguity, default Streamlit-mode adjustments
  - `actor-feature-mapper@0.1.0` — sonnet (W1), actors + features + Actor×Feature matrix (tightly coupled because who-can-do-what is one concept)
  - `ui-surface-analyst@0.1.0` — sonnet (W1), screens + navigation graph + component tree, Streamlit-aware (page-as-screen, widgets-as-components, reactive transitions)
  - `io-catalog-analyst@0.1.0` — sonnet (W1), inputs + outputs + transformation matrix (functional perspective, not infrastructure)
  - `user-flow-analyst@0.1.0` — sonnet (W2), use cases + user flows + Mermaid sequence diagrams with reruns made explicit
  - `implicit-logic-analyst@0.1.0` — sonnet (W2), hidden validation, state machines, callback chains, magic numbers, silent fallbacks; complements (does not duplicate) `business-logic-analyst` from Phase 0
  - `functional-analysis-challenger@0.1.0` — sonnet (W3, opt-in; default ON in Streamlit mode), adversarial review for gaps, contradictions, unverified claims, AS-IS violations; flags but does not rewrite
- `examples/developer-java-spring-example.md` — 3 scenarios: new CRUD endpoint, N+1 fix, code review against standards
- `examples/functional-analyst-example.md` — 3 scenarios: requirements reconstruction, acceptance criteria, CRUD matrix
- `evals/developer-java-spring-eval.md` — 5 evals: CRUD happy path, N+1 fix, code review, Spring Security baseline, refusal of insecure shortcut
- `evals/functional-analyst-eval.md` — 5 evals: requirements reconstruction, acceptance criteria, gap analysis, CRUD matrix, scope-discipline (architecture refusal)
- `evals/software-architect-eval.md` — 5 evals: ADR with alternatives, architecture review, integration pattern, scope-discipline (code refusal), NFR quantification

### Fixed
- `claude-catalog/agents/functional-analyst.md` — updated stale skill reference `analysis/functional-analyst` → `analysis/functional-reconstruction` (left over from the rename in PR #3)

### Changed
- `functional-analyst` skill renamed to `functional-reconstruction` to eliminate the agent/skill name collision (the agent `functional-analyst` and the skill of the same name were ambiguous). The skill's purpose is unchanged: reconstructing functional behaviour from a codebase.
- `validate_catalog.py` — example/eval warnings now fire only for **stable** agents (the warning text already said "before promoting to stable"; the rule now matches the message). Beta agents and skills no longer trigger these warnings. Reduces noise from 116 warnings to 6 (the 5 genuinely missing examples/evals on stable agents + 1 model: opus justification).

### Added
- **Indexing pipeline (8 new agents, beta)** — supervisor pattern for indexing legacy Python codebases (with optional Streamlit) into a markdown knowledge base at `<repo>/.indexing-kb/`. Phase 1 only — indexing and understanding, not migration:
  - `indexing-supervisor@0.1.0` — opus, single entrypoint, dispatches sub-agents in 4 phases (structural / module fan-out / cross-cutting / synthesis), escalates to user on ambiguity
  - `codebase-mapper@0.1.0` — sonnet, structural inventory (tree, LOC, language stats, entrypoints)
  - `dependency-analyzer@0.1.0` — sonnet, external deps + internal import graph + cycles
  - `streamlit-analyzer@0.1.0` — sonnet, pages, session_state, widgets, caching, custom components, migration-relevant anti-patterns
  - `module-documenter@0.1.0` — sonnet, per-package API documentation (parallelizable)
  - `data-flow-analyst@0.1.0` — sonnet, DB / external APIs / file I/O / env vars / configuration
  - `business-logic-analyst@0.1.0` — sonnet, domain concepts, validation rules, business rules, state machines
  - `synthesizer@0.1.0` — sonnet, final consolidation (system overview, bounded context hypothesis, complexity hotspots, index page)
- `orchestrator@2.0.0` — promoted from skill to **agent** (`model: opus`, `tools: Read, Glob, Agent`). Stack-agnostic meta-orchestrator: dynamically discovers installed agents (no hardcoded list), decomposes requests into a phase-based dependency graph, dispatches specialists in parallel where independent, and synthesises their outputs into a unified result. Replaces the previous skill-based orchestrator (1.1.0).
- `developer-frontend@0.1.0` — new agent: multi-framework frontend developer (Angular, React/Next.js/TanStack, Vue 3, Qwik, Vanilla JS/TS); auto-detects stack and loads only relevant skills

### Removed
- `orchestrator` skill (superseded by `orchestrator` agent at 2.0.0 — the skill could only describe plans, the agent actually dispatches them)
- `migration-orchestrator` skill — language/stack-specific workflow template; subsumed by the general meta-orchestrator agent which handles any migration scenario through dynamic agent discovery
- `porting-orchestrator` skill — same rationale as migration-orchestrator
- 36 new skills published to marketplace: `tech-analyst`, `java-expert`, `spring-architecture`, `spring-data-jpa`, `spring-expert`, `postgresql-expert`, `backend-documentation`, `doc-expert`, `documentation-orchestrator`, `frontend-documentation`, `functional-document-generator`, `angular-expert`, `ngrx-expert`, `rxjs-expert`, `css-expert`, `design-expert`, `qwik-expert`, `nextjs`, `react-expert`, `tanstack-query`, `tanstack-start`, `tanstack`, `vanilla-expert`, `vue-expert`, `backend-orchestrator`, `frontend-orchestrator`, `migration-orchestrator`, `orchestrator`, `porting-orchestrator`, `python-expert`, `streamlit-expert`, `dependency-resolver`, `refactoring-expert`, `caveman-commit`, `caveman-review`, `caveman`

### Changed
- `claude-catalog/agents/` — indexing pipeline agents grouped under `agents/indexing/` subdirectory for organization (8 files moved). Marketplace stays flat per existing convention.

### Fixed
- `validate_catalog.py` — agents directory scan now uses `rglob` (recursive) to support thematic subdirectories like `agents/indexing/`. Skills already used `rglob`; this aligns the two.
- `validate_catalog.py` — added `check_marketplace_sync`: every agent/skill in catalog must have a matching entry in `claude-marketplace/catalog.json` or the PR is blocked
- `validate_catalog.py` — skills scan now uses `rglob` to handle subdirectory structure
- `validate_marketplace.py` — added `skill` as valid tier; fixed path convention for skills (`skills/{name}.md`); orphan check now covers `skills/` directory; all warnings promoted to errors
- `validate_catalog.py` — added `check_model_conventions`: enforces model: haiku for skills, model: sonnet for general orchestrator, model: haiku for specialized orchestrators, model: sonnet/opus for agents; warns on model: opus usage
- `validate_catalog.py` — added `check_orchestrator_parallel_section`: warns if orchestrator skill is missing `## Parallel execution` section

### Changed
- All 37 skills in `claude-catalog/skills/` — add `name`, `tools: Read`, `model: haiku` frontmatter fields; rewrite `description` to start with "Use when/for/to"; add `## Role` section; remove `$ARGUMENTS` template artefact; translate `utils/caveman.md` body to English UK
- `orchestrator@1.1.0` — model upgraded haiku → sonnet; added `## Parallel execution` section with independence criterion, dependency graph pattern (anchor → fan-out → convergence), structured `parallel_plan` YAML output format, worktree isolation guidance, and concrete parallelization examples
- `backend-orchestrator@1.1.0` — added `## Parallel execution` section with independence criterion, phase model, and backend-specific parallelizable pairs (postgresql-expert ∥ java-expert; spring-expert ∥ test-writer) and sequential constraints
- `frontend-orchestrator@1.1.0` — added `## Parallel execution` section with frontend-specific parallelizable pairs (design-expert ∥ css-expert; component impl ∥ unit tests) and sequential constraints
- `migration-orchestrator@1.1.0` — added `## Parallel execution` section with migration-specific parallel rules (independent bounded contexts, FE ∥ BE when API contract is stable)
- `porting-orchestrator@1.1.0` — added `## Parallel execution` section with porting-specific parallel rules (independent features, FE ∥ BE when API contract defined)

### Added
- `java-spring-standards@1.0.0` — skill: Java/Spring Boot standards (package structure, layering, testing, error handling, logging, security, observability)
- `testing-standards@1.0.0` — skill: testing principles, scenario taxonomy, JUnit 5 + pytest + Jest templates
- `accenture-branding@1.0.0` — skill: Accenture brand palette, python-pptx constants, CSS template; migrated from policies/
- `rest-api-standards@1.0.0` — skill: REST design rules, HTTP methods, status codes, RFC 7807, OpenAPI 3.1

### Changed
- `developer-java-spring@1.1.0` — delegates standards to java-spring-standards, testing-standards, rest-api-standards skills
- `test-writer@0.2.0` — delegates to testing-standards and java-spring-standards skills
- `code-reviewer@0.2.0` — delegates to java-spring-standards, testing-standards, rest-api-standards skills (fulfills v1.0 TODO)
- `api-designer@0.2.0` — delegates to rest-api-standards skill
- `presentation-creator@0.2.0` — delegates to accenture-branding skill
- `document-creator@0.2.0` — delegates to accenture-branding skill

### Removed
- `policies/accenture-branding.md` — migrated to skill
- `policies/java-spring-conventions.md` — merged into java-spring-standards skill

### Documentation
- `README.md` — updated: skills layer, repo structure, full capability+skill tables, corrected PPTX link
- `docs/quick-start.md` — updated: skills explanation, setup script instructions, full capability list
- `CONTRIBUTING.md` — updated: skill workflow, skill PR requirements
- `how-to-write-a-capability.md` — updated: section 0 on skills (format, constraints, composition)
- `GOVERNANCE.md` — updated: capability types table (agent vs. skill), lifecycle states
- `review-checklist.md` — updated: section 9 for skill-specific checks
- `scripts/new-capability.sh` — updated: `--type skill` flag for skill scaffolding
- `CLAUDE.md` (root) — created: project-level instructions for documentation maintenance rule


### Added
- Initial catalog structure
- `software-architect@1.0.0` — full capability
- `functional-analyst@1.0.0` — full capability
- `developer-java-spring@1.0.0` — full capability
- `technical-analyst@0.1.0` — initial draft (beta)
- `developer-python@0.1.0` — initial draft (beta)
- `code-reviewer@0.1.0` — initial draft (beta)
- `test-writer@0.1.0` — initial draft (beta)
- `debugger@0.1.0` — initial draft (beta)
- `api-designer@0.1.0` — initial draft (beta)
- `documentation-writer@0.1.0` — initial draft (beta)
- `presentation-creator@0.1.0` — Accenture-branded PPTX creator for project/estimation presentations (beta)
- `document-creator@0.1.0` — Accenture-branded PDF/DOCX creator for project/estimation documents (beta)
- `policies/accenture-branding.md` — brand specification: color palette, typography, CSS/python-pptx constants

---

## Release format reference

```
## [software-architect@1.1.0] - 2026-05-01

### Changed
- Enhanced trade-off analysis output format to include cost dimension
- Added explicit guidance for cloud-native patterns

## [software-architect@1.0.0] - 2026-04-19

### Added
- Initial release
```

### Change types

- `Added` — new capability or new section in existing capability
- `Changed` — behavior change, prompt improvement, model change
- `Fixed` — bug fix in prompt (e.g. missing instruction causing wrong output)
- `Deprecated` — capability will be removed in a future release
- `Removed` — capability removed from marketplace
- `Breaking` — name, description, or tools change requiring consumer action
