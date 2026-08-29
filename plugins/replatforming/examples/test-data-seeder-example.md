# Example: test-data-seeder

The agent is invoked by `refactoring-supervisor` as **Phase 4: Step 5.5
Test Data Seeding**, immediately after Step 5 (Hardening) and immediately
before Step 6 (Final Validation / UI smoke gate). Its job is to make the
freshly-built TO-BE application demoable: the database is empty, every UI
page shows "0 records", and the UI smoke gate cannot meaningfully run.

## Scenario 1: Spring Boot + Liquibase (the typical Java replatform)

**Setup**: A TO-BE backend produced by `developer-java` over Phase 4
Steps 0–5. Stack: Spring Boot 3 + Liquibase + H2 (test profile) /
PostgreSQL (prod). Frontend: Angular. Tests are green (`mvn test` =
PASS, `ng test` = PASS). The application starts but every screen shows
empty grids. The supervisor needs realistic data before the UI smoke
gate.

**Supervisor's dispatch prompt** (abbreviated):

> Run Phase 4: Step 5.5 Test Data Seeding. Repo at
> `<repo>`. Functional spec at `<repo>/docs/analysis/01-functional/`.
> TO-BE under `<repo>/backend/` (Spring Boot 3) and `<repo>/frontend/`
> (Angular). Execution policy: `auto`. UI smoke routes:
> `/customers`, `/orders`, `/audit`, `/reports`, `/admin`. Halt and
> ask if you cannot identify the migration tool.

**What the agent does**:

1. Detects Liquibase from
   `<repo>/backend/src/main/resources/db/changelog/db.changelog-master.yaml`.
2. Reads every entity class under `<repo>/backend/src/main/java/...`
   and extracts the schema (columns, lengths, FKs, enum CHECKs).
3. Reads `<repo>/docs/analysis/01-functional/` for the actor list,
   bounded contexts (Customers, Orders, Audit, Reporting, Admin), and
   the lifecycle states (`ACTIVE`, `INACTIVE`, `LOCKED` for customers;
   `OPEN`, `IN_PROGRESS`, `CLOSED`, `CANCELLED` for orders).
4. Invokes `test-data-seeding-standards` and produces the dataset plan
   (5 pivot customers across 5 profile slots, 4 login users covering
   admin / analyst / multi-role / inactive, one order per state per
   pivot customer, audit rows on every state transition).
5. Invokes `test-data-seeding-standards` for the Liquibase YAML
   template.
6. Runs the column-length pre-check; shortens a draft `additional_notes`
   value from 18 chars to 9 to fit a `VARCHAR(10)` status column it had
   mis-assigned.
7. Writes seed files:
   - `db/changelog/changes/99a-test-seed-customers.yaml`
   - `db/changelog/changes/99b-test-seed-orders.yaml`
   - `db/changelog/changes/99c-test-seed-audit.yaml`
   - `db/changelog/changes/99d-test-seed-users.yaml`
   - `db/changelog/changes/99e-test-seed-reports.yaml`
   Each file is gated `context: test`.
8. Registers each file in `db.changelog-master.yaml`.
9. Extends the in-memory user repository
   (`backend/src/main/java/.../auth/InMemoryUserRepository.java`) so the
   four seeded users can actually log in (password == username).
10. Stops the currently-running backend (`taskkill /F /PID <port-8080-pid>`).
11. Restarts: `mvn -f backend/pom.xml spring-boot:run` and waits for
    `Started`.
12. Smoke-tests via curl:
    - `GET /api/customers` → 5 rows ✓
    - `GET /api/orders` → 16 rows (4 states × ~4 customers) ✓
    - `GET /api/audit/recent` → 22 rows ✓

**Recap returned to the supervisor**:

