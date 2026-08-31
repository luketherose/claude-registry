---
name: backend-orchestrator
description: "ALWAYS use this skill when a backend task spans more than one Java/Spring layer: the user asks to add a new endpoint end-to-end, design a module from Controller to DB, refactor an existing feature across Service/Repository/Entity, or resolve cross-layer inconsistencies. Trigger phrases: \"add a new endpoint end-to-end\", \"wire a service\", \"from controller to database\", \"full backend feature\", \"design this module Controller to DB\". Coordinates java-expert, spring-expert, spring-data-jpa, spring-architecture, postgresql-expert, and guarantees cross-layer consistency. Do not use for single-layer tasks (use the targeted skill directly)."
---

# Backend Orchestrator

Act as the decision-making layer for backend work. Write no code directly. Decide which skills to activate, in which order and under which constraints, and guarantee architectural consistency between layers.

## Available skills

| Skill | Scope | Use when |
|---|---|---|
| `java-expert` | Core Java 17+, Lombok, exceptions, concurrency, POI/iText | Pure Java logic, document generation, idiomatic patterns |
| `spring-expert` | IoC/DI, Spring Boot, Security JWT, WebClient, testing | Spring configuration, endpoint security, external API calls |
| `spring-data-jpa` | Entities, relationships, N+1, transactions, JPQL | ORM mapping, fetch strategy, custom queries, transaction boundaries |
| `spring-architecture` | Layer design, DTO, mapper, error handling, naming | New module structure, separation of concerns, naming review |
| `postgresql-expert` | Schema design, indices, SQL performance, Liquibase migrations | DDL, query optimisation, index tuning, DB constraints |

---

## Context sources (decreasing priority)

Before activating any backend skill, query sources in this order:

| Priority | Source | When to use it |
|---|---|---|
| 1 | **Real code** | Absolute source of truth, always |
| 2 | **Pre-existing analyses** | Quickly understand what a module does without reading all the code, if available in the project |
| 3 | **Dependency graph / architectural artefacts** | Dependencies, migration targets, architectural impacts, if available |
| 4 | **Functional documentation** | Business rules, user flows, use cases |
| 5 | **Technical analysis** | Module map, bounded context, complexity |
| 6 | **Inferences** | Only if previous sources do not cover the case |

### When to consult pre-existing analysis artefacts

**Use analysis artefacts when:**
- Implementing a Service that replicates legacy logic: read the source code or the corresponding pre-indexed chunks
- Deciding the public interface of a service: the inputs/outputs of available artefacts tell what goes in and what comes out
- Understanding the dependencies of a module without reading all the code
- Validating whether a JPA entity is complete with respect to the business logic

