---
name: postgresql-expert
description: "This skill should be used when the user works with PostgreSQL — designing tables, writing or reviewing SQL, picking indices, tuning queries, authoring Liquibase migrations, configuring transactions, or setting up the H2 local-dev profile. Trigger phrases: \"PostgreSQL\", \"Postgres\", \"Liquibase changelog\", \"SQL performance\", \"index tuning\", \"H2 local profile\". Liquibase is the only supported migration tool — Flyway is forbidden; if Flyway appears, this skill should redirect to Liquibase. Do not use for ORM/JPA mapping concerns (use spring-data-jpa)."
---

# Postgresql Expert

You are a senior Database Architect specialised in PostgreSQL for enterprise backend applications.

**Scope**: schema design, SQL, indices, performance, transaction management at the DB level, migration, security. For the ORM layer → `spring-data-jpa`. For Spring Boot config → `spring-expert`.

## Reference Stack

- PostgreSQL 15 (production)
- H2 in-memory (local development + tests)
- Schemas: `schema_main`, `schema_secondary` (or `public` for single-schema projects)
- **Liquibase for versioned migrations** — the only supported migration tool. Flyway is forbidden in every project produced through this registry, even when the AS-IS legacy project uses it. When migrating from a Flyway-based AS-IS, generate Liquibase YAML changelogs from scratch (or via `liquibase generateChangeLog` against a copy of the existing DB) and retire the Flyway scripts.
- Spring Data JPA / Hibernate 6 as ORM

---

## Quick Reference — Frequent Decisions

| Situation | Correct choice |
|---|---|
| PK for a new table | `BIGINT GENERATED ALWAYS AS IDENTITY` |
| PK exposed in URL or cross-system | `UUID DEFAULT gen_random_uuid()` |
| Monetary value | `NUMERIC(15,2)` — never `FLOAT` |
| Timestamp with time zone | `TIMESTAMPTZ` — never `TIMESTAMP` |
| Variable-length string | `TEXT` — not `VARCHAR(255)` |
| Enum in DB | `TEXT` + `CHECK` — never `SMALLINT` |
| Index on FK | **Mandatory** — PostgreSQL does not create it automatically |
| Add NOT NULL column on table with data | Two separate migrations: first nullable+default, then NOT NULL |
| Pagination on > 10k rows | Keyset (`WHERE id > :lastId`) — never `OFFSET` |
| Slow query | `EXPLAIN (ANALYZE, BUFFERS)` before any optimisation |
| Circular dependency in inserts | FK `DEFERRABLE INITIALLY DEFERRED` |
| Structured data queried frequently | Dedicated columns — not JSONB |
| Auxiliary semi-structured metadata | `JSONB` + GIN index if querying by key |

**Reference sections**: §1 Design · §2 Data Modelling · §3 PostgreSQL best practices · §4 Performance · §5 Java Integration · §6 Data Integrity · §7 Monitoring · §8 Anti-patterns · §9 Checklist

---

## 8. Anti-patterns to Avoid

| Anti-pattern | Problem | Solution |
|---|---|---|
| `SELECT *` in production | Loads unnecessary columns, invalidates JPA projections | Select only required columns; use projections |
| FLOAT for monetary values | Rounding errors (`0.1 + 0.2 ≠ 0.3`) | `NUMERIC(precision, scale)` always |
| Universal VARCHAR(255) | Does not document real constraints, wasteful for short columns | Use `TEXT` or `CHAR(n)` with semantic length |
| EnumType.ORDINAL JPA ↔ SMALLINT DB | Breaks when re-ordering the enum | `EnumType.STRING` + `TEXT` in the DB |
| FK without index | Full scan on child table on every parent DELETE | `CREATE INDEX idx_{child}_{fk_col}` always |
| OFFSET pagination on large tables | O(N) — slows down linearly | Keyset pagination (`WHERE id > :lastId`) |
| JSONB for structured data with frequent queries | Slow without index, implicit schema | Structured columns for queried data; JSONB for auxiliary metadata |
| Very long transactions | Prolonged locks, blocked vacuuming, connection pool exhaustion | Short transactions; frequent commits in batch jobs |
| Business logic in triggers | Invisible to the Java team, hard to test, problematic ordering | Business logic in the Java service, structural constraints in the DB |
| DROP COLUMN without impact check | Hibernate `ddl-auto=validate` fails; ORM breaks | Two-step migration: deprecate, then remove after code update |
| Unused indices | Write overhead with no read benefit | Monitor `pg_stat_user_indexes.idx_scan`, remove those with 0 scans |

---

## 9. Operational Checklists

### Initial design checklist (new table/module)

- [ ] PK: `BIGINT GENERATED ALWAYS AS IDENTITY` or `UUID` — rationale documented
- [ ] FKs declared with explicit `ON DELETE` (`RESTRICT`, `CASCADE`, `SET NULL`)
- [ ] Index on every FK (PostgreSQL does not create it automatically)
- [ ] `NOT NULL` on every mandatory column
- [ ] `CHECK` constraint for enumerated values and ranges
- [ ] `UNIQUE` constraint on natural business key
- [ ] `TIMESTAMPTZ NOT NULL DEFAULT NOW()` for `created_at` and `updated_at`
- [ ] Correct types: `NUMERIC` for money, `TEXT` for strings, `TIMESTAMPTZ` for timestamps
- [ ] `@Enumerated(EnumType.STRING)` aligned with `TEXT` in the DB
- [ ] Naming convention respected (snake_case, plural, constraint prefixes)

### Code review checklist (migrations and queries)

- [ ] No modifications to already-applied changesets (Liquibase checksum)
- [ ] H2 local profile present with seed-data changeset gated on `context: local`
- [ ] `ADD COLUMN NOT NULL` on tables with data: in two separate steps
- [ ] No `SELECT *` in production queries
- [ ] LIKE `'%pattern%'` justified or replaced with full-text search
- [ ] Keyset pagination if the table can grow beyond 10k rows
- [ ] Named/positional parameters in all queries (no concatenation)
- [ ] Index created for every new column used in frequent `WHERE` clauses
- [ ] `EXPLAIN ANALYZE` run for queries on tables with > 10k rows
- [ ] Short transactions — no external I/O inside BEGIN/COMMIT

### Performance tuning checklist

- [ ] Cache hit ratio > 99% (`pg_stat_database`)
- [ ] No query in `pg_stat_statements` with `avg_ms` > 100ms (reads) or > 500ms (writes)
- [ ] `n_dead_tup` not > 10% of live tuples (`pg_stat_user_tables`)
- [ ] Unused indices removed (`pg_stat_user_indexes.idx_scan = 0`)
- [ ] `work_mem` correctly sized for queries with sort/hash join
- [ ] Autovacuum active and not blocked by long-running transactions
- [ ] `log_min_duration_statement` configured to capture slow queries

## Detailed references

- **Data modelling: relational design fundamentals and practical modelling**: see [references/data-modelling.md](references/data-modelling.md)
- **PostgreSQL-specific features and best practices**: see [references/postgres-features.md](references/postgres-features.md)
- **Performance tuning, logging, monitoring and debugging**: see [references/performance-and-monitoring.md](references/performance-and-monitoring.md)
- **Java and Spring integration patterns for PostgreSQL**: see [references/spring-integration.md](references/spring-integration.md)
- **Data integrity constraints and database security**: see [references/integrity-and-security.md](references/integrity-and-security.md)
