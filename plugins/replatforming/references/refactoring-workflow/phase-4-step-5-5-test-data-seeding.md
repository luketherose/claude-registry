# Phase 4, Step 5.5: Test Data Seeding

> Reference doc for `refactoring-supervisor`. Read at runtime when the
> manifest reports Step 5 (Hardening) complete and Step 6 (Final
> Validation / UI smoke gate) is about to start. This step is the
> bridge that makes Step 6 actually meaningful: the UI smoke gate
> cannot judge an app whose every screen is empty.

## Contents

- [Why this step exists](#why-this-step-exists): an empty database makes a working UI indistinguishable from a broken one.
- [Sub-agent](#sub-agent): a single `test-data-seeder` dispatch, with no wave model.
- [Inputs to the sub-agent](#inputs-to-the-sub-agent): what the supervisor passes to the agent.
- [What the sub-agent produces](#what-the-sub-agent-produces): seed files in whichever migration tool the project already uses.
- [Hard gate](#hard-gate): the gate items that must all hold before Step 6 is unlocked.
- [Pre-Step-5.5 supervisor brief (mandatory user message)](#pre-step-55-supervisor-brief-mandatory-user-message): the brief posted before dispatch, and what the `defer` answer changes.
- [Post-Step-5.5 supervisor recap (mandatory user message)](#post-step-55-supervisor-recap-mandatory-user-message): the recap posted after the agent returns, and what `redispatch` narrows.
- [Manifest update](#manifest-update): the manifest fields written on success, including the credentials Step 6 needs to log in.
- [What this step is NOT](#what-this-step-is-not): what this step is not, above all not fixture loading for the test suite.

## Why this step exists

Phases 4.0 through 4.5 produce a fully-built, fully-tested TO-BE
application, but the runtime database after migrations is empty.
Every UI page shows "0 records", every dashboard reads "No data",
every list is blank. From a human visual standpoint, an empty app
looks identical to a broken app:

- empty grid vs. broken grid renderer
- "No customers" vs. "API endpoint failed"
- blank dashboard vs. routing misconfiguration

The Step 6 UI smoke gate's job is to catch precisely these
**human-perceived** failures, but the gate is meaningless if the
data layer is empty. Step 5.5 produces the small, coherent,
cross-module dataset that turns an empty shell into a navigable
application, without contaminating production and without
introducing logic the test suite hasn't already exercised.

## Sub-agent

This step is driven by exactly one sub-agent: `test-data-seeder`. It
is not orchestrated by a wave model: Step 5.5 is a single
dispatch, single recap, single gate.

## Inputs to the sub-agent

The supervisor passes:

- repo root path
- `<repo>/docs/analysis/01-functional/`: actors, use cases, bounded
  contexts, enum values, lifecycle states (the dataset's *shape*
  comes from here)
- `<repo>/docs/refactoring/`: bounded-context decomposition, ADRs,
  OpenAPI contract (drives which endpoints to smoke-test)
- `<repo>/<backend-dir>/`: backend source (drives migration-tool
  detection, schema extraction, optional in-memory auth-store
  extension)
- `<repo>/<frontend-dir>/`: frontend source (only to learn which
  routes Step 6 will exercise)
- the list of UI smoke routes Step 6 will visit
- execution policy: `auto` (default) | `on` | `off`

## What the sub-agent produces

A short set of seed files in whatever migration tool the project
already uses (Liquibase, Flyway, Django fixtures, Rails seeds, EF
Core Data Seeding, Knex, TypeORM, Prisma, sqlx, Diesel, goose,
Alembic, or raw SQL fallback), each gated to a non-production
profile.

Plus, when needed and only for an in-memory dev/test auth store, a
small extension so the seeded login users can actually log in.

Plus a recap message in the canonical format defined by the agent.

## Hard gate

Step 5.5 is complete (and Step 6 entry is unlocked) only when ALL
of the following hold:

| Gate item | Verified by |
|---|---|
| Seed files written and registered in the migration tool's manifest | recap "Seed files written" section |
| Every seed file gated to a non-production profile | recap and agent's self-check |
| Backend restarts successfully with the seed loaded | recap "Restart + smoke verification" |
| At least 3 API smoke calls return non-empty results | recap "smoke endpoint" lines |
| The credentials needed for Step 6 are documented | recap "Login credentials" table |

If `execute_policy` is `off`, the last three items are deferred to
Step 6.1 of the UI smoke gate, but the seed files must still exist
and be registered.

If any gate item fails, the supervisor:

1. Reads the recap's `Halted` section (if present) or the failure
   evidence.
2. If the failure is a transient runtime issue (migration lock,
   wrong profile selected), retries the agent with the corrected
   policy.
3. If the failure is structural (schema cannot accept the seed),
   routes to the **Step 3 debug sub-loop** (root-cause the
   schema / migration / dataset mismatch) before re-attempting
   Step 5.5.

## Pre-Step-5.5 supervisor brief (mandatory user message)

Before dispatching `test-data-seeder`, post this brief to the user:

```
Phase 4 Step 5.5 — Test Data Seeding

Hardening (Step 5) is complete and all automated tests are green.
The application builds, starts, and passes its test suite — but the
database after migrations is empty, so the upcoming UI smoke gate
(Step 6) would judge a blank UI as the worst-case visual result.

About to dispatch `test-data-seeder` to:
  1. detect the project's migration tool (Liquibase / Flyway /
     Django fixtures / Rails seeds / EF Migrations / Knex / TypeORM
     / Prisma / sqlx / Diesel / goose / Alembic / raw SQL),
  2. design a coherent 5-pivot dataset covering every bounded
     context, every documented lifecycle state, and every login
     role variant,
  3. write the seed file(s) gated to the non-production profile,
  4. restart the backend and verify via API smoke calls.

Execution policy: <auto | on | off>.
UI smoke routes Step 6 will visit: <list from manifest>.

  [proceed] [defer — execute_policy=off, write files only]
```

If the user picks `defer`, dispatch the agent with
`execute_policy: off`: the recap will list the files and the
invocation command without restarting the backend.

## Post-Step-5.5 supervisor recap (mandatory user message)

After the agent returns:

```
Phase 4 Step 5.5 — Test Data Seeding result

Migration tool: <tool>
Seed files written: <N> (gated to <profile>)
Per-module row counts:
  <bc-1>: <n> rows  ·  <bc-2>: <n> rows  ·  ...
Login credentials (test-only):
  <u1> / <p1>  ·  <u2> / <p2>  ·  ...
Smoke endpoint results:
  /<x> → <n> rows ✓  ·  /<y> → <n> rows ✓  ·  /<z> → <n> rows ✓

Caveats: <agent's caveats section, verbatim>

  [confirm — proceed to Step 6 UI smoke gate] [redispatch — gaps in <area>]
```

If the user picks `redispatch`, route back to `test-data-seeder`
with a narrowed scope (refresh mode, target module).

## Manifest update

After a successful Step 5.5, write to
`docs/refactoring/_meta/manifest.json`:

```json
{
  "phase4": {
    "step": "5.5",
    "step_5_5": {
      "status": "complete",
      "migration_tool": "<tool>",
      "seed_files": ["<path1>", "<path2>", "..."],
      "pivot_entities": [{"alias": "Acme", "id": "1001", "name": "Acme Industries"}, "..."],
      "login_credentials": [{"username": "admin", "password": "admin", "role": "Administrator"}, "..."],
      "smoke_endpoints_verified": ["/api/customers", "/api/orders", "..."],
      "completed_at": "<iso-timestamp>",
      "duration_sec": <int>
    }
  }
}
```

The credentials block is captured to enable Step 6 to log in
without re-asking the user. **Important**: the manifest is also
gated: `_meta/manifest.json` is a project-local file and is not
intended to ship to production.

## What this step is NOT

- It is NOT a fixture-loading step for the test suite (those live
  next to the tests, in JUnit fixtures / pytest conftest / etc.).
  Step 5.5 produces **runtime** data for a running application.
- It is NOT a production seed. The non-production gate is
  non-negotiable.
- It is NOT a load-generator. Volume is intentionally small:
  coverage over cardinality.
- It is NOT a schema-design step. The seed conforms to whatever
  schema Step 2 / Step 5 produced.
