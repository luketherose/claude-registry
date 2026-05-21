---
name: test-data-design-standards
description: "This skill should be used when an agent (`test-data-seeder`, `fixture-builder`, a developer agent producing demo data, a QA agent preparing a UAT dataset) needs the canonical principles for designing a coherent, demo-ready, cross-module test dataset. Returns: the pivot-entity model (a small set of anchor IDs referenced by every module), the lifecycle-state coverage rule (one row per documented state per stateful entity), foreign-key consistency rules, login-user permission spread, edge / boundary realism, dataset-plan template, and the column-length safety checklist that prevents the most common seed-failure class. Trigger phrases: \"test data design\", \"seed dataset principles\", \"pivot data\", \"how do I design demo data\", \"why is my seed file failing on a VARCHAR length\". Returns standards and templates, not a generated dataset. Do not trigger directly from a user prompt — invoked by the agents above."
tools: Read
model: haiku
color: cyan
---

## Role

You are the authoritative knowledge source for designing a coherent,
demo-ready, cross-module test dataset for any application. When
invoked, you return the principles and templates an agent needs to
produce a dataset that is **small, realistic, and consistent** across
every bounded context of the system under test.

You do not generate the dataset for a specific application — you
return the rules. The calling agent applies the rules against the
specific schema and Phase 1 functional artifacts of the project.

---

## Core principles

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
   names, amounts, dates) — but values that could not be mistaken
   for real customers. `Acme`, `Beta`, `Gamma`, `Delta`, `Epsilon` is
   a canonical alias set for five pivot companies. `IT12345678901`
   is a canonical anodyne VAT.
5. **One row per role, one row per state, one row per boundary.**
   Coverage matters more than volume.
6. **Stable identifiers.** Where the schema lets you assign IDs
   manually, use a documented base (`1001..1010`) or business-keyed
   IDs (`COMPANY-001`). Auto-generated IDs are unstable across runs
   and break referential integrity in downstream fixtures.

---

## The pivot-entity model

A **pivot entity** is a core domain entity (Customer, Account,
Order, Product, Project — whatever the system is about) that every
other module references. Pivot entities are the spine of the
dataset.

### Default pivot count: 5

Five is the smallest number that gives meaningful variety:

| Slot | Profile | Why |
|---|---|---|
| 1 | Large / mature / active | Drives "happy path" demos. |
| 2 | Small / growing | Drives boundary tests at the low end. |
| 3 | Cross-border / foreign | Drives locale, currency, regulatory variation. |
| 4 | Distressed / inactive / failing | Drives error-state and recovery flows. |
| 5 | Niche / specialized | Drives less-common feature paths. |

### Pivot anchor table (mandatory output of any seed plan)

| Alias | Stable ID | Display name | Profile | Used by modules |
|---|---|---|---|---|
| Acme | 1001 / `COMPANY-001` | Acme Industries | Large, active | CRM, Billing, Audit, Reporting, Demo |
| Beta | 1002 / `COMPANY-002` | Beta Logistics | Small, growing | CRM, Billing, Audit |
| Gamma | 1003 / `COMPANY-003` | Gamma Holding | Foreign / cross-border | CRM, Billing, Reporting |
| Delta | 1004 / `COMPANY-004` | Delta Retail | Distressed | CRM, Audit, Recovery |
| Epsilon | 1005 / `COMPANY-005` | Epsilon Tech | Niche / tech | CRM, Billing, Reporting |

Adapt the *profile mix* to the application's domain (`Customers`,
`Accounts`, `Projects`, `Devices`, …) — but keep the five-slot
diversity and the stable-ID convention.

### Anti-pattern: per-module pivots

Do not let each module invent its own anchor IDs. A dataset where
the CRM module uses `100000001` but the Billing module uses
`COMP-XYZ` for the same conceptual customer is **incoherent** and
makes cross-module flows untestable.

---

## Lifecycle-state coverage rule

