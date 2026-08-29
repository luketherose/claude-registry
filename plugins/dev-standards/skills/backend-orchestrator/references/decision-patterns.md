# Decision patterns

## Contents

- 3. Orchestration order
- New feature (TYPE A) — top-down
- Bug / problem (TYPE B) — bottom-up
- Optimisation (TYPE C) — diagnose first, fix later
- Refactoring (TYPE D) — architecture guides everything
- Parallel execution
- Independence criterion
- Phase model
- Domain-specific parallelization rules
- When NOT to parallelize
- 5. Decision patterns
- DTO vs Entity
- Custom query vs standard repository
- Optimise at DB level vs application level
- Introducing caching

## 3. Orchestration order

### New feature (TYPE A) — top-down

```
1. /backend/spring-architecture   → define layer structure and contracts (DTO, interfaces)
2. /database/postgresql-expert    → schema, tables, indices, constraints, migration DDL
3. /backend/spring-data-jpa       → entity mapping, relationships, fetch strategy, repository
4. /backend/java-expert           → Java logic in the service (if complex)
5. /backend/spring-expert         → configuration, security, WebClient if necessary
```

**Why this order**: the structure and public contract (DTO, interfaces) must be defined before implementation. The DB schema must exist before entity mapping. The entity must exist before the service. Reversing the order causes cascading refactoring.

### Bug / problem (TYPE B) — bottom-up

```
1. /database/postgresql-expert    → does the query reach the DB? Is the data correct? Are indices used?
2. /backend/spring-data-jpa       → does the ORM generate the expected query? Is the transaction correct?
3. /backend/java-expert / /backend/spring-expert → is the application logic correct?
4. /backend/spring-architecture   → is the problem structural (wrong layer)?
```

**Why bottom-up**: most backend bugs have their root cause in the lowest layer. Starting from the top wastes time.

### Optimisation (TYPE C) — diagnose first, fix later

```
1. /database/postgresql-expert    → EXPLAIN ANALYZE, missing indices, query anti-patterns
2. /backend/spring-data-jpa       → N+1, fetch strategy, bulk operations, projections
3. /backend/java-expert           → concurrency, inefficient streams, unnecessary objects
   → DO NOT optimise at code level if the problem is in the DB
```

### Refactoring (TYPE D) — architecture guides everything

```
1. /backend/spring-architecture   → define the target structure
2. All involved skills             → adapt each layer to the target structure
   → Maintain unchanged functional behaviour during refactoring
```

---

## Parallel execution

### Independence criterion
Two tasks are parallelizable when:
- They do not write to the same files
- Neither depends on the other's output
- They operate on distinct system layers or surfaces

### Phase model
Map every multi-skill task into phases before executing:
```
Phase 1 — Sequential anchor    (shared contracts, interfaces, schemas)
Phase 2 — Parallel fan-out     (independent implementation workers)
Phase 3 — Sequential merge     (integration, consistency checks, tests)
```

### Domain-specific parallelization rules

```
Parallelizable pairs (no shared state):
  - postgresql-expert (DDL) ∥ java-expert (pure domain logic with no DB calls)
  - spring-expert (config/security) ∥ test-writer (unit tests for already-defined interfaces)

Always sequential (output dependency):
  spring-architecture → spring-data-jpa (entity needs defined contracts)
  postgresql-expert → spring-data-jpa (entity mapping needs final schema)
  spring-data-jpa → spring-expert (service needs repository interface)
```

### When NOT to parallelize
- Tasks share mutable output files (same component, same table, same service)
- Task B's input is Task A's output
- Only 1-2 tasks total (coordination overhead exceeds benefit)

---

## 5. Decision patterns

### DTO vs Entity

```
Use Entity when:
  - Inside the repository/service layer and the data has not yet been serialised
  - Updating JPA state (dirty checking)

Use DTO when:
  - Leaving the service (towards the controller)
  - Entering the service (from the controller)
  - At the public interface of a service
  - Serialising towards an external API

Never pass an Entity beyond the service→controller boundary.
```

### Custom query vs standard repository

```
Use Spring Data derived query when:
  - Single or double condition on indexed columns
  - No join, no aggregate

Use JPQL when:
  - JOIN between entities, complex conditions, ORDER BY with logic
  - The query is understandable without reading the DB

Use native query when:
  - PostgreSQL-specific features: ANY, JSONB, full-text, window functions
  - Critical performance on queries with many rows (EXPLAIN has confirmed the problem)

Use Projection when:
  - Returning a subset of columns from a large entity is required
  - The query is read-only and the full entity is not needed for dirty checking
```

### Optimise at DB level vs application level

```
Optimise at DB level first if:
  - EXPLAIN ANALYZE shows Seq Scan on a table > 10k rows
  - The problem is the number of queries (N+1)
  - The query takes > 100ms in staging

Optimise at application level after the DB is optimised:
  - Reduction of objects allocated in loops
  - CompletableFuture parallelism for independent I/O calls
  - Lazy streams instead of materialised collections

Do not optimise prematurely: profile first, optimise later.
```

### Introducing caching

```
L1 caching (Hibernate first-level): automatic per session — do not configure
L2 caching (Hibernate second-level): for stable lookup entities (< 1 write/hour)
Application caching (Spring Cache): for results of complex queries that:
  - Do not change frequently (TTL > 5 minutes)
  - Are expensive (> 200ms)
  - Have stable identity (same input → same output)

Do not cache:
  - Transactional data (accounts, balances, process states)
  - Data with per-user access logic (without a per-user key)
  - As a workaround for poorly optimised queries — fix the DB first
```

---
