# Seed file patterns

## Contents

- Part 2: Seed-file injection patterns
- Step 1: Auto-detect the migration tool
- Step 2: Gate the seed to a non-production profile
- Step 3: Idempotent insert templates per tool
- Step 4: Resolve FK parent IDs by lookup, never by hardcoded value
- Step 5: File naming and registration
- Step 6: Invocation commands (for the recap)

## Part 2: Seed-file injection patterns

### Step 1: Auto-detect the migration tool

Probe the project root and backend module in this order; stop at
the first match.

| Tool | Detection signal |
|---|---|
| **Liquibase** | `src/main/resources/db/changelog/db.changelog-master.{yaml,xml,json}` exists, or `application.{yml,properties}` references `spring.liquibase.change-log`. |
| **Flyway** | `src/main/resources/db/migration/V*.sql` exists, or `flyway.conf` / `build.gradle` Flyway plugin block. |
| **Django** | `manage.py` exists at root and one of the apps has a `migrations/` directory; fixtures land under `<app>/fixtures/`. |
| **Rails** | `Gemfile` mentions `rails`, `db/migrate/` and `db/seeds.rb` exist. |
| **EF Core** | `*.csproj` with `Microsoft.EntityFrameworkCore.*`; migrations under `Migrations/` (with `*Designer.cs`). |
| **Knex** | `knexfile.{js,ts,cjs,mjs}` exists; migrations under `migrations/`, seeds under `seeds/`. |
| **TypeORM** | `data-source.ts` (or `ormconfig.json`); migrations under `src/migration/`. |
| **Prisma** | `prisma/schema.prisma` exists; seed script declared as `prisma.seed` in `package.json`. |
| **sqlx (Rust)** | `Cargo.toml` references `sqlx`; migrations under `migrations/` (`<NN>_<name>.sql`). |
| **Diesel (Rust)** | `diesel.toml` exists; migrations under `migrations/<TIMESTAMP>_<name>/up.sql`. |
| **goose / golang-migrate (Go)** | `go.mod` references `pressly/goose` or `golang-migrate/migrate`; migrations under `db/migrations/`. |
| **Alembic (Python)** | `alembic.ini` exists; migrations under `alembic/versions/`. |
| **None detected** | Halt and ask. Do not invent a tool. |

If two tools coexist, prefer the one that owns the schema (the one
whose migrations create the tables you are about to seed).

---

### Step 2: Gate the seed to a non-production profile

The seed MUST NOT execute in `prod`.

| Tool | Gating mechanism |
|---|---|
| Liquibase | `context: test` on the changeset; activated by `spring.liquibase.contexts=test` in `application-test.yml`. |
| Flyway | Folder split: `db/migration/test/` included only when the test profile sets `flyway.locations`. |
| Django | `manage.py loaddata --settings=project.settings.dev`. Production settings never call `loaddata` on test fixtures. |
| Rails | `seeds.rb` guarded with `Rails.env.development? / test?`; or `db/seeds/development.rb` loaded conditionally. |
| EF Core | `modelBuilder.HasData(...)` guarded by `if (environment.IsDevelopment())` in `OnModelCreating`. |
| Knex | `seeds/development/` directory; `knex seed:run --env development`. |
| TypeORM | Seeder script tied to `NODE_ENV !== 'production'`. |
| Prisma | `NODE_ENV` check inside `prisma/seed.ts`. |
| sqlx / Diesel / goose / golang-migrate | Folder split (`migrations/test/`) skipped in production runs. |
| Alembic | Separate env or branch; applied via a non-default branch only in dev. |

**Refusal rule.** If you cannot identify the gating mechanism, halt
and ask. Never emit a seed without a gate.

---

### Step 3: Idempotent insert templates per tool

#### Liquibase (YAML)

```yaml
- changeSet:
    id: 99-test-001-pivot-customers
    author: <team>
    context: test
    comment: Seed 5 pivot customers (test profile only)
    changes:
      - insert:
          tableName: customers
          columns:
            - column: { name: id,         valueNumeric: 1001 }
            - column: { name: name,        value: "Acme Industries" }
            - column: { name: status,      value: "ACTIVE" }
            - column: { name: created_at,  valueDate: "2026-01-15T10:00:00" }
```

For FK-dependent rows, use embedded SQL:

```yaml
- changeSet:
    id: 99-test-002-orders
    author: <team>
    context: test
    changes:
      - sql:
          sql: |
            INSERT INTO orders (customer_id, status, amount)
            SELECT id, 'OPEN', 100.00 FROM customers WHERE id = 1001;
```

#### Flyway (SQL)

```sql
-- V100__seed_test_customers.sql (lives in db/migration/test/)
INSERT INTO customers (id, name, status, created_at) VALUES
  (1001, 'Acme Industries',  'ACTIVE',   '2026-01-15 10:00:00'),
  (1002, 'Beta Logistics',   'ACTIVE',   '2026-01-15 10:00:00'),
  (1003, 'Gamma Holding',    'ACTIVE',   '2026-01-15 10:00:00'),
  (1004, 'Delta Retail',     'INACTIVE', '2026-01-15 10:00:00'),
  (1005, 'Epsilon Tech',     'ACTIVE',   '2026-01-15 10:00:00')
ON CONFLICT (id) DO NOTHING;
```

#### Django (fixtures)

```json
[
  {
    "model": "customers.customer",
    "pk": 1001,
    "fields": { "name": "Acme Industries", "status": "ACTIVE", "created_at": "2026-01-15T10:00:00Z" }
  }
]
```

Loaded via `python manage.py loaddata test_seed --settings=project.settings.dev`.

#### Rails (`db/seeds.rb`)

