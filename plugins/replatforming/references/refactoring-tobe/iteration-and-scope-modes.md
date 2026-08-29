# Phase 4 — Iteration model, code-generation scope, verification & review policies

> Reference doc for `refactoring-tobe-supervisor`. Read at runtime when answering Q1 (iteration model), Q2 (code generation scope), Q3 (verification policy), or Q4 (code review policy).

## Q1 — Iteration model (default `A`)

Two valid models:

### Model A — One-shot (default)

Phase 4 produces the entire TO-BE in a single supervisor pass. All bounded contexts handled together. Faster, simpler. Risk: if the challenger finds problems late, the scope to fix is large.

### Model B — Per-bounded-context milestone

The supervisor iterates over bounded contexts identified in W1. For each BC: full backend (4.2/4.4/4.5) + frontend (4.3) + hardening for that BC. After all BCs done, single 4.7 (full hardening) and 4.8 (full roadmap).

Use Model B when:
- > 5 bounded contexts identified
- repo size > 30k Java LOC equivalent expected
- user explicitly requests strangler-fig deployment

Bootstrap presents the BC count and recommends a model. User confirms.

## Q2 — Code generation scope (default `scaffold-todo`)

Three modes:

### Mode `full` — Scaffold + data layer + COMPLETE business logic translation

Workers translate every UC into runnable Java code. Most ambitious. Token-heavy. Risk: incorrect translation that compiles but is semantically wrong.

### Mode `scaffold-todo` — DEFAULT

Workers produce:
- complete project scaffold (pom.xml, package structure, controllers, services, repositories, DTOs, mappers, error handlers, security config, Angular workspace + modules + components + services + guards)
- complete data layer (JPA entities, Liquibase YAML changelogs, repository signatures)
- complete API contract implementation (OpenAPI-generated controller signatures, DTO from schema)
- **TODO markers** for complex business logic — each TODO carries:
  - the UC-NN being implemented
  - the AS-IS source ref (`<repo>/<file>:<line>`)
  - a one-line summary of what to translate
  - a note on tests (the Phase 3 baseline test that should pass once translation is done)

This is the sweet spot: mechanical work done by agent; complex semantic translation reserved for human review with full context.

### Mode `structural` — Scaffold only

No translation, no data layer beyond entity skeletons. Just the project skeleton. For users who want Phase 4 as a "preparation" step and will do all coding manually.

## Q3 — Verification policy (default `auto`)

After W3 completes, the supervisor attempts to verify the scaffolds build. Adaptive:

```
1. Did the user pass --verify <X>? Use it.
2. Auto-detect:
   - mvn available? java >= 17?
   - node available? npm available? Angular CLI?
3. Decision:
   - all available -> verify ON
   - missing -> verify OFF (write-only); warn user
4. Verify execution (verify ON):
   - cd backend && mvn clean compile -DskipTests
     (compile only, not full build; faster + still catches structural
      errors)
   - cd frontend && npm install && npx ng build --configuration
     development
   - capture outputs to docs/refactoring/_meta/verify-output.txt
5. On failure:
   - escalate (don't silently proceed)
   - the user decides: fix-by-hand-and-resume, or revise the worker
     output, or accept partial (Phase 5 will catch it)
```

`mvn compile` is intentional (not `mvn package`): we want to verify the code is syntactically and structurally correct, not run tests (Phase 5 territory).

## Q4 — Code review policy (default `background`)

After each major output (decomposition, API contract, backend scaffold, frontend scaffold), the supervisor MAY dispatch `code-reviewer` in parallel without blocking the next wave. Findings accumulate in `docs/refactoring/_meta/code-review-findings.md` and surface in the final recap.

If `--review-mode sync`: review blocks the next wave. Slower but stricter.

If `--review-mode off`: skip entirely. Useful for quick exploratory runs.
