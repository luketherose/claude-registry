# Language-agnostic refactoring pipeline — design

**Status**: draft
**Owner**: catalog maintainers
**Last updated**: 2026-04-28
**Tracking PR**: `refactor/language-agnostic-supervisors`

This document describes the target design for the refactoring pipeline
(Phases 0-5 + top-level `refactoring-supervisor`) after the
**language-agnostic refactoring**. Today the pipeline is hardcoded for
the AS-IS = Python (+ optional Streamlit) and TO-BE = Java/Spring Boot 3
+ Angular. The goal is to make every supervisor and every sub-agent
free of language-specific assumptions, and to push all language-specific
behaviour into the `developer-*` agents and language-specific skills.

This is a **design document**, not an implementation. Implementation
proceeds in subsequent PRs (one per phase) following the migration plan
at the end of this document.

---

## Goals

1. **Supervisors are language-agnostic**. Their prompts contain no
   reference to Python, Streamlit, Java, Spring, Angular, JPA, etc.
2. **AS-IS detection is autonomous**. Phase 0 detects the AS-IS stack
   from the codebase; Phases 1-3 read this without re-detecting.
3. **TO-BE is decision-driven, not auto-detected**. Phase 4 reads the
   target stack from ADR-002 (or an explicit user argument) — there is
   no default. Phase 5 detects the TO-BE stack from the just-generated
   TO-BE codebase.
4. **Language-specific knowledge lives in two places only**:
   - `developer-*` agents (one per target language)
   - language/framework skills (e.g. `python-expert`, `streamlit-expert`,
     `spring-expert`, `angular-expert`)
5. **Dispatch is table-driven**. Supervisors look up which developer
   agent and which skills to engage from a single canonical mapping.
6. **No regression in capability**. Whatever the current Python →
   Java/Spring + Angular pipeline can do today, the agnostic pipeline
   must still do — just with the knowledge wired up dynamically.

## Non-goals (for the first iteration)

- Supporting every language pair. The first agnostic implementation
  must support, at minimum: Python, Java, Kotlin, C#, Go, Rust, Ruby,
  PHP, TypeScript/JavaScript (frontend frameworks). Less common stacks
  (Scala, Swift, Elixir, Haskell, …) are deferred to a follow-up PR
  that adds a developer agent + skill.
- Fully automated TO-BE selection. The user (via ADR-002 or a flag)
  must declare the target stack — auto-selection of the target is out
  of scope.
- Cross-language migrations beyond what current skills cover. Existing
  migration skills (`python-to-java-migration-expert`,
  `python-to-react-migration-expert`, `python-to-angular-migration-expert`)
  remain pair-specific. A `python-to-go` migration would need a new
  skill or a generic migration framework — neither is in scope here.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  refactoring-supervisor (opus, top-level)                        │
│  language-agnostic prompt; reads stack from manifest             │
│  delegates phases sequentially with HITL between them            │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ▼
   ┌─────────────────────────────────────────────────────────────┐
   │  PHASE 0 — Indexing (AS-IS auto-detection)                  │
   │  indexing-supervisor                                         │
   │   └─ codebase-mapper                                         │
   │      ├─ detects languages (file ext + manifest files)       │
   │      ├─ detects frameworks (Streamlit, Rails, Spring, etc.)│
   │      └─ writes _meta/manifest.json `stack:` block ◄────────┐│
   │   └─ stack-aware sub-agents                                ││
   │      e.g. streamlit-analyzer runs ONLY if stack=Streamlit  ││
   └─────────────────────────────────────────────────────────────┘
           │                                                      │
           ▼                                                      │
   ┌─────────────────────────────────────────────────────────────┐│
   │  PHASE 1 — Functional analysis (reads stack from manifest) ││
   │  PHASE 2 — Technical analysis (reads stack from manifest)  ││
   │  PHASE 3 — Baseline testing (reads stack from manifest)    ││
   │   └─ Each supervisor selects sub-agents/skills via the     ││
   │      DISPATCH TABLE based on stack.languages               ││
   └─────────────────────────────────────────────────────────────┘│
           │                                                      │
           ▼                                                      │
   ┌─────────────────────────────────────────────────────────────┐│
   │  PHASE 4 — TO-BE refactoring                                ││
   │  refactoring-tobe-supervisor                                ││
   │   └─ decomposition-architect produces ADR-002 (target stack)││
   │   └─ supervisor reads ADR-002 → selects target developer   ││
   │      agent (e.g. developer-go) + target skills             ││
   │   └─ writes TO-BE codebase + manifest.tobe.stack           ││
   └─────────────────────────────────────────────────────────────┘│
           │                                                      │
           ▼                                                      │
   ┌─────────────────────────────────────────────────────────────┐│
   │  PHASE 5 — TO-BE testing                                    ││
   │  tobe-testing-supervisor                                    ││
   │   └─ codebase-mapper-light (re-runs on TO-BE) writes        ││
   │      _meta/manifest.tobe.json `stack:` block ──────────────┘│
   │   └─ supervisor selects test framework / harness based      │
   │      on TO-BE stack (e.g. JUnit 5 if Java, pytest if Python,│
   │      go test if Go, cargo test if Rust, …)                  │
   └─────────────────────────────────────────────────────────────┘
