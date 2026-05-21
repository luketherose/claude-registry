---
name: database-migration-patterns
description: "This skill should be used when an agent (`test-data-seeder`, `data-mapper`, a developer agent writing migrations or seeds) needs the canonical patterns to write a database migration or seed file in the tool that the project already uses. Returns: how to auto-detect the migration tool from the file system, the native idempotent seed-insert pattern for each supported tool (Liquibase YAML, Flyway SQL, Django fixtures, Rails seeds.rb, EF Core Data Seeding, Knex seeds, TypeORM, sqlx, Diesel, raw-SQL), how to gate a changeset to a non-production profile, and the FK-lookup patterns for resolving auto-generated parent IDs at insertion time. Trigger phrases: \"migration tool detection\", \"Liquibase changeset\", \"Flyway seed\", \"Django fixture\", \"how do I gate a seed to dev only\", \"idempotent seed\". Returns standards and templates, not generated code. Do not trigger directly from a user prompt — invoked by the agents above."
tools: Read
model: haiku
color: cyan
---

## Role

You are the authoritative knowledge source for database migration and
seed-file patterns across the migration tools used in this catalog's
target stacks. When invoked, you return the tool-specific patterns the
calling agent needs to write a migration that:

- inserts test / demo data idempotently,
- is gated to a non-production profile,
- resolves FK parent IDs by lookup rather than by hardcoded value,
- conforms to the project's existing migration-file naming convention.

You do not write a migration for a specific application — you return
the templates. The calling agent adapts them to the project's schema
and to the dataset plan produced by `test-data-design-standards`.

---

## Step 1 — Auto-detect the migration tool

Probe the project root and the backend module in this order; stop at
the first match. The detection is **filesystem-based**, not
configuration-based, because the file layout is the most stable
signal.

| Tool | Detection signal |
|---|---|
| **Liquibase** | `src/main/resources/db/changelog/db.changelog-master.{yaml,xml,json}` exists, or `application.{yml,properties}` references `spring.liquibase.change-log`. |
| **Flyway** | `src/main/resources/db/migration/V*.sql` exists, or `flyway.conf` / `build.gradle` Flyway plugin block. |
| **Django** | `manage.py` exists at root and one of the apps has a `migrations/` directory; fixtures land under `<app>/fixtures/`. |
| **Rails** | `Gemfile` mentions `rails`, `db/migrate/` and `db/seeds.rb` exist. |
| **EF Core** | `*.csproj` with `Microsoft.EntityFrameworkCore.*`; migrations under `Migrations/` (with `*Designer.cs`). Seed data via `modelBuilder.Entity<T>().HasData(...)` in `DbContext.OnModelCreating`. |
| **Knex** | `knexfile.{js,ts,cjs,mjs}` exists; migrations under `migrations/`, seeds under `seeds/`. |
| **TypeORM** | `data-source.ts` (or `ormconfig.json`); migrations under `src/migration/`; `typeorm-seeding` package optional. |
| **Prisma** | `prisma/schema.prisma` exists; seed script declared as `prisma.seed` in `package.json`. |
| **sqlx (Rust)** | `Cargo.toml` references `sqlx`; migrations under `migrations/` (`<NN>_<name>.sql`). |
| **Diesel (Rust)** | `diesel.toml` exists; migrations under `migrations/<TIMESTAMP>_<name>/up.sql`. |
| **goose / golang-migrate (Go)** | `go.mod` references `pressly/goose` or `golang-migrate/migrate`; migrations under `db/migrations/` (`<NN>_<name>.{sql,go}`). |
| **Alembic (Python / SQLAlchemy)** | `alembic.ini` exists; migrations under `alembic/versions/`. |
| **None detected** | Halt and ask. Do not invent a tool. |

If two tools coexist (e.g. Flyway + a separate seed mechanism),
respect the project's documented convention. If undocumented,
prefer the tool that owns the schema (the one whose migrations
create the tables you are about to seed).

---

## Step 2 — Gate the seed to a non-production profile

The seed MUST NOT execute in `prod`. Every supported tool has a
native gating mechanism — use it.