For every stateful entity (any entity whose schema has a `status`,
`state`, `phase`, or equivalent column with a finite value set):

- **One row per reachable state.** If the documented states are
  `OPEN`, `IN_PROGRESS`, `CLOSED`, `CANCELLED`, you need 4 rows.
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

## Login-user spread

A demo-ready seed needs varied auth contexts. The minimum spread:

| Slot | Username | Role | Why |
|---|---|---|---|
| 1 | `admin` | Administrator, all permissions | Drives admin-only screens. |
| 2 | `<analyst-or-role-1>` | Single-permission, common role | Drives the most-frequent auth context. |
| 3 | `<analyst-or-role-2>` | Multi-permission, cross-functional | Drives navigation between bounded contexts. |
| 4 | `<bob-or-inactive>` | Limited / inactive (where supported) | Drives unauthorized-state UI. |

### Password convention for test profile

Use `password == username` (so the supervisor's recap can publish
credentials in plain text without raising a security alarm — the
seed is profile-gated to test/dev only). Use the project's existing
hash function; do not introduce a new one.

### Adapt role names to the domain

Do not copy the role names above verbatim — derive them from the
project's actor list in Phase 1 (`docs/analysis/01-functional/`
actors / RBAC matrix). Keep the *spread* (admin + role-1 + role-2 +
edge), drop the verbatim labels.

---

## Foreign-key consistency rules

Every dataset failure I have seen falls into one of these classes;
prevent each one explicitly.

1. **Orphan FK.** A child row references a parent ID that doesn't
   exist. **Prevention:** topologically sort the seed by dependency
   — parents first.
2. **Stale auto-generated PK.** A child row hardcodes a parent's
   auto-generated ID from a previous run. **Prevention:** use
   `INSERT ... SELECT (SELECT id FROM parent WHERE business_key =
   ...)` patterns, or the migration tool's native ID-lookup.
3. **Composite-PK collision.** Two rows insert into a composite-PK
   table with the same key tuple. **Prevention:** the dataset plan
   must list every composite-PK row explicitly with its key tuple.
4. **Cascade-delete surprise.** A seed re-run deletes child rows
   transitively because the parent was re-inserted. **Prevention:**
   use the migration tool's idempotence guarantee
   (`changeset id` / `find_or_create_by!` / `ON CONFLICT DO NOTHING`)
   rather than DROP + INSERT.

---

## Column-length safety checklist

The single most common seed failure is `Value too long for column
VARCHAR(N)`. Run this checklist before emitting any seed file.

For every textual value you intend to insert:

1. Look up the column's declared length in the schema (entity
   `@Column(length = ...)`, migration `VARCHAR(N)`, model field
   `max_length=N`).
2. Compare to the literal value's character length.
3. If the value exceeds the length, **shorten the value** — do not
   extend the column. The schema is the contract; the seed
   conforms.
4. Pay special attention to small VARCHAR columns: `VARCHAR(10)`,
   `VARCHAR(20)`, `VARCHAR(50)` are common limits on status,
   enum-like, and code columns. Free-text values often exceed them.
5. CHECK constraints with explicit value lists are length-implied;
   the seed value must also be in the allowed set.

---

## Edge / boundary realism

For every column that has a meaningful range, seed at least one row
at each meaningful boundary:

| Column kind | Boundary rows to seed |
|---|---|
| Date in past/future | one near-past, one near-future, one current |
| Numeric amount | one zero, one large positive, one large negative (if allowed) |
| Optional FK | one row with the FK set, one row with it `NULL` (if nullable) |
| Boolean flag | one row `true`, one row `false`, one row `NULL` if tri-state |
| Free-text | one short, one near-max-length |

These boundaries surface formatting / overflow / null-handling bugs
that the happy-path data hides.

---

## Dataset plan template (internal artifact)

Before writing the seed file, the calling agent produces a plan in
this shape. The plan is not a deliverable — it's the reasoning
behind the seed file. Keep it as a comment block in the agent's
output or as a sibling file.