```

The `stack:` block in `.indexing-kb/_meta/manifest.json` is the
**single source of truth** for AS-IS language information.
The `stack:` block in `tests/baseline/_meta/manifest.tobe.json` (or
similar) holds the TO-BE language information after Phase 4.

---

## Stack detection schema

Both AS-IS (`manifest.json`) and TO-BE (`manifest.tobe.json`) follow
the same schema:

```json
{
  "stack": {
    "primary_language": "python",
    "languages": ["python", "typescript"],
    "frameworks": ["streamlit", "fastapi"],
    "build_tools": ["uv", "npm"],
    "package_managers": ["pip", "npm"],
    "runtime": "cpython 3.11",
    "test_frameworks": ["pytest"],
    "confidence": "high",
    "evidence": [
      "pyproject.toml at repo root",
      "12 .py files, 0 .java files",
      "import streamlit as st in app.py:1",
      "package.json with @angular/cli@17 in frontend/"
    ]
  }
}
```

### Detection rules (from `codebase-mapper`)

The detection logic — invoked by `codebase-mapper` (Phase 0) and by
`codebase-mapper-light` (Phase 5) — applies these rules in order:

| Marker | Implies |
|---|---|
| `pyproject.toml`, `setup.py`, `requirements.txt`, `Pipfile` | language: python |
| `package.json` | language: typescript or javascript (ts if tsconfig.json present) |
| `pom.xml`, `build.gradle*` | language: java (or kotlin if `*.kt` files present) |
| `Cargo.toml` | language: rust |
| `go.mod` | language: go |
| `*.csproj`, `*.sln`, `global.json` | language: csharp |
| `Gemfile`, `*.gemspec` | language: ruby |
| `composer.json`, `composer.lock` | language: php |
| `import streamlit` in any .py file | framework: streamlit |
| `from fastapi`, `import fastapi` | framework: fastapi |
| `from django` | framework: django |
| `from flask` | framework: flask |
| `@SpringBootApplication`, `org.springframework` | framework: spring-boot |
| `angular.json`, `@angular/core` | framework: angular |
| `next.config.{js,ts,mjs}` | framework: nextjs |
| `nuxt.config.{js,ts}` | framework: nuxt |
| `vite.config.{js,ts}` | build tool: vite |
| `qwik.config.ts`, `@builder.io/qwik` | framework: qwik |
| `vue.config.js`, `*.vue` files | framework: vue |
| `Cargo.toml` with `axum` dep | framework: axum |
| `Cargo.toml` with `actix-web` dep | framework: actix-web |
| `go.mod` with `gin-gonic`, `chi`, etc. | framework: gin / chi / etc. |
| `app/Http/Controllers/` | framework: laravel |
| `bin/console` + `symfony/framework-bundle` | framework: symfony |
| `config/routes.rb` | framework: rails |
| `Sinatra::Base` | framework: sinatra |
| `*.sln` + `Microsoft.AspNetCore` package | framework: aspnet-core |
| Multiple language markers | report as polyglot in `languages[]`, primary = the one with most LOC |

`confidence` is `high` if ≥ 2 independent markers agree, `medium` if 1
strong marker, `low` if only file extensions match.

`evidence` is a list of human-readable strings citing where each
finding comes from (file path, line, count). This is mandatory for
auditability.

---

## Dispatch table

The canonical mapping language → developer agent + invocable skills.
This table is **the only place where language-specific knowledge lives
inside the supervisor layer**. Every supervisor that needs to engage a
developer or load a stack-specific skill consults this table.

| Stack language | Frameworks (sub-flavours) | Developer agent | Skills loaded |
|---|---|---|---|
| python | streamlit, fastapi, django, flask | `developer-python` | `python-expert`; `streamlit-expert` if framework=streamlit |
| java | spring-boot (default), micronaut, quarkus, helidon, java-se | `developer-java` | `java-spring-standards`, `spring-expert`, `spring-architecture`, `spring-data-jpa`, `java-expert` (Spring skills loaded only when stack.frameworks contains spring-boot) |
| kotlin | spring-boot, ktor, android | `developer-kotlin` | `java-spring-standards`, `spring-architecture`, `spring-data-jpa`, `java-expert` (Kotlin reuses Spring skills + adds Kotlin idioms in the agent itself) |
| go | gin, chi, fiber, std | `developer-go` | (none yet — `go-standards` skill is roadmap) |
| rust | axum, actix-web, rocket, tokio | `developer-rust` | (none yet — `rust-standards` skill is roadmap) |
| csharp | aspnet-core, blazor | `developer-csharp` | `rest-api-standards`, `testing-standards` |
| ruby | rails, sinatra, hanami | `developer-ruby` | `rest-api-standards`, `testing-standards` |
| php | laravel, symfony | `developer-php` | `rest-api-standards`, `testing-standards` |
| typescript / javascript (frontend) | angular, react, nextjs, tanstack-start, vue, qwik, vanilla | `developer-frontend` | per framework: `angular-expert`+`ngrx-expert`+`rxjs-expert` / `react-expert`+`tanstack-query` / `vue-expert` / `qwik-expert` / `vanilla-expert` / `nextjs` / `tanstack-start`; always `css-expert`+`design-expert` |

Sub-agents in the analysis pipelines use the same mapping in the
opposite direction: `state-runtime-analyst` invokes `streamlit-expert`
when `stack.frameworks` contains `streamlit`, `python-expert` always
when `stack.primary_language=python`, etc.

The dispatch table lives at
`claude-catalog/docs/language-agnostic-design.md` (this file) and is
referenced by every supervisor's prompt under a `## Dispatch` section.
The table itself is **not** duplicated across agents — they all link
back here. (TODO in implementation: optionally extract to a JSON/YAML
file for machine-readable consumption.)