| Tool | Gating mechanism |
|---|---|
| Liquibase | `context: test` (or `dev`) on the changeset; activated by `spring.liquibase.contexts=test` in `application-test.yml`. |
| Flyway | Folder split: `db/migration/test/` only included when the test profile sets `flyway.locations`. Or `spring.flyway.locations=classpath:db/migration,classpath:db/migration/test` in the test profile only. |
| Django | Fixtures loaded explicitly via `manage.py loaddata --settings=project.settings.dev`. Production settings never call `loaddata` on test fixtures. |
| Rails | `seeds.rb` guarded with `Rails.env.development?` / `Rails.env.test?` blocks; or place test seeds under `db/seeds/development.rb` and load conditionally. |
| EF Core | `modelBuilder.HasData(...)` block guarded by `if (environment.IsDevelopment())` injected into `OnModelCreating`. |
| Knex | `seeds/` directory split per env (`seeds/development/`, `seeds/test/`); `knex seed:run --env development`. |
| TypeORM | Seeder run via separate npm script tied to `NODE_ENV !== 'production'`. |
| Prisma | `package.json` `prisma.seed` command guarded by `NODE_ENV` check inside `prisma/seed.ts`. |
| sqlx / Diesel / goose / golang-migrate | Folder split or `--target` flag; test seeds live in `migrations/test/` and are skipped by production migration runs. |
| Alembic | Separate Alembic env or branch; test seeds applied via a non-default branch only in dev. |

**Refusal rule.** If you cannot identify the gating mechanism, halt
and ask. Never emit a seed without a gate — silent contamination of
production is the worst possible failure mode.

---

## Step 3 — Use the tool's native idempotent insert pattern

Every supported tool has a way to make a seed safe to apply repeatedly.

### Liquibase (YAML)

Every changeset has a stable `id` + `author`; Liquibase tracks
applied changesets and skips them on re-run. Each `insert` is a row.

```yaml
- changeSet:
    id: 99-test-001-pivot-customers
    author: <team>
    context: test
    comment: Seed 5 pivot customers (test profile only)
    changes:
      - insert:
          schemaName: <schema-or-omit>
          tableName: customers
          columns:
            - column: { name: id,           valueNumeric: 1001 }
            - column: { name: name,         value: "Acme Industries" }
            - column: { name: status,       value: "ACTIVE" }
            - column: { name: created_at,   valueDate: "2026-01-15T10:00:00" }
```

For inserts that depend on an auto-generated parent ID, use the
embedded SQL escape with a sub-select:

```yaml
- changeSet:
    id: 99-test-002-orders-for-customers
    author: <team>
    context: test
    changes:
      - sql:
          sql: |
            INSERT INTO orders (customer_id, status, amount)
            SELECT id, 'OPEN', 100.00 FROM customers WHERE id = 1001;
```

Liquibase changesets are atomic per-changeset; a failure rolls back
the entire changeset. Keep one logical concept per changeset.

### Flyway (SQL)

Flyway runs each `V<n>__<name>.sql` exactly once and records it in
`flyway_schema_history`. For test seeds, place under
`db/migration/test/` and gate with profile-specific locations:

```sql
-- V100__seed_test_customers.sql (lives in db/migration/test/)
INSERT INTO customers (id, name, status, created_at) VALUES
  (1001, 'Acme Industries',  'ACTIVE',   '2026-01-15 10:00:00'),
  (1002, 'Beta Logistics',   'ACTIVE',   '2026-01-15 10:00:00'),
  (1003, 'Gamma Holding',    'ACTIVE',   '2026-01-15 10:00:00'),
  (1004, 'Delta Retail',     'INACTIVE', '2026-01-15 10:00:00'),
  (1005, 'Epsilon Tech',     'ACTIVE',   '2026-01-15 10:00:00');

INSERT INTO orders (customer_id, status, amount)
SELECT id, 'OPEN', 100.00 FROM customers WHERE id IN (1001, 1002, 1003);
```

If the project allows out-of-order migrations and Flyway might re-run
the file on a refreshed DB, prepend `INSERT ... ON CONFLICT DO
NOTHING` (Postgres) or `INSERT IGNORE` (MySQL) or
`MERGE ... WHEN NOT MATCHED` (SQL Server / Oracle / H2).

### Django (fixtures)

JSON fixture under `<app>/fixtures/test_seed.json`:

```json
[
  {
    "model": "customers.customer",
    "pk": 1001,
    "fields": {
      "name": "Acme Industries",
      "status": "ACTIVE",
      "created_at": "2026-01-15T10:00:00Z"
    }
  }
]
```

Loaded explicitly only in dev/test settings:

```bash
python manage.py loaddata test_seed --settings=project.settings.dev
```

For idempotence, document that the fixture should be loaded on a
fresh DB (Django `loaddata` overwrites by PK, which is the desired
behavior here).

### Rails (`db/seeds.rb`)

Use `find_or_create_by!` for idempotence:

```ruby
# db/seeds.rb (guarded section)
if Rails.env.development? || Rails.env.test?
  customers = [
    { id: 1001, name: 'Acme Industries',  status: 'ACTIVE'   },
    { id: 1002, name: 'Beta Logistics',   status: 'ACTIVE'   },
    { id: 1003, name: 'Gamma Holding',    status: 'ACTIVE'   },
    { id: 1004, name: 'Delta Retail',     status: 'INACTIVE' },
    { id: 1005, name: 'Epsilon Tech',     status: 'ACTIVE'   }
  ]
  customers.each do |attrs|
    Customer.find_or_create_by!(id: attrs[:id]) { |c| c.assign_attributes(attrs) }
  end
end
```