```markdown
# Dataset plan

## Pivot entities
[the 5-slot anchor table from this skill]

## Login users
[the spread table from this skill]

## Per-module row plan
| Bounded context | Tables | Rows | Lifecycle states covered | Notes |
|---|---|---|---|---|
| <bc-1> | <t1, t2, t3> | <n> | <state1, state2, …> | <notes> |
| <bc-2> | <t4, t5> | <n> | <state1, state2> | <notes> |

## Cross-module coherence map
- pivot <alias> → <bc-1>.<table>.<column> → <bc-2>.<table>.<column>
- pivot <alias> → …

## Column-length pre-check
| Table.column | Length | Worst-case literal | Pass? |
|---|---|---|---|
| <t>.<c> | VARCHAR(10) | "<value>" (N chars) | ✓ / shorten |

## Gaps / accepted sentinels
- <column> filled with <sentinel> because no Phase 1 mapping
  existed; documented for follow-up.
```

The plan is the gate. Do not emit a seed file until every section
of the plan has been filled.

---

## Examples — reference patterns

### Example: 5-pivot company set (M&A / CRM domain)

| Alias | NDG / ID | VAT / Tax | Country | Profile |
|---|---|---|---|---|
| Acme | 100000001 | IT12345678901 | IT | Large industrial |
| Beta | 100000002 | IT12345678902 | IT | Small logistics |
| Gamma | 100000003 | CH98765432101 | CH | Listed holding |
| Delta | 100000004 | IT11223344501 | IT | Distressed retail |
| Epsilon | 100000005 | IT55667788901 | IT | Tech / SaaS |

### Example: 5-pivot account set (banking domain)

| Alias | Account ID | Currency | Country | Profile |
|---|---|---|---|---|
| Account-A | ACC-001 | EUR | IT | High-balance, active |
| Account-B | ACC-002 | EUR | IT | Low-balance, new |
| Account-C | ACC-003 | CHF | CH | Cross-border |
| Account-D | ACC-004 | EUR | IT | Overdrawn / risk |
| Account-E | ACC-005 | USD | US | Niche / foreign currency |

### Example: 5-pivot device set (IoT domain)

| Alias | Device ID | Type | Status | Profile |
|---|---|---|---|---|
| D-A | DEV-001 | Sensor | ONLINE | Always-on, frequent telemetry |
| D-B | DEV-002 | Gateway | ONLINE | Aggregator |
| D-C | DEV-003 | Sensor | OFFLINE | Recently disconnected |
| D-D | DEV-004 | Actuator | ALERT | In alarm state |
| D-E | DEV-005 | Sensor | DECOMMISSIONED | Terminal state |

The pivot pattern adapts; the *five-slot diversity* and the *stable
ID convention* do not.

---

## Anti-patterns

- **One huge SQL file with no structure.** Group by bounded
  context, prefix with `<NN>-<bc>-seed`, document the order.
- **Per-table seed without a plan.** A seed that fills 30 tables
  with random-looking data but no coherent pivot graph cannot be
  navigated module-to-module — the demo breaks at the second click.
- **Hardcoded auto-generated IDs.** A seed that depends on the parent
  getting `id = 7` because that's what happened last run will fail
  on a fresh DB. Always resolve via lookup.
- **Free-text data in `VARCHAR(10)` columns.** "Closed Q2 2024" in
  a `VARCHAR(10)` status column is 14 chars and fails. See the
  column-length checklist.
- **Empty audit / log tables.** If the schema has audit tables, seed
  at least one row per audited action — empty audit panes look
  broken.
- **Production-mode seeds.** A seed file with no profile gate WILL
  be applied to production by someone. The gate is non-negotiable.
- **Domain values from another project.** Carrying over
  company names / VAT codes / NDGs from a previous engagement
  contaminates the new project's data. Always derive the dataset's
  *shape* from this project's schema and *values* from generic
  anodyne placeholders.
