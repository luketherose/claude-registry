# TO-BE Testing Supervisor: Protocol

> **LEGACY: this supervisor is deprecated in v3 of the replatforming workflow.**
> Equivalence verification is now absorbed into Phase 4 Step 6 of `refactoring-supervisor` v3.
> This document applies only when running the legacy separate Phase 5 flow.

Read this document during supervision steps. It contains: escalation triggers,
decision rules, AS-IS source preservation check, manifest update rules, and
hard constraints. Do not preemptively load. Read on demand when a supervision
decision is needed.

---

## Contents

- [Pipeline state](#pipeline-state): the `pipeline-state.yaml` file, its bootstrap and update protocol, and its schema.
- [Escalation triggers: always ask the user](#escalation-triggers-always-ask-the-user): the conditions that stop the supervisor, including an OpenAPI spec that fails spectral.
- [Decision rules](#decision-rules): the situation by decision table applied without asking.
- [AS-IS source preservation (non-negotiable)](#as-is-source-preservation-non-negotiable): the per-wave command that proves no AS-IS file was touched.
- [Manifest update](#manifest-update): what to update after every wave, and how resumed sessions append.
- [Constraints](#constraints): the non-negotiables: measure, compare and certify, never modify source.

## Pipeline state

**File**: `docs/analysis/05-tobe-tests/_meta/pipeline-state.yaml`

> Note: `tobe-testing-supervisor` is a legacy agent. In the current v3 workflow, equivalence verification is absorbed into Phase 4 Step 6 of `refactoring-supervisor`. This state schema applies only when running the legacy separate Phase 5 flow.

### Bootstrap protocol
1. Check if `pipeline-state.yaml` exists.
   - Missing → first run; create before dispatching Wave 1.
   - `status: complete` → ask user: skip / re-run / revise.
   - `status: in-progress` → resume from first incomplete wave.
2. Detect execution policy at bootstrap (`mvn`, `ng`, `playwright` available → `execute`; else `write-only`). Write into state file.

### Update protocol
Write `pipeline-state.yaml` after each wave.

### Schema
```yaml
phase: "Phase 5 — TO-BE Testing (legacy)"
use_case: "application-replatforming"
run_id: "<uuid>"
started_at: "<ISO 8601>"
last_updated_at: "<ISO 8601>"
status: "in-progress"
execute_policy: "execute"   # execute | write-only
waves:
  W1:
    status: pending
    agents:
      - { name: equivalence-test-writer, status: pending, output: tests/equivalence/ }   # fan-out
      - { name: backend-test-writer,  status: pending, output: backend/src/test/ }
      - { name: frontend-test-writer, status: pending, output: frontend/src/test/ }
      - { name: security-test-writer, status: pending, output: docs/analysis/05-tobe-tests/05-security-findings.md }
  W2:
    status: pending
    agents:
      - { name: performance-comparator, status: pending, output: docs/analysis/05-tobe-tests/04-performance-comparison.md }
  W3:
    status: pending
    agents:
      - { name: tobe-test-runner, status: pending, output: docs/analysis/05-tobe-tests/03-coverage-report.md }
  W4:
    status: pending
    agents:
      - { name: equivalence-synthesizer, status: pending, output: docs/analysis/05-tobe-tests/01-equivalence-report.md }
  W5:
    status: pending
    agents:
      - { name: tobe-testing-challenger, status: pending, output: docs/analysis/05-tobe-tests/_meta/challenger-report.md }
```

---

## Escalation triggers: always ask the user

Stop and ask before proceeding when:

- **Any prior phase incomplete**: never bypass.
- **OpenAPI not spectral-valid**: contract drift will cascade.
- **Existing test files with unclear authorship** (no agent frontmatter): ask
  the user before overwriting: they may have hand-written tests to preserve.
- **`tobe-test-runner` reports critical regression**: surface immediately,
  before Wave 4, with a focused summary.
- **Performance p95 delta > +10%**: surface immediately at Wave 2; recommend
  Phase 4 hardening loop before proceeding.
- **Sub-agent reports > 5 unresolved items in `## Open questions`**.
- **AS-IS source-code modification detected** (forbidden): block, flag as
  blocking, never proceed.
- **TO-BE source-code modification detected** (forbidden in this phase): block,
  flag as blocking, never proceed.
- **Sub-agent fails twice on the same input**: do not retry a third time;
  escalate.
- **Conflict between sub-agent outputs** that you cannot resolve from Phase
  1/3/4 evidence.
- **Destructive operation suggested by yourself**: e.g., overwriting existing
  complete test suite, deleting `_meta/manifest.json`.

---

## Decision rules

| Situation | Decision |
|---|---|
| Phase 0 confirmation not given | Do not dispatch any sub-agent |
| Prior phase manifest reports `partial` | Stop, escalate |
| Phase 5 already complete (manifest=complete) | Detect as `complete-eligible`; ask user explicitly: skip / re-run / revise. Default `skip`. |
| Phase 5 outputs exist but manifest=partial/failed/missing | Detect as `resume-incomplete`; recommend `re-run`; user may override with `revise` |
| W1 worker fails (foundational: equivalence-test-writer, backend-test-writer) | Stop, escalate |
| W1 worker fails (other) | Continue with the rest; flag failure |
| `tobe-test-runner` reports ≥ 1 critical regression | Stop, do not declare Phase 5 complete; escalate |
| `tobe-test-runner` reports ≥ 1 high regression | Continue to W4; flag in equivalence report; PO must sign or block |
| Equivalence-synthesizer reports any UC without disposition | Stop, escalate |
| Challenger reports ≥ 1 blocking contradiction | Stop, do not declare Phase 5 complete; escalate |
| Resume requested | Read manifest, skip waves with `status: complete`, ask if refresh wanted |
| > 100 UCs detected | Ask user for prioritization (critical vs nice-to-have); default to all |
| Contract test fails vs OpenAPI | Critical: escalate; root cause is either Phase 4 drift or OpenAPI spec error |

---

## AS-IS source preservation (non-negotiable)

After every wave, run:

```
git status --porcelain
```

Then verify NO entry under the AS-IS source paths (i.e., the original
Python/Streamlit codebase outside `tests/baseline/`, `tests/equivalence/`,
`backend/`, `frontend/`, `e2e/`, `docs/`) is modified. If any AS-IS file is
dirty: stop, flag as blocking, never auto-revert. The user must confirm whether
the change is intentional or a bug in a worker.

The same check applies to TO-BE source code (`backend/`, `frontend/` non-test
files): in Phase 5 these are read-only. Test files are write-allowed; production
code is not.

---

## Manifest update

After every wave, update `docs/analysis/05-tobe-tests/_meta/manifest.json`. If
the file does not exist, create it; append to `runs` for resumed sessions.
Per-agent timing is mandatory: the workflow supervisor surfaces it in its
post-phase recap.

→ Read [`output-layout.md`](output-layout.md) "Manifest schema" section for the
full JSON schema.

---

## Constraints

- **Strictly TO-BE validation**. You measure, compare, and certify; you do not
  modify TO-BE source code, you do not modify AS-IS source code, you do not
  write production fixes.
- **`tests/baseline/` is the AS-IS oracle**, immutable in this phase.
- **`docs/refactoring/api/openapi.yaml` is the contract**, immutable in this
  phase. Drift between OpenAPI and TO-BE backend is a critical finding, not a
  fix target.
- **AS-IS-bug-carry-over**: bugs deferred from Phase 3 are NOT TO-BE
  regressions; do not flag them. Pass the list to every worker.
- **Never invent baselines**. If Phase 3 is incomplete, stop.
- **Never invoke yourself recursively.**
- **Never let a sub-agent write outside its permitted roots.** Verify after each
  dispatch.
- **Always read sub-agent outputs from disk** after dispatch: the Agent tool
  result text is a summary, not the source of truth.
- **Always update `_meta/manifest.json`** after each wave.
- **Never skip Phase 0 confirmation** unless the user has explicitly authorized
  full-pipeline execution in the same conversation.
- **Aggregate open questions** into `14-unresolved-questions.md` after each wave.
- **Never silently overwrite authored test files**. Explicit user confirmation
  is required.
- **Never commit AS-IS source modifications**. Abort and flag.
- **Never commit TO-BE production code modifications**. Abort and flag (fixes
  belong to a Phase 4 hardening loop).
- **Redact secrets** in any output you produce or any error you echo to the
  user. Never quote a connection string with real password.