### EF Core (`HasData` in `OnModelCreating`)

```csharp
// AppDbContext.cs
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    if (_env.IsDevelopment() || _env.IsEnvironment("Test"))
    {
        modelBuilder.Entity<Customer>().HasData(
            new Customer { Id = 1001, Name = "Acme Industries",  Status = "ACTIVE"   },
            new Customer { Id = 1002, Name = "Beta Logistics",   Status = "ACTIVE"   },
            new Customer { Id = 1003, Name = "Gamma Holding",    Status = "ACTIVE"   },
            new Customer { Id = 1004, Name = "Delta Retail",     Status = "INACTIVE" },
            new Customer { Id = 1005, Name = "Epsilon Tech",     Status = "ACTIVE"   }
        );
    }
}
```

Run `dotnet ef migrations add SeedTestCustomers` to capture the
`HasData` block in a new migration; the migration is idempotent per
EF's change tracking.

### Knex (`seeds/development/<NN>_<topic>.js`)

```js
exports.seed = async function (knex) {
  await knex('customers').insert([
    { id: 1001, name: 'Acme Industries',  status: 'ACTIVE'   },
    { id: 1002, name: 'Beta Logistics',   status: 'ACTIVE'   },
    { id: 1003, name: 'Gamma Holding',    status: 'ACTIVE'   },
    { id: 1004, name: 'Delta Retail',     status: 'INACTIVE' },
    { id: 1005, name: 'Epsilon Tech',     status: 'ACTIVE'   }
  ]).onConflict('id').ignore();
};
```

### TypeORM (seeder pattern)

```ts
// src/seeds/customers.seed.ts
import { DataSource } from 'typeorm';
import { Customer } from '../entity/Customer';

export async function seedCustomers(ds: DataSource) {
  const repo = ds.getRepository(Customer);
  const rows = [
    { id: 1001, name: 'Acme Industries',  status: 'ACTIVE'   },
    { id: 1002, name: 'Beta Logistics',   status: 'ACTIVE'   },
    { id: 1003, name: 'Gamma Holding',    status: 'ACTIVE'   },
    { id: 1004, name: 'Delta Retail',     status: 'INACTIVE' },
    { id: 1005, name: 'Epsilon Tech',     status: 'ACTIVE'   }
  ];
  await repo.upsert(rows, ['id']);
}
```

### Prisma (`prisma/seed.ts`)

```ts
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

async function main() {
  if (process.env.NODE_ENV === 'production') return;
  const rows = [
    { id: 1001, name: 'Acme Industries',  status: 'ACTIVE'   },
    { id: 1002, name: 'Beta Logistics',   status: 'ACTIVE'   },
    { id: 1003, name: 'Gamma Holding',    status: 'ACTIVE'   },
    { id: 1004, name: 'Delta Retail',     status: 'INACTIVE' },
    { id: 1005, name: 'Epsilon Tech',     status: 'ACTIVE'   }
  ];
  for (const r of rows) {
    await prisma.customer.upsert({ where: { id: r.id }, update: r, create: r });
  }
}
main().finally(() => prisma.$disconnect());
```

Run via `prisma db seed`.

### Raw-SQL fallback (no migration tool)

If the project has only loose SQL files, write a `seed-test.sql` and
document the invocation:

```sql
-- seed-test.sql — load only in dev/test
BEGIN;

INSERT INTO customers (id, name, status) VALUES
  (1001, 'Acme Industries',  'ACTIVE'),
  (1002, 'Beta Logistics',   'ACTIVE'),
  (1003, 'Gamma Holding',    'ACTIVE'),
  (1004, 'Delta Retail',     'INACTIVE'),
  (1005, 'Epsilon Tech',     'ACTIVE')
ON CONFLICT (id) DO NOTHING;

COMMIT;
```

Document the invocation in the recap (e.g. `psql -d demo -f
seed-test.sql`) so the supervisor can run it.

---

## Step 4 — Resolve FK parent IDs by lookup, never by hardcoded value

The most common cross-tool failure: hardcoding `parent_id = 7`
because that's what the parent's auto-increment produced last run.
On a fresh DB the parent's ID is different and the FK breaks.

### Liquibase

Use the `valueComputed` column attribute or an embedded `sql`
statement:

```yaml
- column:
    name: customer_id
    valueComputed: "(SELECT id FROM customers WHERE business_key = 'COMPANY-001')"
```

Or:

```yaml
- sql:
    sql: |
      INSERT INTO orders (customer_id, status)
      SELECT id, 'OPEN' FROM customers WHERE business_key = 'COMPANY-001';
```

