# Data modelling

## Contents

- 1. Relational Design Fundamentals
- Normalisation: just enough, no more
- Keys: surrogate vs natural
- Constraints: declare them in the DB, not only in Java
- 2. Practical Data Modelling
- From requirements to schema: process
- Naming conventions
- Schema versioning with Liquibase (preferred)
- Local-dev profile: H2 in-memory + seed data

## 1. Relational Design Fundamentals

### Normalisation: just enough, no more

**First Normal Form (1NF)**: every column is atomic, no arrays in cells, no repeating groups.

```sql
-- ❌ Denormalised — phone numbers as a CSV string
CREATE TABLE contacts (
    id BIGINT PRIMARY KEY,
    name TEXT,
    phones TEXT -- "333-1234,334-5678" → impossible to query an individual number
);

-- ✅ Separate relation
CREATE TABLE contact_phones (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    contact_id BIGINT NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    phone TEXT NOT NULL,
    phone_type TEXT NOT NULL CHECK (phone_type IN ('MOBILE', 'OFFICE', 'HOME'))
);
```

**Second Normal Form (2NF)**: every non-key attribute depends on the entire PK (relevant with composite PKs).

**Third Normal Form (3NF)**: no transitive dependencies. If `city → region`, `region` must not appear in `companies` alongside `city`.

```sql
-- ❌ Transitive dependency: city determines region, region does not depend on company
CREATE TABLE companies (
    id BIGINT PRIMARY KEY,
    name TEXT,
    city TEXT,
    region TEXT -- depends on city, not on company
);

-- ✅ Separate lookup table
CREATE TABLE cities (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL
);

CREATE TABLE companies (
    id BIGINT PRIMARY KEY,
    name TEXT,
    city_code TEXT REFERENCES cities(code)
);
```

**Normalisation vs performance trade-off**: 3NF reduces update anomalies but increases JOINs. For stable lookup tables (regions, categories), controlled denormalisation (copying a field) can be pragmatic if a critical query runs millions of times. Always document the choice and the reason.

### Keys: surrogate vs natural

```sql
-- Surrogate key: BIGINT IDENTITY — recommended for most cases
id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY

-- Natural key: use only if the value is truly immutable and universally unique
vat_number CHAR(11) PRIMARY KEY -- ❌ VAT numbers can change due to company mergers

-- UUID: use when cross-system portability or client-side generation is required
id UUID DEFAULT gen_random_uuid() PRIMARY KEY
```

**General rule**: use `BIGINT GENERATED ALWAYS AS IDENTITY` as the default PK. Use `UUID` only for entities that must be created on the client side before being persisted, or for IDs exposed in public URLs (security through sequence obfuscation).

### Constraints: declare them in the DB, not only in Java

```sql
CREATE TABLE items (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code CHAR(12) NOT NULL,
    owner_id BIGINT NOT NULL,
    nominal_value NUMERIC(15, 2) NOT NULL,
    rate NUMERIC(5, 4),
    expiry_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',

    -- Structural constraints
    CONSTRAINT uq_items_code UNIQUE (code),
    CONSTRAINT fk_items_owner
        FOREIGN KEY (owner_id) REFERENCES owners(id) ON DELETE RESTRICT,
    CONSTRAINT chk_items_nominal_positive
        CHECK (nominal_value > 0),
    CONSTRAINT chk_items_rate_range
        CHECK (rate IS NULL OR rate BETWEEN 0 AND 1),
    CONSTRAINT chk_items_status
        CHECK (status IN ('ACTIVE', 'EXPIRED', 'CANCELLED')),
    CONSTRAINT chk_items_expiry_future
        CHECK (expiry_date > CURRENT_DATE) -- only at insert time
);
```

**DB constraints vs Java-only constraints**: DB constraints are the last line of defence. Code can have bugs, SQL batch jobs bypass the ORM, and migration scripts can insert data directly. Do not rely solely on Bean Validation.

---

## 2. Practical Data Modelling

### From requirements to schema: process

```
Requirements → Entities → Attributes → Relations → Cardinality → Schema → Indices
```

**Example (N:M relation with join entity)**:

Requirement: "A parent entity can have multiple child entities. Each child entity has a unique code and can be associated with multiple participants with different allocations."

