# Phase 4 challenger — checklist templates

> Reference doc for `phase4-challenger`. Read at runtime when running the
> nine adversarial checks defined in the agent's `## Method` section.

## Goal

Verbatim per-check matrices and schemas the challenger reuses while
producing findings. The Method section in the agent body decides *what to
check*; this doc carries the *shapes* of the artifacts produced.

---

## Check 1 — AS-IS↔TO-BE traceability matrix

The traceability matrix connects every Phase 1 UC to its TO-BE
manifestation. Build it by following this hierarchy:

```
UC-NN
  └── x-uc-ref operation(s) in openapi.yaml (W2)
        └── controller method in <backend-dir>/.../api/<BC>Controller.java
              └── service method in <backend-dir>/.../application/<Aggregate>Service.java
        └── feature module in <frontend-dir>/.../features/<bc>/
              └── component(s) for screen(s) S-NN that surface this UC
```

For each UC-NN:
- find the operation(s) with matching `x-uc-ref` in openapi.yaml
- find the controller method via the `operationId` in the relevant
  Java file
- find the service method called from the controller
- find the FE component(s) for each S-NN that uses this UC (per
  Phase 1 component-tree.md)

Tag each UC as:
- **fully covered**: all four layers present and linked
- **partially covered**: missing one layer (e.g., no FE component
  because the UC is a backend job per `4.6-api/design-rationale.md`
  documented exception)
- **uncovered**: no TO-BE artifact found

### Matrix JSON schema

Output the matrix at `.refactoring-kb/02-traceability/as-is-to-be-matrix.json`:

```json
{
  "schema_version": "1.0",
  "generated": "<ISO-8601>",
  "agent": "phase4-challenger",
  "use_cases": [
    {
      "uc_id": "UC-01",
      "title": "Register a new user",
      "bc": "BC-01",
      "openapi_operation_id": "createUser",
      "openapi_path": "POST /v1/users",
      "backend_controller": "com.<org>.<app>.identity.api.IdentityController#createUser",
      "backend_service": "com.<org>.<app>.identity.application.UserService#registerUser",
      "frontend_screen": "S-02",
      "frontend_component": "src/app/features/identity/pages/register/register.component.ts",
      "as_is_source": "<repo>/infosync/auth/register.py:48",
      "phase3_test": "tests/baseline/test_uc_01_register.py",
      "phase3_status": "green | xfail-bug-04",
      "translation_status": "full | scaffold-todo | structural | not-started",
      "coverage": "fully_covered | partial | uncovered"
    }
  ],
  "summary": {
    "total_ucs": 0,
    "fully_covered": 0,
    "partial": 0,
    "uncovered": 0
  }
}
```

---

## Check 8 — AS-IS-only token regex

Scan TO-BE outputs (Java / TS / markdown under `<backend-dir>/`,
`<frontend-dir>/`, `docs/refactoring/`) for AS-IS-only token leaks:

```
streamlit | st\.session_state | st\.cache_data | st\.cache_resource |
st\.rerun | st\.experimental_ | AppTest | streamlit\.testing
```

Tokens may legitimately appear in:
- comments referencing AS-IS source (e.g., "AS-IS source ref:
  <repo>/.../streamlit/...")
- ADR resolution notes (e.g., "AS-IS used st.session_state; TO-BE
  uses Spring Session — see ADR-003")

But NOT in:
- runtime code (Java method bodies, TS components without resolution
  context)
- design-doc bodies that aren't comparing AS-IS to TO-BE

---

## Finding shape (every check)

Each finding the challenger emits follows this shape:

- **Type**: gap | drift | orphan | as-is-leak | bug-carry-over |
  perf-hypothesis | security-regression | equivalence | adr-missing |
  source-modified
- **Where**: which file(s) or artifact ID
- **Description**: one paragraph
- **Suggested fix**: short, actionable
- **Severity of meta-finding**: blocking | needs-review | nice-to-have

Stable IDs use the prefix `CHL-NN` for challenger meta-findings.
