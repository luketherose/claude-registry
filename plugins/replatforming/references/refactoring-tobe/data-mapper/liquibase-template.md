# Data-mapper — Liquibase changelog templates

> Reference doc for `data-mapper`. Read at runtime when emitting Liquibase
> YAML changelogs. The decision rules (Case A vs Case B, immutability,
> rollback policy) live in the agent body under `## Method`. The YAML
> skeletons below are the literal shapes to copy-and-parametrise.

## Layout

Generate one master aggregator + one changelog file per logical change
under `<backend-dir>/src/main/resources/db/changelog/`:

```
<backend-dir>/src/main/resources/db/changelog/
  db.changelog-master.yaml      ← aggregator, includes every changelog below
  01__baseline_schema.yaml      ← TO-BE baseline (greenfield) or AS-IS snapshot (Case B)
  02__<next-change>.yaml        ← subsequent changes
  ...
  zz__seed-data.yaml            ← optional, gated on context: local
```

## `db.changelog-master.yaml` — option A (includeAll)

```yaml
databaseChangeLog:
  - includeAll:
      path: classpath:db/changelog/
      filter: "\\d{2}__.+\\.yaml"
      relativeToChangelogFile: false
```

## `db.changelog-master.yaml` — option B (explicit ordering)

If you prefer explicit ordering over `includeAll`, list every changelog in
order:

```yaml
databaseChangeLog:
  - include: { file: db/changelog/01__baseline_schema.yaml }
  - include: { file: db/changelog/02__add_audit_columns.yaml }
  # ... append new changelogs at the bottom; never reorder published entries
```

## `01__baseline_schema.yaml`

```yaml
databaseChangeLog:
  - changeSet:
      id: 01-create-users
      author: data-mapper
      comment: >
        Baseline schema for <app>. BCs: BC-01 (Identity & Access).
        Generated from .refactoring-kb/00-decomposition/aggregate-design.md.
        ADR-002: target DB = PostgreSQL 16; Liquibase YAML changelogs.
      changes:
        - createTable:
            tableName: users
            columns:
              - column:
                  name: id
                  type: uuid
                  defaultValueComputed: gen_random_uuid()
                  constraints: { primaryKey: true, nullable: false }
              - column:
                  name: email
                  type: varchar(255)
                  constraints: { nullable: false }
              - column:
                  name: password_hash
                  type: varchar(60)
                  constraints: { nullable: false }
              - column:
                  name: status
                  type: varchar(20)
                  constraints: { nullable: false }
              - column:
                  name: created_at
                  type: timestamptz
                  constraints: { nullable: false }
              - column:
                  name: updated_at
                  type: timestamptz
                  constraints: { nullable: false }
              - column:
                  name: version
                  type: bigint
                  defaultValueNumeric: 0
                  constraints: { nullable: false }
        - addUniqueConstraint:
            tableName: users
            columnNames: email
            constraintName: uk_users_email
        - createIndex:
            tableName: users
            indexName: idx_users_status
            columns:
              - column: { name: status }
      rollback:
        - dropTable: { tableName: users }

  # ... additional changeSets for BC-02, etc.
```

## Rules

- one changeSet per logical change (avoid mega-changesets)
- **never edit a deployed changeSet** — its checksum is recorded in
  `DATABASECHANGELOG`; always add a new one with the next id
- author = `data-mapper` (or the human author when hand-edited)
- prefer YAML over SQL/XML formats — diffs and conditional logic are
  cleaner; raw SQL is allowed only inside a `sql:` change when YAML
  cannot express the operation (e.g., DB-specific functions)
- always include a `rollback:` block (Liquibase needs it for
  `liquibase rollback`); for irreversible changes, emit `<empty />`
  rollback with a comment
- explicit constraint names (forward-compatible)
- indexes on common query patterns from Phase 2
- contexts: tag environment-specific changesets with `context: local`
  (e.g., seed data) — production changelogs run unconditionally

## Case B — existing-schema migration

For Case B (existing schema migration), the first changelog is
`01__baseline_existing.yaml` that captures the AS-IS schema (typically from
`liquibase generateChangeLog --url=jdbc:postgresql://...` against a copy of
the existing DB; otherwise inferred from
`.indexing-kb/06-data-flow/database.md`). Subsequent changelogs introduce
changes.