**How to navigate them:**
1. Identify the relevant bounded context (the project's bounded contexts)
2. Go to the corresponding artefacts available in the project (functional analysis, technical analysis, semantic chunks)
3. Filter by type, layer or tag to find the exact artefact
4. Extract the business rules: those belong in the Java Service, not in the Controller

**Do not use analysis artefacts when:**
- The task concerns completely new code (no artefacts available)
- An artefact is marked as unstable or out of date: verify against the real code

### Conflicts between sources

- **Real code always wins** over any analysis artefact
- Detailed analyses beat architectural ones for implementation details and business rules
- Architectural artefacts beat detailed ones for relationships and migration targets
- If analysis and code contradict each other, the code is more recent: update the artefacts if significant

---

## 1. Intent Recognition: request classification

Before activating any skill, classify the request into one of the categories:

```
TYPE A: New feature
  → Requires: architecture → DB → entity/JPA → service → controller

TYPE B: Bug / behavioural problem
  → Requires: layer-by-layer diagnosis (bottom-up: DB → repository → service → controller)

TYPE C: Performance optimisation
  → Requires: DB diagnosis first, then ORM, then application code

TYPE D: Refactoring / redesign
  → Requires: architecture → then all involved skills

TYPE E: Atomic single-layer task
  → Requires: single skill (do not orchestrate unless necessary)
```

**Anti-over-engineering rule**: if the request involves only one layer (e.g. "add a column to an existing query"), activate a single skill. Orchestration is justified only when decisions in one layer impact another.

---

## 2. Skill Selection Strategy: decision rules

### Request → skill mapping

| Request | Primary skill | Secondary skills |
|---|---|---|
| New REST endpoint | `spring-architecture` | `spring-expert`, `java-expert` |
| Entity + JPA mapping | `spring-data-jpa` | `postgresql-expert` |
| Slow query / N+1 | `postgresql-expert` | `spring-data-jpa` |
| Complex transaction | `spring-data-jpa` | `spring-expert`, `postgresql-expert` |
| Complete new module | `spring-architecture` | all backend skills |
| External API call | `spring-expert` | `java-expert` |
| Complex business logic | `java-expert` | `spring-architecture` |
| DB schema design | `postgresql-expert` | `spring-data-jpa` |
| Security / JWT | `spring-expert` | `spring-architecture` |
| Liquibase migration | `postgresql-expert` | `spring-data-jpa` |
| Exception handling | `spring-architecture` | `java-expert` |
| PDF/Excel generation | `java-expert` | n/a |

### Exclusion rule

Do not activate a skill if:
- Its domain is not touched by the request
- Another skill already covers the overlap point (e.g.: `spring-architecture` covers controller error handling, so `spring-expert` is not also needed for that)
- The request is already resolved by the primary skill without cross-layer ambiguity

---

## 4. Priority rules (conflict resolution)

When two skills suggest different approaches, the priority is:

```
1. Data integrity (DB):          a failing DB constraint is non-negotiable
2. Architectural correctness:    respect layer separation
3. Performance:                  optimise only after the design is correct
4. Clean code / idiomaticity:    refactoring only if it does not introduce risks
```

**Conflict example**: the JPA skill suggests `FetchType.EAGER` for simplicity, the DB skill flags an explosive query. **DB wins**: use explicit `JOIN FETCH` in the repository instead.

**Conflict example**: the Java skill suggests logic in the service, the architecture skill suggests extracting it to a helper. **Architecture wins** if the logic is reusable across modules; **service wins** if it is specific to that case.

---

## 6. Cross-layer consistency: mandatory invariants

These rules must be respected in every orchestrated output:

```
[DB]      → Every FK has an explicit index
[DB]      → Structural constraints declared in DDL (NOT NULL, UNIQUE, CHECK)
[DB]      → Correct types: NUMERIC for money, TIMESTAMPTZ for timestamps, TEXT for strings

[JPA]     → @NoArgsConstructor on every entity
[JPA]     → @EqualsAndHashCode(of="id"), never relationships in equals/hashCode
[JPA]     → FetchType.LAZY on OneToMany, override with JOIN FETCH where necessary
[JPA]     → @Transactional(readOnly=true) default in service, override for writes
[JPA]     → @Enumerated(EnumType.STRING) aligned to TEXT in the DB

[SERVICE] → Public interface + separate implementation
[SERVICE] → No entity returned beyond the service→controller boundary
[SERVICE] → Business validations in the service, not in the controller
[SERVICE] → Exception hierarchy: AppException → specialisations (use the project name)

[CTRL]    → @Valid on all @RequestBody
[CTRL]    → No business logic
[CTRL]    → GlobalExceptionHandler for all errors, no try/catch in the controller
[CTRL]    → ResponseEntity with semantically correct status code (201 for create, 204 for delete)

[JAVA]    → Constructor injection everywhere
[JAVA]    → Logging with {} placeholders, not concatenation
[JAVA]    → Records for immutable DTOs, classes for objects with behaviour
```

---

## 7. Output Strategy: response structure

Every orchestrated response must be structured by layer, in dependency order:

```
### Schema / Migration (if DB is involved)
  DDL, indices, Liquibase YAML changelog

### Entity / Repository
  JPA entity, relationships, custom queries

### DTO (request + response)
  Java records with validations

### Mapper
  Entity ↔ DTO conversion

### Service (interface + implementation)
  Business logic, transactions

### Controller
  REST endpoints, HTTP status codes

### Explanation of architectural choices
  Trade-offs, alternatives considered, constraints
```

Not all layers need to be included in every response: include only those impacted by the request. But if a layer is impacted, do not omit it for brevity.

---

## 8. Operating modes

### Design Mode
**Activate when**: new feature request, redesign, question "how do we structure X"
**Focus**: public contracts, separation of concerns, DB schema
**Output**: layer structure + DDL + service interfaces + DTO, without complete implementation
**Primary skill**: `spring-architecture` + `postgresql-expert`

### Implementation Mode
**Activate when**: structure already decided, concrete code is needed
**Focus**: complete and working code, all layers
**Output**: compilable code for each layer, in dependency order
**Primary skill**: all skills appropriate for the involved layers

### Debug Mode
**Activate when**: unexpected behaviour, exception, incorrect result
**Focus**: systematic bottom-up diagnosis
**Output**: root cause identified + minimal fix + explanation
**Primary skill**: bottom-up based on the suspected layer

### Optimisation Mode
**Activate when**: slow query, timeout, memory pressure, insufficient throughput
**Focus**: measure first, optimise later (not assumption-driven)
**Output**: EXPLAIN ANALYZE if DB, fetch strategy if ORM, profiling if Java
**Primary skill**: `postgresql-expert` → `spring-data-jpa` → `java-expert`

---

## 10. Orchestration anti-patterns

| Anti-pattern | Symptom | Correction |
|---|---|---|
| Activating all skills for every request | Verbose response, duplications, confusion | Activate only skills with direct responsibility for the request |
| Ignoring the DB in JPA decisions | Poorly mapped entity, missing indices, constraints only in Java | `postgresql-expert` always paired with `spring-data-jpa` |
| Optimising before diagnosing | Cache added before EXPLAIN ANALYZE | Measure → identify cause → minimal fix |
| Business logic in the controller | Controller with if/for, domain validations, direct repository access | Move to the service: the controller manages only HTTP |
| Emergent design (no architectural phase) | Inconsistent layers discovered late | Always `spring-architecture` before implementing |
| Feature flags and backward compat not requested | Dead code, accidental complexity | Change directly: compat is not needed unless explicitly requested |

---

## Acceptance Criteria for completed orchestration

**New feature (TYPE A) completed when:**
- [ ] DB schema with indices on FK and structural constraints
- [ ] JPA entity with `@NoArgsConstructor`, `@EqualsAndHashCode(of="id")`, `FetchType.LAZY`
- [ ] DTO (request validated with `@Valid`, response without JPA entity)
- [ ] GlobalExceptionHandler covers the new exceptions
- [ ] Controller: no business logic, semantically correct status code
- [ ] Tests: unit service (Mockito) + integration controller (`@WebMvcTest`)

**Bug (TYPE B) completed when:**
- [ ] Root cause identified with specific layer
- [ ] Minimal fix applied without changing the behaviour of other layers
- [ ] Regression documented if relevant

**Optimisation (TYPE C) completed when:**
- [ ] EXPLAIN ANALYZE run before and after the fix
- [ ] No cache introduced as a workaround for poorly structured queries
- [ ] Performance measured (avg_ms within target range)

---

## Orchestration checklist

**Before starting**:
- [ ] Request type classified (A/B/C/D/E)
- [ ] Necessary skills identified (only those with direct responsibility)
- [ ] Activation order defined

**During orchestration**:
- [ ] Cross-layer invariants respected (see section 6)
- [ ] Conflicts between skills resolved according to priorities (section 4)
- [ ] No business logic in the controller
- [ ] No entity exposed beyond the service→controller boundary
- [ ] DB and ORM aligned (types, enums, indices on FK)

**Final output**:
- [ ] All impacted layers included in the response
- [ ] Implementation order explicit (DB → Entity → DTO → Service → Controller)
- [ ] Key decisions and trade-offs explained
- [ ] No duplication between layers (DTO ≠ Entity ≠ DB schema, but aligned)

## Detailed references

- **Worked orchestration examples end to end**: see [references/orchestration-examples.md](references/orchestration-examples.md)
- **Orchestration order, parallel execution rules and decision patterns**: see [references/decision-patterns.md](references/decision-patterns.md)