---

## TO-BE handling

Phase 4 cannot auto-detect TO-BE — there is no codebase yet. The
target stack is a decision, not a discovery. The flow is:

1. `decomposition-architect` (W1) is invoked by
   `refactoring-tobe-supervisor`. The supervisor passes the AS-IS
   stack info from `_meta/manifest.json`.
2. `decomposition-architect` produces ADR-002 (target stack), driven
   by either:
   - explicit user input: `refactoring-tobe-supervisor --target
     "java/spring-boot+angular"`
   - a `migration profile` argument: `--profile java-spring-angular`
     (a profile is a named bundle of language + framework choices —
     declared in `claude-catalog/docs/migration-profiles.md`,
     a follow-up artifact)
   - inference + explicit confirmation: e.g. for a Streamlit AS-IS the
     supervisor proposes `java/spring-boot + angular` (the historical
     default) and asks the user to confirm or override before writing
     the ADR.
3. ADR-002 declares: `target.language`, `target.frameworks[]`,
   `target.build_tools[]`, `target.test_frameworks[]`, with the same
   schema as the AS-IS stack block.
4. All subsequent W2-W6 sub-agents read ADR-002 to know what to
   generate. They do not have hardcoded "Java/Spring" assumptions —
   they engage the `developer-*` agent for `target.language` and the
   skills for `target.frameworks`.