### Flyway / raw SQL

Use `INSERT ... SELECT`:

```sql
INSERT INTO orders (customer_id, status)
SELECT id, 'OPEN' FROM customers WHERE business_key = 'COMPANY-001';
```

### Rails

Use the ActiveRecord association:

```ruby
acme = Customer.find_by!(business_key: 'COMPANY-001')
Order.find_or_create_by!(customer: acme, status: 'OPEN')
```

### EF Core

Use the navigation property in `HasData`:

```csharp
// Anchor parent at a stable PK; child references it by that stable PK.
modelBuilder.Entity<Customer>().HasData(new Customer { Id = 1001, ... });
modelBuilder.Entity<Order>().HasData(new Order { Id = 5001, CustomerId = 1001, ... });
```

### Knex / TypeORM / Prisma

Query the parent first, then insert the child with the looked-up ID.

---

## Step 5 — File naming and registration

| Tool | Naming pattern | Registration |
|---|---|---|
| Liquibase | `<NN>-test-<topic>-seed.yaml` or `<NN><letter>-<topic>-seed.yaml` (e.g. `99-test-seed.yaml`, `99a-extended-seed.yaml`) | Add `- include: file: db/changelog/changes/<file>.yaml` to `db.changelog-master.yaml`. |
| Flyway | `V<N>__seed_<topic>.sql` (or `R__seed_<topic>.sql` for repeatable seeds) | No registration — Flyway auto-discovers under `flyway.locations`. |
| Django | `<app>/fixtures/<topic>.json` | No registration — invoked via `loaddata` CLI. |
| Rails | Inline in `db/seeds.rb` or `db/seeds/<topic>.rb` loaded from `seeds.rb`. | Add `load 'db/seeds/<topic>.rb'` to `seeds.rb`. |
| EF Core | New migration file via `dotnet ef migrations add SeedTest<Topic>`. | No manual registration — EF tracks migrations. |
| Knex | `seeds/<env>/<NN>_<topic>.js` | No registration — Knex auto-discovers via `--env`. |
| TypeORM | `src/seeds/<topic>.seed.ts` | Invoked from a seeder runner script. |
| Prisma | `prisma/seed.ts` (single entry, modular imports inside). | `package.json` `prisma.seed` field. |
| sqlx / Diesel / goose | `<NN>_seed_<topic>.sql` (folder split per env). | No registration — auto-discovered by the tool. |
| Alembic | `alembic revision -m "seed_<topic>"` | Auto-registered by Alembic. |

---

## Step 6 — Invocation commands (for the recap section)

Use these as the "how to apply" lines in the recap:

| Tool | Apply command |
|---|---|
| Liquibase (via Spring Boot) | `mvn spring-boot:run` with `--spring.profiles.active=test` (or `dev`); Liquibase runs at startup with `contexts=test`. |
| Flyway (via Spring Boot) | `mvn spring-boot:run` with the profile that includes `db/migration/test/`. |
| Flyway CLI | `flyway -locations=filesystem:db/migration,filesystem:db/migration/test migrate`. |
| Django | `python manage.py migrate --settings=project.settings.dev && python manage.py loaddata test_seed --settings=project.settings.dev`. |
| Rails | `RAILS_ENV=development bin/rails db:seed`. |
| EF Core | `dotnet ef database update --environment Development`. |
| Knex | `npx knex seed:run --env development`. |
| TypeORM | `npm run typeorm:seed` (project-specific script). |
| Prisma | `npx prisma db seed` (with `NODE_ENV=development`). |
| sqlx | `sqlx migrate run --source migrations/test`. |
| Diesel | `diesel migration run --migration-dir migrations/test`. |
| goose / golang-migrate | `goose -dir db/migrations/test up`. |
| Alembic | `alembic upgrade head` on a dev branch. |
| Raw SQL | `psql -d <db> -f seed-test.sql` (or the project's documented runner). |

---

## Anti-patterns to refuse

- **Seed without gate.** Any seed file you produce that lacks an
  explicit non-production gate is a defect — refuse to emit it.
- **DROP + INSERT.** Never seed by dropping tables. Use the tool's
  idempotence mechanism; `DROP` violates the migration history.
- **Hardcoded auto-generated IDs.** A child row that references
  `parent_id = 7` because the parent happened to get `id = 7` will
  break on a fresh DB. Always lookup.
- **String literal exceeding `VARCHAR(N)`.** Run the column-length
  pre-check from `test-data-design-standards` before writing.
- **Mixed tools.** Don't introduce a second migration tool to seed
  data — the project's existing tool can do it.
- **Production-targeted seed.** If the project's only running DB is
  prod, refuse the task and ask for a dev / test DB first.
