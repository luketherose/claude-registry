---
name: test-data-seeding-standards
description: "This skill should be used when an agent (`test-data-seeder`, `fixture-builder`, a developer agent producing demo or seed data) needs both the design principles for a coherent cross-module test dataset AND the tool-specific patterns to write it. Returns: the pivot-entity model, lifecycle-state coverage rule, FK consistency rules, login-user permission spread, edge/boundary realism, dataset-plan template, column-length safety checklist, auto-detection logic for 13 migration tools (Liquibase, Flyway, Django, Rails, EF Core, Knex, TypeORM, Prisma, sqlx, Diesel, goose, Alembic, raw SQL), idempotent insert templates per tool, non-production profile gating per tool, and FK-lookup patterns. Trigger phrases: \"test data design\", \"seed dataset principles\", \"how do I gate a seed to dev only\", \"Liquibase changeset\", \"idempotent seed\". Returns standards and templates, not generated code. Do not use this skill for schema migration design (CREATE TABLE, ALTER TABLE, rollback strategies). That is out of scope."
---

# Test Data Seeding Standards

This skill is the authoritative source for designing and writing a
coherent, demo-ready, cross-module test dataset for any application.
It covers:

1. **Design principles**: what a good seed dataset looks like
   (pivot-entity model, lifecycle-state coverage, FK consistency,
   login-user spread, edge realism, column-length safety).
2. **Injection patterns**: how to write the seed file in whatever
   migration tool the project already uses (auto-detection logic,
   idempotent insert templates, non-production profile gating,
   FK-lookup patterns for 13 tools).

Generate no dataset or migration file for a specific application here.
These are the rules and templates. The calling agent applies them
against the project's schema and Phase 1 functional artifacts.

---

## Part 1: Dataset design

### Core principles

1. **Small but complete.** Aim for the smallest dataset that exercises
   every screen, every module, every lifecycle state, and every user
   role. A 5-entity dataset that covers every state is better than a
   500-entity dataset that only covers the happy path.
2. **Coherent across modules.** Every module's data must reference
   the same pivot entities. If `Customer 1001` exists in the CRM
   module, the Billing module must invoice `1001`, the Audit module
   must log `1001`'s actions, the Reporting module must aggregate
   `1001`'s numbers. No orphan IDs.
3. **Lifecycle-state coverage.** If an entity has a state machine
   (`draft → submitted → approved → closed`), seed at least one row
   per state. The reviewer cannot judge a "Closed" tab if no row is
   in the Closed state.
4. **Realistic but anodyne.** Use plausible domain values (company
   names, amounts, dates), but values that could not be mistaken
   for real customers. `Acme`, `Beta`, `Gamma`, `Delta`, `Epsilon` is
   a canonical alias set for five pivot companies. `IT12345678901`
   is a canonical anodyne VAT.
5. **One row per role, one row per state, one row per boundary.**
   Coverage matters more than volume.
6. **Stable identifiers.** Where the schema allows manually assigned IDs
   use a documented base (`1001..1010`) or business-keyed
   IDs (`COMPANY-001`). Auto-generated IDs are unstable across runs
   and break referential integrity in downstream fixtures.

---

### The pivot-entity model

A **pivot entity** is a core domain entity (Customer, Account,
Order, Product, Project, or whatever the system is about) that every
other module references. Pivot entities are the spine of the dataset.

#### Default pivot count: 5

| Slot | Profile | Why |
|---|---|---|
| 1 | Large / mature / active | Drives "happy path" demos. |
| 2 | Small / growing | Drives boundary tests at the low end. |
| 3 | Cross-border / foreign | Drives locale, currency, regulatory variation. |
| 4 | Distressed / inactive / failing | Drives error-state and recovery flows. |
| 5 | Niche / specialized | Drives less-common feature paths. |

#### Pivot anchor table (mandatory output of any seed plan)

| Alias | Stable ID | Display name | Profile | Used by modules |
|---|---|---|---|---|
| Acme | 1001 / `COMPANY-001` | Acme Industries | Large, active | CRM, Billing, Audit, Reporting, Demo |
| Beta | 1002 / `COMPANY-002` | Beta Logistics | Small, growing | CRM, Billing, Audit |
| Gamma | 1003 / `COMPANY-003` | Gamma Holding | Foreign / cross-border | CRM, Billing, Reporting |
| Delta | 1004 / `COMPANY-004` | Delta Retail | Distressed | CRM, Audit, Recovery |
| Epsilon | 1005 / `COMPANY-005` | Epsilon Tech | Niche / tech | CRM, Billing, Reporting |

Adapt the *profile mix* to the application's domain (`Customers`,
`Accounts`, `Projects`, `Devices`, …), but keep the five-slot
diversity and the stable-ID convention.

**Anti-pattern:** do not let each module invent its own anchor IDs.
A dataset where the CRM module uses `100000001` but the Billing
module uses `COMP-XYZ` for the same conceptual customer is
incoherent and makes cross-module flows untestable.

---

### Lifecycle-state coverage rule

For every stateful entity (any entity whose schema has a `status`,
`state`, `phase`, or equivalent column with a finite value set):

- **One row per reachable state.** If the documented states are
  `OPEN`, `IN_PROGRESS`, `CLOSED`, `CANCELLED`, the seed needs 4 rows.
- **Documented states only.** Pull the state list from Phase 1
  business-rules or the schema's CHECK constraint / enum type.
  Never invent states.
- **Audit trail (where present).** If the entity has an audit log,
  seed at least one audit row per non-terminal state so the audit
  tab is not empty.