Phase 5 detects the TO-BE stack by re-running `codebase-mapper-light`
on the generated TO-BE directories (`backend/`, `frontend/`). This
produces `manifest.tobe.json`. The Phase 5 supervisor then engages
the right test-writer sub-agents based on what was actually generated.

---

## What changes in each agent

### `refactoring-supervisor` (top-level)

**Today**: prompts mention "Python AS-IS → Java/Spring + Angular".
**Tomorrow**: prompts read `_meta/manifest.json` and ADR-002, render
the dispatch table, and pass the relevant developer agent + skill
names down to each phase supervisor in the dispatch prompt.

### Phase 0 — `indexing-supervisor` + `codebase-mapper`

**Today**: `streamlit-analyzer` is dispatched unconditionally;
prompts assume Python.
**Tomorrow**:
- `codebase-mapper` produces the `stack:` block as part of its output.
- `indexing-supervisor` reads `stack:` and conditionally dispatches
  framework-specific sub-agents. Today: `streamlit-analyzer` is
  dispatched only if `streamlit` ∈ `stack.frameworks`. Tomorrow: same
  pattern for any framework-specific analyzer added later (e.g. a
  hypothetical `rails-analyzer`).
- `business-logic-analyst`, `data-flow-analyst`, `module-documenter`
  remain language-agnostic (they read code, summarise structure —
  the language is metadata they receive, not a hardcoded assumption).

### Phase 1 — `functional-analysis-supervisor` + sub-agents

**Today**: "Streamlit-aware adjustments" block is hardcoded.
**Tomorrow**:
- The supervisor's "stack-aware adjustments" block is generic. It
  injects framework-specific guidance into sub-agent prompts based on
  `stack.frameworks`.
- Each sub-agent (e.g. `ui-surface-analyst`, `user-flow-analyst`)
  has framework-conditional sections (Streamlit page-as-screen,
  Rails view templates, Next.js routes, Angular components). Today
  these are absent or Streamlit-only; tomorrow they are skill-loaded.

### Phase 2 — `technical-analysis-supervisor` + sub-agents

Same pattern. Sub-agents like `state-runtime-analyst`,
`data-access-analyst`, `performance-analyst` learn to load the right
expert skill based on `stack.primary_language`.

### Phase 3 — `baseline-testing-supervisor` + sub-agents

**Today**: hardcoded for `pytest`.
**Tomorrow**: the supervisor reads `stack.test_frameworks` from the
manifest. If pytest, dispatches the current Python sub-agents. If
JUnit 5, dispatches Java equivalents. If `go test`, dispatches Go
equivalents. Etc. Each test-writer sub-agent specialises by language.

This phase needs **new sub-agents** for non-Python AS-IS:
- `usecase-test-writer-java` (or extend the existing one to be
  language-agnostic with a language argument)
- … per language

For the first iteration we accept a constraint: if AS-IS is not
Python, Phase 3 emits `status: not-implemented` and the migration
proceeds without the regression baseline (degraded mode flagged in
the manifest). Adding language-specific test writers is a follow-up.

### Phase 4 — `refactoring-tobe-supervisor` + sub-agents

**Today**: hardcoded "Java/Spring + Angular".
**Tomorrow**:
- Supervisor reads ADR-002 for target stack.
- Dispatches the right developer agent for backend (`developer-go`,
  `developer-rust`, etc.) and frontend (`developer-frontend` with
  framework hint).
- Sub-agents like `backend-scaffolder`, `data-mapper`,
  `logic-translator`, `frontend-scaffolder` become **dispatchers**
  rather than executors: they hand off to the appropriate
  `developer-*` agent with detailed instructions. Or they get
  language-specific siblings (`backend-scaffolder-go`,
  `backend-scaffolder-csharp`, …).