```ruby
if Rails.env.development? || Rails.env.test?
  [
    { id: 1001, name: 'Acme Industries',  status: 'ACTIVE'   },
    { id: 1002, name: 'Beta Logistics',   status: 'ACTIVE'   },
    { id: 1004, name: 'Delta Retail',     status: 'INACTIVE' }
  ].each { |a| Customer.find_or_create_by!(id: a[:id]) { |c| c.assign_attributes(a) } }
end
```

#### EF Core (`OnModelCreating`)

```csharp
if (_env.IsDevelopment() || _env.IsEnvironment("Test"))
{
    modelBuilder.Entity<Customer>().HasData(
        new Customer { Id = 1001, Name = "Acme Industries",  Status = "ACTIVE"   },
        new Customer { Id = 1004, Name = "Delta Retail",     Status = "INACTIVE" }
    );
}
```

Run `dotnet ef migrations add SeedTestCustomers` to capture.

#### Knex

```js
exports.seed = async function (knex) {
  await knex('customers').insert([
    { id: 1001, name: 'Acme Industries', status: 'ACTIVE'   },
    { id: 1004, name: 'Delta Retail',    status: 'INACTIVE' }
  ]).onConflict('id').ignore();
};
```

#### TypeORM

```ts
export async function seedCustomers(ds: DataSource) {
  const repo = ds.getRepository(Customer);
  await repo.upsert([
    { id: 1001, name: 'Acme Industries', status: 'ACTIVE'   },
    { id: 1004, name: 'Delta Retail',    status: 'INACTIVE' }
  ], ['id']);
}
```

#### Prisma

```ts
async function main() {
  if (process.env.NODE_ENV === 'production') return;
  const rows = [
    { id: 1001, name: 'Acme Industries', status: 'ACTIVE'   },
    { id: 1004, name: 'Delta Retail',    status: 'INACTIVE' }
  ];
  for (const r of rows) {
    await prisma.customer.upsert({ where: { id: r.id }, update: r, create: r });
  }
}
```

#### Raw-SQL fallback

```sql
BEGIN;
INSERT INTO customers (id, name, status) VALUES
  (1001, 'Acme Industries',  'ACTIVE'),
  (1004, 'Delta Retail',     'INACTIVE')
ON CONFLICT (id) DO NOTHING;
COMMIT;
```

Document invocation in the recap (e.g. `psql -d demo -f seed-test.sql`).

---

### Step 4: Resolve FK parent IDs by lookup, never by hardcoded value

The most common cross-tool failure: hardcoding `parent_id = 7`
because that's what auto-increment produced last run. On a fresh DB
the parent's ID is different and the FK breaks.

**Liquibase** (use `valueComputed` or embedded SQL):

```yaml
- column:
    name: customer_id
    valueComputed: "(SELECT id FROM customers WHERE business_key = 'COMPANY-001')"
```

**Flyway / raw SQL** (use `INSERT ... SELECT`):

```sql
INSERT INTO orders (customer_id, status)
SELECT id, 'OPEN' FROM customers WHERE business_key = 'COMPANY-001';
```

**Rails** (use ActiveRecord association):

```ruby
acme = Customer.find_by!(business_key: 'COMPANY-001')
Order.find_or_create_by!(customer: acme, status: 'OPEN')
```

**EF Core**: anchor the parent at a stable PK; child references it
by that PK in `HasData`.

**Knex / TypeORM / Prisma**: query the parent first, then insert
the child with the looked-up ID.

---

### Step 5: File naming and registration

| Tool | Naming pattern | Registration |
|---|---|---|
| Liquibase | `<NN>-test-<topic>-seed.yaml` | `include` in `db.changelog-master.yaml`. |
| Flyway | `V<N>__seed_<topic>.sql` | Auto-discovered under `flyway.locations`. |
| Django | `<app>/fixtures/<topic>.json` | Invoked via `loaddata` CLI. |
| Rails | Inline in `db/seeds.rb` or `db/seeds/<topic>.rb`. | `load` from `seeds.rb`. |
| EF Core | New migration via `dotnet ef migrations add Seed<Topic>`. | Auto-tracked by EF. |
| Knex | `seeds/<env>/<NN>_<topic>.js` | Auto-discovered via `--env`. |
| TypeORM | `src/seeds/<topic>.seed.ts` | Invoked from seeder runner script. |
| Prisma | `prisma/seed.ts` (modular imports inside). | `package.json` `prisma.seed` field. |
| sqlx / Diesel / goose | `<NN>_seed_<topic>.sql` in env subfolder. | Auto-discovered by the tool. |
| Alembic | `alembic revision -m "seed_<topic>"`. | Auto-registered by Alembic. |

---

### Step 6: Invocation commands (for the recap)

| Tool | Apply command |
|---|---|
| Liquibase (Spring Boot) | `mvn spring-boot:run` with `--spring.profiles.active=test`. |
| Flyway (Spring Boot) | `mvn spring-boot:run` with the profile that includes `db/migration/test/`. |
| Flyway CLI | `flyway -locations=filesystem:db/migration,filesystem:db/migration/test migrate`. |
| Django | `python manage.py migrate && python manage.py loaddata test_seed --settings=project.settings.dev`. |
| Rails | `RAILS_ENV=development bin/rails db:seed`. |
| EF Core | `dotnet ef database update --environment Development`. |
| Knex | `npx knex seed:run --env development`. |
| TypeORM | `npm run typeorm:seed` (project-specific). |
| Prisma | `npx prisma db seed` (with `NODE_ENV=development`). |
| sqlx | `sqlx migrate run --source migrations/test`. |
| Diesel | `diesel migration run --migration-dir migrations/test`. |
| goose / golang-migrate | `goose -dir db/migrations/test up`. |
| Alembic | `alembic upgrade head` on dev branch. |
| Raw SQL | `psql -d <db> -f seed-test.sql`. |

---
