# Phase 4 — Output layout & frontmatter contract

> Reference doc for `refactoring-tobe-supervisor`. Read at runtime when planning where workers write their outputs and what frontmatter / header comments every artefact must carry.

## Output roots

Two roots: `<repo>/.refactoring-kb/` (TO-BE knowledge base — distinct from `.indexing-kb/` which holds AS-IS) and `<repo>/docs/refactoring/` (stakeholder docs and ADRs). Plus the actual codebase under `backend/` and `frontend/` (paths configurable).

```
.refactoring-kb/                                ← TO-BE KB (NEVER mix with .indexing-kb/)
├── 00-decomposition/
│   ├── bounded-contexts.md
│   ├── module-decomposition.md                 (AS-IS module → TO-BE BC mapping)
│   └── aggregate-design.md
├── 01-api/
│   └── openapi.yaml                            (canonical link)
├── 02-traceability/
│   └── as-is-to-be-matrix.json                 (UC-NN → endpoint → service → component)
├── 03-decisions/
│   └── decision-log.md                         (running log of decisions made)
└── _meta/
    ├── manifest.json                           (timing per worker)
    └── unresolved-tobe.md

docs/refactoring/
├── README.md                                   (you — index)
├── 00-context.md                               (you — system summary, mode)
├── 4.1-decomposition/                          (decomposition-architect)
├── 4.6-api/                                    (api-contract-designer)
│   ├── openapi.yaml
│   ├── design-rationale.md
│   └── postman-tobe.json
├── 4.7-hardening/                              (hardening-architect)
├── roadmap.md                                  (migration-roadmap-builder)
├── _exports/                                   (opt-in)
│   ├── roadmap.pdf
│   └── steering-deck.pptx
└── _meta/
    ├── manifest.json
    └── challenger-report.md

docs/adr/                                       (cumulative)
├── ADR-001-architecture-style.md               (decomposition-architect)
├── ADR-002-target-stack.md                     (decomposition-architect)
├── ADR-003-auth-flow.md                        (api-contract-designer)
├── ADR-004-observability.md                    (hardening-architect)
└── ADR-005-security-baseline.md                (hardening-architect)

backend/                                        (Spring Boot 3 — Maven)
├── pom.xml
├── src/main/java/<base-pkg>/
│   ├── <bc-1>/                                 (one package per bounded context)
│   │   ├── api/                                (controller + DTO)
│   │   ├── application/                        (service)
│   │   ├── domain/                             (entity + value objects)
│   │   └── infrastructure/                     (repository + mapper)
│   ├── <bc-2>/
│   └── shared/                                 (cross-cutting: error, security, telemetry)
├── src/main/resources/
│   ├── application.yml
│   └── db/changelog/                           (Liquibase YAML)
└── src/test/java/                              (unit-test scaffold; Phase 5 fills it)

frontend/                                       (Angular workspace)
├── angular.json
├── package.json
├── src/app/
│   ├── core/                                   (interceptors, guards, services)
│   ├── shared/                                 (components, pipes, models)
│   └── features/                               (one lazy module per BC)
└── src/environments/
```

Workers must not write outside these roots. Verify after each dispatch.

## Frontmatter contract (markdown)

Every markdown under `docs/refactoring/` and `.refactoring-kb/` has YAML frontmatter:

```yaml
---
agent: <worker-name>
generated: <ISO-8601>
sources:
  - .indexing-kb/<path>
  - docs/analysis/01-functional/<path>
  - docs/analysis/02-technical/<path>
  - tests/baseline/<path>
  - docs/analysis/03-baseline/<path>
related_ucs: [UC-NN, ...]                      # mandatory for traceability
related_bcs: [<bounded-context-id>, ...]       # mandatory for traceability
confidence: high | medium | low
status: complete | partial | needs-review | blocked
duration_seconds: <int>
---
```

## Header-comment contract (Java / TypeScript)

Java and TypeScript files don't carry YAML, but each generated source file MUST include a header comment with:
- the UC-NN(s) it implements (or "scaffold" / "infrastructure")
- the AS-IS source reference (`<repo>/<path>:<line>` of the original Python module being translated)
- a `// TODO(BC-NN, UC-NN): translate from <as-is-path>` for unfilled business logic (per the `scaffold-todo` scope)
- the bounded context the file belongs to