The "dispatcher" approach is cleaner — fewer files. But it requires
each `developer-*` agent to know how to scaffold a project from
scratch given a bounded-context decomposition. We choose dispatcher.

For the first iteration we accept the same constraint as Phase 3:
target language has a developer agent or Phase 4 emits
`status: not-implemented` for that target. The 9 currently-shipping
developer agents cover the common cases.

### Phase 5 — `tobe-testing-supervisor` + sub-agents

**Today**: hardcoded JUnit 5 + Mockito + Testcontainers + Spring
Cloud Contract + Angular Testing Library + Playwright + pytest.
**Tomorrow**:
- Re-run codebase detection on the TO-BE codebase to get the actual
  stack (since the user might have chosen Go, Rust, etc.).
- Dispatch the right test-writer per language.

Same first-iteration constraint as Phase 3.

---

## Migration plan (one PR per phase)

The full refactor lands across multiple PRs to keep each reviewable.
Order matters because later phases consume earlier ones'
`_meta/manifest.json`.

| PR | Branch | Scope |
|---|---|---|
| **PR-01** (this) | `refactor/language-agnostic-supervisors` | Move developers to subfolder; write this design doc; CHANGELOG entry. **No logic changes.** |
| **PR-02** | `refactor/phase0-stack-detection` | Extend `codebase-mapper` with `stack:` block emission; conditional dispatch in `indexing-supervisor`; Streamlit-only assumption removed. |
| **PR-03** | `refactor/phase1-stack-aware` | `functional-analysis-supervisor` + sub-agents read stack from manifest; framework-conditional adjustments. |
| **PR-04** | `refactor/phase2-stack-aware` | Same for Phase 2. |
| **PR-05** | `refactor/phase3-multi-language-tests` | `baseline-testing-supervisor`: read `stack.test_frameworks`, dispatch language-specific writers; or emit `not-implemented` for non-Python in v0.1 of the agnostic pipeline. |
| **PR-06** | `refactor/phase4-target-stack-from-adr` | `refactoring-tobe-supervisor`: read target from ADR-002; dispatch developer agents via dispatch table; sub-agents become dispatchers. |
| **PR-07** | `refactor/phase5-tobe-detection` | `tobe-testing-supervisor`: re-detect on TO-BE codebase; dispatch language-specific test writers. |
| **PR-08** | `refactor/top-level-supervisor` | `refactoring-supervisor`: drop hardcoded language references; rely on dispatch table. |
| **PR-09** | `refactor/cleanup` | Remove dead language-specific blocks; final CHANGELOG; tier promotion review. |

PR-02 to PR-08 are roughly equal-effort; PR-01 is the smallest. Each
ships a working pipeline (worst case: degraded mode flagged in the
manifest for unsupported languages in Phase 3 / 4 / 5).

---

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Detection mis-identifies stack on polyglot repos | Always emit `confidence` + `evidence`; supervisor surfaces low-confidence detections to user before proceeding. |
| Refactor breaks the existing Python → Java/Spring + Angular pipeline | Land changes phase-by-phase; smoke-test each PR by running the pipeline against a known reference repo. |
| Adding a new language requires changes in many files | The dispatch table localises this to one place; adding a language = adding one row in this doc + one developer agent + (optionally) a few skills. |
| Sub-agents accumulate framework-conditional branches | Push framework knowledge into skills; sub-agents conditionally invoke skills based on detected stack. |
| TO-BE stack disagreement between user and ADR-002 | The supervisor's HITL checkpoint after `decomposition-architect` lets the user veto/edit ADR-002 before proceeding. |
| `not-implemented` status for non-Python AS-IS in Phases 3/4/5 in v1 | Documented limitation; addressed in follow-up PRs adding language-specific sub-agents. |

---

## Out of scope

- Auto-detection of *target* stack (Phase 4 input).
- Cross-language migration skills beyond what already exists (`python-to-java`, `python-to-react`, `python-to-angular`).
- Migration profiles (`migration-profiles.md`) — proposed in this doc but deferred to a follow-up.
- Removing the Italian/English language mix in agent prompts (separate concern).