- **Terminal-state realism.** A `CLOSED` row should have a
  `closed_at` timestamp; an `EXPIRED` row should have an
  `expired_at` in the past. Empty terminal fields look like bugs.

---

### Login-user spread

| Slot | Username | Role | Why |
|---|---|---|---|
| 1 | `admin` | Administrator, all permissions | Drives admin-only screens. |
| 2 | `<analyst-or-role-1>` | Single-permission, common role | Drives the most-frequent auth context. |
| 3 | `<analyst-or-role-2>` | Multi-permission, cross-functional | Drives navigation between bounded contexts. |
| 4 | `<bob-or-inactive>` | Limited / inactive (where supported) | Drives unauthorized-state UI. |

Use `password == username` for the test profile so the recap can
publish credentials in plain text without raising a security alarm.
Derive role names from the project's actor list in Phase 1. Do not
copy the slot labels verbatim.

---

### Foreign-key consistency rules

1. **Orphan FK.** A child row references a parent ID that doesn't
   exist. **Prevention:** topologically sort the seed by dependency,
   parents first.
2. **Stale auto-generated PK.** A child row hardcodes a parent's
   auto-generated ID from a previous run. **Prevention:** use lookup
   patterns (see Part 2, Step 4).
3. **Composite-PK collision.** Two rows insert into a composite-PK
   table with the same key tuple. **Prevention:** list every
   composite-PK row in the dataset plan explicitly.
4. **Cascade-delete surprise.** A seed re-run deletes child rows
   transitively. **Prevention:** use the migration tool's idempotence
   guarantee (changeset id / `find_or_create_by!` / `ON CONFLICT DO
   NOTHING`) rather than DROP + INSERT.

---

### Column-length safety checklist

The most common seed failure is `Value too long for column VARCHAR(N)`.

For every textual value to be inserted:

1. Look up the column's declared length in the schema (`@Column(length
   = ...)`, `VARCHAR(N)`, `max_length=N`).
2. Compare to the literal value's character length.
3. If the value exceeds the length, **shorten the value**. Do not
   extend the column. The schema is the contract; the seed conforms.
4. Pay special attention to small VARCHAR columns: `VARCHAR(10)`,
   `VARCHAR(20)`, `VARCHAR(50)` are common limits on status,
   enum-like, and code columns.
5. CHECK constraints with explicit value lists are length-implied;
   the seed value must also be in the allowed set.

---

### Edge / boundary realism

| Column kind | Boundary rows to seed |
|---|---|
| Date in past/future | one near-past, one near-future, one current |
| Numeric amount | one zero, one large positive, one large negative (if allowed) |
| Optional FK | one row with the FK set, one row with it `NULL` (if nullable) |
| Boolean flag | one row `true`, one row `false`, one row `NULL` if tri-state |
| Free-text | one short, one near-max-length |

---

### Dataset plan template (internal artifact)

Before writing the seed file, produce a plan in this shape:

```markdown
# Dataset plan

## Pivot entities
[the 5-slot anchor table]

## Login users
[the spread table]

## Per-module row plan
| Bounded context | Tables | Rows | Lifecycle states covered | Notes |
|---|---|---|---|---|

## Cross-module coherence map
- pivot <alias> → <bc-1>.<table>.<column> → <bc-2>.<table>.<column>

## Column-length pre-check
| Table.column | Length | Worst-case literal | Pass? |
|---|---|---|---|

## Gaps / accepted sentinels
- <column> filled with <sentinel> because no Phase 1 mapping existed.
```

Do not emit a seed file until every section of the plan has been
filled.

---

### Domain examples

**M&A / CRM:** Acme / Beta / Gamma / Delta / Epsilon. See anchor
table above.

**Banking:**

| Alias | Account ID | Currency | Country | Profile |
|---|---|---|---|---|
| Account-A | ACC-001 | EUR | IT | High-balance, active |
| Account-B | ACC-002 | EUR | IT | Low-balance, new |
| Account-C | ACC-003 | CHF | CH | Cross-border |
| Account-D | ACC-004 | EUR | IT | Overdrawn / risk |
| Account-E | ACC-005 | USD | US | Foreign currency |

**IoT:**

| Alias | Device ID | Type | Status | Profile |
|---|---|---|---|---|
| D-A | DEV-001 | Sensor | ONLINE | Always-on |
| D-B | DEV-002 | Gateway | ONLINE | Aggregator |
| D-C | DEV-003 | Sensor | OFFLINE | Recently disconnected |
| D-D | DEV-004 | Actuator | ALERT | In alarm state |
| D-E | DEV-005 | Sensor | DECOMMISSIONED | Terminal state |

---

## Anti-patterns

- **Seed without gate.** Any seed file without an explicit non-production
  gate is a defect: refuse to emit it.
- **DROP + INSERT.** Never seed by dropping tables; use the tool's
  idempotence mechanism.
- **Hardcoded auto-generated IDs.** Always lookup, never hardcode.
- **String literal exceeding `VARCHAR(N)`.** Run the column-length
  pre-check before writing.
- **Mixed tools.** Don't introduce a second migration tool; use the
  project's existing one.
- **Production-targeted seed.** If the project's only running DB is
  prod, refuse the task.
- **Per-module pivots.** Don't let each module invent its own anchor
  IDs: the dataset breaks cross-module flows.
- **One huge SQL file with no structure.** Group by bounded context,
  prefix with `<NN>-<bc>-seed`.
- **Domain values from another project.** Derive the dataset's shape
  from this project's schema and values from generic anodyne
  placeholders.

## Detailed references

- **Per-tool seed-file injection patterns for 13 migration tools**: see [references/seed-file-patterns.md](references/seed-file-patterns.md)