```sql
-- Entities: owners, items, participants
-- Relations:
--   owner 1 → N items
--   items N ↔ M participants (with allocation → join entity)

CREATE TABLE item_allocations (
    item_id BIGINT NOT NULL REFERENCES items(id),
    participant_id BIGINT NOT NULL REFERENCES participants(id),
    allocation_amount NUMERIC(15, 2) NOT NULL CHECK (allocation_amount > 0),
    allocation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    PRIMARY KEY (item_id, participant_id) -- composite PK in the join entity
);
```

### Naming conventions

| Object | Convention | Example |
|---|---|---|
| Schema | snake_case | `schema_main`, `public` |
| Table | snake_case, plural | `companies`, `items` |
| Column | snake_case | `vat_number`, `created_at` |
| PK | `id` | `id` |
| FK | `{referenced_table}_id` | `company_id` |
| Index | `idx_{table}_{columns}` | `idx_companies_vat_number` |
| Unique constraint | `uq_{table}_{column}` | `uq_companies_business_code` |
| Check constraint | `chk_{table}_{description}` | `chk_items_nominal_positive` |
| FK constraint | `fk_{table}_{ref}` | `fk_items_company` |

### Schema versioning with Liquibase (preferred)

```
src/main/resources/db/changelog/
  db.changelog-master.yaml          ← root changelog, includes all versions
  v1.0/
    01-init-schema.yaml
    02-companies-table.yaml
    03-items-table.yaml
  v1.1/
    01-add-index-companies-code.yaml
    02-add-contact-phones.yaml
  v1.2/
    01-alter-companies-add-industry.yaml   ← ALTER, not DROP+CREATE
  seed/
    data-h2.yaml                    ← seed rows for the local H2 profile only
```

`db.changelog-master.yaml`:

```yaml
databaseChangeLog:
  - includeAll:
      path: db/changelog/v1.0/
      relativeToChangelogFile: true
  - includeAll:
      path: db/changelog/v1.1/
      relativeToChangelogFile: true
  - includeAll:
      path: db/changelog/v1.2/
      relativeToChangelogFile: true
```

**Liquibase rules**:
- Never modify already-applied changesets (Liquibase verifies the checksum). To revert, write a new changeset.
- Each changeset has an `id`, `author`, and (where useful) `preConditions`.
- Use Liquibase changelog formats: YAML (default), XML, or SQL formatted-changelog. Avoid mixing.
- Rollback blocks defined in the same changeset (`rollback:` key) for any non-trivial DDL.
- In production: `ddl-auto=validate`. Liquibase manages the schema, never Hibernate.

```yaml
# application.yml (production / shared baseline)

spring:
  liquibase:
    enabled: true
    change-log: classpath:db/changelog/db.changelog-master.yaml
    contexts: prod                 # filters changesets by context
  jpa:
    hibernate:
      ddl-auto: validate           # Hibernate validates, does not modify
```

### Local-dev profile: H2 in-memory + seed data

Every Spring project ships an `application-local.yml` profile that runs against H2 in-memory with the **same Liquibase changelog** plus a seed-data changeset. Goal: a contributor can clone the repo and run `mvn spring-boot:run -Dspring-boot.run.profiles=local`. The app comes up populated with realistic sample rows, no external DB required.

```yaml
# application-local.yml

spring:
  datasource:
    url: jdbc:h2:mem:appdb;MODE=PostgreSQL;DATABASE_TO_LOWER=TRUE;DB_CLOSE_DELAY=-1
    driver-class-name: org.h2.Driver
    username: sa
    password: ""
  h2:
    console:
      enabled: true                 # /h2-console for visual inspection
      path: /h2-console
  liquibase:
    enabled: true
    change-log: classpath:db/changelog/db.changelog-master.yaml
    contexts: local                 # picks up seed-data changesets gated on `context: local`
  jpa:
    hibernate:
      ddl-auto: validate
    properties:
      hibernate.dialect: org.hibernate.dialect.H2Dialect
```

The seed changeset (`db/changelog/seed/data-h2.yaml`) must declare `context: local` so it does **not** run in `prod` or `test` profiles:

```yaml
databaseChangeLog:
  - changeSet:
      id: seed-companies
      author: dev-team
      context: local
      changes:
        - insert:
            tableName: companies
            columns:
              - column: { name: id, valueNumeric: 1 }
              - column: { name: name, value: "Acme Corp" }
              - column: { name: vat_number, value: "12345678901" }
              - column: { name: status, value: "ACTIVE" }
```

**Maven dependencies for the local profile**:

```xml
<dependency>
    <groupId>org.liquibase</groupId>
    <artifactId>liquibase-core</artifactId>
</dependency>

<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>runtime</scope>
</dependency>
```

---
