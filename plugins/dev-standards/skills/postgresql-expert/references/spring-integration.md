# Spring integration

## Contents

- 5. Java / Spring Integration
- JPA → PostgreSQL mapping — critical points
- Common ORM ↔ DB issues
- Liquibase — migration best practice

## 5. Java / Spring Integration

### JPA → PostgreSQL mapping — critical points

```java
// BIGINT GENERATED ALWAYS AS IDENTITY → IDENTITY strategy in JPA
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Long id;

// UUID
@Id
@GeneratedValue(strategy = GenerationType.UUID)
@Column(columnDefinition = "UUID DEFAULT gen_random_uuid()")
private UUID id;

// NUMERIC(15,2) for monetary values — never double in Java for money
@Column(name = "nominal_value", precision = 15, scale = 2)
private BigDecimal nominalValue;

// TIMESTAMPTZ → Instant or OffsetDateTime in Java
@Column(name = "created_at")
private Instant createdAt;

// JSONB — with Jackson converter
@Column(columnDefinition = "JSONB")
@Convert(converter = JsonbConverter.class)
private Map<String, Object> metadata;

// Enum → TEXT in PostgreSQL (not SMALLINT — see spring-data-jpa)
@Enumerated(EnumType.STRING)
@Column(name = "status")
private ItemStatus status;
```

### Common ORM ↔ DB issues

**Hibernate generates a schema different from what is expected**:
```yaml
# Use validate to detect discrepancies at startup rather than discovering them at runtime

spring.jpa.hibernate.ddl-auto: validate
```

**Hibernate does not use the index you created**:
- Verify with `EXPLAIN ANALYZE` that PostgreSQL sees it
- Hibernate does not control indices — only the PostgreSQL query planner decides
- If the planner does not use it, the cause may be stale statistics (`ANALYZE`) or too low selectivity

**N+1 at the DB level** — see `spring-data-jpa` for the ORM solution. At the DB level:
```sql
-- Diagnostics: how many queries arrive for a single operation?
-- Enable log_min_duration_statement in dev
log_min_duration_statement = 0  -- logs all queries
-- In staging: log_min_duration_statement = 100 (ms)
```

### Liquibase — migration best practice

```yaml
# db/changelog/v1.0/01-init-main-schema.yaml

databaseChangeLog:
  - changeSet:
      id: 01-create-schema-main
      author: dev-team
      changes:
        - sql:
            sql: CREATE SCHEMA IF NOT EXISTS schema_main;

  - changeSet:
      id: 02-create-companies
      author: dev-team
      changes:
        - createTable:
            schemaName: schema_main
            tableName: companies
            columns:
              - column:
                  name: id
                  type: BIGINT
                  autoIncrement: true
                  constraints:
                    primaryKey: true
                    nullable: false
              - column:
                  name: name
                  type: TEXT
                  constraints: { nullable: false }
              - column:
                  name: business_code
                  type: TEXT
                  constraints: { unique: true }
              - column:
                  name: vat_number
                  type: CHAR(11)
                  constraints: { unique: true }
              - column:
                  name: status
                  type: TEXT
                  defaultValue: ACTIVE
                  constraints: { nullable: false }
              - column:
                  name: created_at
                  type: TIMESTAMP WITH TIME ZONE
                  defaultValueComputed: NOW()
                  constraints: { nullable: false }
        - sql:
            sql: |
              ALTER TABLE schema_main.companies
                ADD CONSTRAINT chk_companies_status
                CHECK (status IN ('ACTIVE','INACTIVE','SUSPENDED'));

  - changeSet:
      id: 03-index-companies-name-lower
      author: dev-team
      changes:
        - createIndex:
            schemaName: schema_main
            tableName: companies
            indexName: idx_companies_name_lower
            columns:
              - column: { name: "LOWER(name)" }

  # ─── Two-step NOT NULL on a populated table ─────────────────────────────
  # db/changelog/v1.1/01-add-industry-nullable.yaml
  - changeSet:
      id: 04-add-companies-industry-nullable
      author: dev-team
      changes:
        - addColumn:
            schemaName: schema_main
            tableName: companies
            columns:
              - column:
                  name: industry
                  type: TEXT
                  defaultValue: UNKNOWN

  # db/changelog/v1.1/02-add-industry-not-null.yaml — runs AFTER backfill
  - changeSet:
      id: 05-add-companies-industry-not-null
      author: dev-team
      changes:
        - addNotNullConstraint:
            schemaName: schema_main
            tableName: companies
            columnName: industry
```

**Rule for ADD COLUMN NOT NULL on a table with data**: split into two separate changesets — first nullable with DEFAULT, then NOT NULL after backfill. Adding NOT NULL directly on a table with existing rows can cause a prolonged lock or failure.

**Free-form SQL fallback**: when a Liquibase declarative change is more verbose than helpful (complex constraints, partial indexes, generated columns, PostgreSQL-specific DDL), use the `sql:` change-type with the SQL written verbatim, **always paired with a `rollback:` block**. Do not use `formatted SQL` changelogs unless the team has standardised on them.

---