```markdown
# Test Data Seeding: Recap

## Migration tool detected
Liquibase — backend/src/main/resources/db/changelog/db.changelog-master.yaml

## Seed files written
- backend/src/main/resources/db/changelog/changes/99a-test-seed-customers.yaml (5 rows, context: test)
- backend/src/main/resources/db/changelog/changes/99b-test-seed-orders.yaml (16 rows, context: test)
- backend/src/main/resources/db/changelog/changes/99c-test-seed-audit.yaml (22 rows, context: test)
- backend/src/main/resources/db/changelog/changes/99d-test-seed-users.yaml (4 rows, context: test)
- backend/src/main/resources/db/changelog/changes/99e-test-seed-reports.yaml (3 rows, context: test)

## Auth-store extension
backend/src/main/java/com/<group>/auth/InMemoryUserRepository.java — 4 users added

## Login credentials (test-only)
| user | password | role |
|---|---|---|
| admin | admin | Administrator (all permissions) |
| analyst | analyst | Read-only analyst |
| ops | ops | Multi-role operator |
| inactive | inactive | Locked / inactive (edge state) |

## Pivot entities
| alias | id | name | referenced by |
|---|---|---|---|
| Acme | 1001 | Acme Industries | Customers, Orders, Audit, Reports |
| Beta | 1002 | Beta Logistics | Customers, Orders, Audit |
| Gamma | 1003 | Gamma Holding | Customers, Orders, Reports |
| Delta | 1004 | Delta Retail | Customers, Audit |
| Epsilon | 1005 | Epsilon Tech | Customers, Orders, Reports |

## Per-module row counts
| bounded context | tables seeded | row count |
|---|---|---|
| Customers | customers | 5 |
| Orders | orders, order_items | 16 + 32 |
| Audit | audit_log | 22 |
| Admin | users | 4 |
| Reports | report_snapshots | 3 |

## Restart + smoke verification
- backend start: ok (Started in 20.1 s)
- smoke endpoint /api/customers: 5 rows ✓
- smoke endpoint /api/orders: 16 rows ✓
- smoke endpoint /api/audit/recent: 22 rows ✓

## Caveats / accepted gaps
- customers.tax_code filled with anodyne placeholder "ANON-001..005"
  because no Phase 1 mapping existed for this column.

## Next gate
Step 6 — UI smoke gate may now proceed. The /home route and the
following sample routes will render with non-empty data:
- /customers
- /orders
- /audit
- /reports
- /admin
```

The supervisor takes this recap, posts it to the user, and then proceeds
to Step 6.

---

## Scenario 2: Django + fixtures (Python replatform)

**Setup**: A TO-BE backend produced by `developer-python` for a Django
+ DRF stack. Frontend: Vue. Tests green; `manage.py runserver`
returns empty grids.

**What the agent does**:

1. Detects Django from `manage.py` and `<app>/migrations/` directories.
   No Liquibase, no Flyway.
2. Reads the model files (`<app>/models.py`) to extract field types,
   `max_length=`, and FK targets.
3. Designs the dataset (same 5-pivot principle adapted to the
   project's domain entities).
4. Invokes `test-data-seeding-standards` for the Django fixture
   template.
5. Writes `<app>/fixtures/test_seed.json` per bounded context
   (`customers/fixtures/test_seed.json`,
   `orders/fixtures/test_seed.json`, …).
6. Extends `project/settings/dev.py` to ensure the dev superuser can
   log in.
7. Runs `python manage.py migrate --settings=project.settings.dev &&
   python manage.py loaddata test_seed --settings=project.settings.dev`.
8. Smoke-tests via curl against the DRF endpoints.

The recap follows the same format, only the "Migration tool
detected" and "Seed files written" sections differ. Everything else
(pivot anchor table, credential table, smoke verification, next gate)
is identical because the design principles are stack-agnostic.

---

## Scenario 3: Resume mode after a failed UI smoke

**Setup**: A previous Phase 4 Step 6 run failed the UI smoke gate.
The user reported "every page is empty". The supervisor inspects the
manifest, sees `Step 5.5 = skipped`, and redispatches this agent.

**What the agent does**:

1. Detects the existing seed files (if any): none in this case.
2. Runs the full Method (Steps 1–7).
3. Returns the recap.

The supervisor then redispatches the UI smoke gate.

---

## Scenario 4: Schema-change refresh

**Setup**: A Phase 4 feature loop added a new table
`notification_preferences` after the seed was already written. The
supervisor detects schema drift and redispatches this agent with
flag `--mode refresh`.

**What the agent does**:

1. Reads the existing seed files and the current schema.
2. Computes the diff: `notification_preferences` is unseeded.
3. Writes a new changeset `99f-test-seed-notifications.yaml` (does
   NOT modify the existing changesets, Liquibase tracks them).
4. Restarts and re-verifies.

The recap surfaces only the delta.