---

## Open questions

1. **Generic developer-java vs. developer-java-spring**? ✅ **Decided
   in PR-01**: renamed `developer-java-spring` → `developer-java`
   (MAJOR bump 1.0.0 → 2.0.0). Spring Boot remains the default
   framework; Micronaut/Quarkus/Helidon/Java SE are handled with
   explicit user guidance. Future siblings (`developer-java-micronaut`,
   `developer-java-quarkus`) can specialise per framework when there
   is enough demand.

2. **Frontend framework detection granularity**? `developer-frontend`
   handles Angular/React/Vue/Qwik/Vanilla via skills. Should the
   detection emit `frameworks: [angular]` or
   `frontend_framework: angular`? The schema above says `frameworks[]`
   — confirm this is right.
   - **Tentative answer**: yes, `frameworks[]` is right; multiple
     framework markers are possible (e.g. Next.js + TanStack Query).

3. **Where do migration profiles live**? A YAML file in
   `claude-catalog/docs/migration-profiles.yaml` referenced from this
   doc? Or a skill?
   - **Tentative answer**: YAML file for now; promote to skill if
     consumed by ≥ 2 supervisors.

4. **Does each `developer-*` agent need to ship a "scaffold a fresh
   project" capability**? ✅ **Decided in PR-01**: yes. Each
   `developer-*` agent's "Project structure" section will be extended
   to be **executable** — provide commands and templates the agent
   uses to bootstrap a project from scratch given a bounded-context
   decomposition. This is needed for Phase 4's dispatcher pattern
   (sub-agents like `backend-scaffolder` hand off to the appropriate
   `developer-*` agent). Tracked under PR-06; no change in PR-01.

5. **Migration profiles location**? ✅ **Decided in PR-01**: deferred.
   A YAML file at `claude-catalog/docs/migration-profiles.yaml` is
   the proposed home, but it is not added until at least one
   supervisor consumes it. Tracked under the PR that first introduces
   profile consumption (likely PR-06).

6. **Frontend framework granularity**? ✅ **Decided in PR-01**:
   `frameworks[]` (array). Multiple framework markers are possible
   (e.g. Next.js + TanStack Query), so the schema must accommodate
   them. Single-framework projects emit a one-element array.

These are recorded for resolution during the relevant downstream PR.

---

## Acceptance criteria for the full refactor

The refactor is complete when:

- [ ] No supervisor's system prompt contains `python`, `streamlit`,
  `java`, `spring`, `angular`, `jpa`, `pytest`, `junit`, `maven`,
  `npm`, `gradle`, `cargo` outside of (a) the dispatch table and (b)
  citations of skills/agents that legitimately mention them.
- [ ] Phase 0 emits `stack:` in `_meta/manifest.json` with high
  confidence on the reference Streamlit project today.
- [ ] Phases 1-3 read the manifest and adapt without re-detection.
- [ ] Phase 4 reads ADR-002 and supports at least Java/Spring + Angular
  (regression) AND one non-Java target (proof of agnosticism — Go is
  the easiest test).
- [ ] Phase 5 re-detects on TO-BE and adapts.
- [ ] The reference Python → Java/Spring + Angular pipeline still
  produces the same output it produces today (smoke test).
- [ ] Adding a 10th language requires touching: 1 row in the dispatch
  table; 1 new `developer-X` agent; optionally skills. Nothing else.

---

## References

- Current `refactoring-supervisor` and phase supervisors:
  `claude-catalog/agents/refactoring-supervisor.md`,
  `claude-catalog/agents/{indexing,functional-analysis,technical-analysis,baseline-testing,refactoring-tobe,tobe-testing}/`
- Developer agents (now under `developers/`):
  `claude-catalog/agents/developers/`
- Existing Streamlit-aware blocks (to be migrated):
  grep `streamlit` in `claude-catalog/agents/` for the current list.
- 2026-04-28 File-writing rule (carried over to all touched agents):
  see `claude-catalog/CHANGELOG.md`.
