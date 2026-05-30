# TO-BE Refactoring Supervisor — Protocol

Read this document during supervision steps. It contains: escalation triggers,
decision rules, inverse drift check, manifest update rules, and hard constraints.
Do not preemptively load — read on demand when a supervision decision is needed.

---

## Pipeline state

**File**: `.refactoring-kb/_meta/pipeline-state.yaml`

> Note: `refactoring-tobe-supervisor` is a legacy agent. In the current v3 workflow, `refactoring-supervisor` drives Phase 4 directly. This state schema applies only when running the legacy big-bang flow.

### Bootstrap protocol
1. Check if `pipeline-state.yaml` exists.
   - Missing → first run; create before dispatching Wave 1.
   - `status: complete` → ask user: skip / re-run / revise.
   - `status: in-progress` → resume from first incomplete wave.

### Update protocol
Write `pipeline-state.yaml` after each wave.

### Schema
```yaml
phase: "Phase 4 — TO-BE Refactoring (legacy)"
use_case: "application-replatforming"
run_id: "<uuid>"
started_at: "<ISO 8601>"
last_updated_at: "<ISO 8601>"
status: "in-progress"
waves:
  W1:
    status: pending
    agents:
      - { name: decomposition-architect, status: pending, output: docs/refactoring/01-bounded-contexts.md }
  W2:
    status: pending
    agents:
      - { name: api-contract-designer, status: pending, output: docs/refactoring/api/openapi.yaml }
  W3:
    status: pending
    agents:
      - { name: backend-scaffolder, status: pending, output: backend/ }
      - { name: data-mapper,        status: pending, output: backend/src/main/resources/ }
      - { name: logic-translator,   status: pending, output: backend/src/main/java/ }   # fan-out
      - { name: frontend-scaffolder, status: pending, output: frontend/ }
  W4:
    status: pending
    agents:
      - { name: hardening-architect, status: pending, output: backend/src/main/resources/application.yml }
  W5:
    status: pending
    agents:
      - { name: migration-roadmap-builder, status: pending, output: docs/refactoring/migration-roadmap.md }
  W6:
    status: pending
    agents:
      - { name: phase4-challenger, status: pending, output: docs/refactoring/_meta/challenger-report.md }
```

---

## Escalation triggers — always ask the user

- Any of Phase 0–3 missing or `failed`
- Phase 3 has unresolved `critical` AS-IS bugs (Phase 4 cannot proceed
  without explicit deferral decision)
- Existing `.refactoring-kb/`, `backend/`, or `frontend/` with content →
  explicit overwrite confirmation required
- ADR-001 or ADR-002 produced by `decomposition-architect` conflicts
  with existing project constraints (e.g., user has stated "monolith
  required" but worker proposes microservices) → escalate before W2
- OpenAPI spectral validation fails → escalate before W3
- `mvn compile` or `ng build` fails (verify policy on) → escalate before W4
- Challenger reports `≥ 1 blocking` issue (especially: orphan UCs,
  AS-IS-only leak, OpenAPI↔code drift) → block Phase 4 completion
- Worker fails twice on the same input → do not retry; escalate
- AS-IS source modification proposed by any worker → block immediately;
  AS-IS code is read-only

---

## Decision rules

| Situation | Decision |
|---|---|
| Phase 0 confirmation not given | Do not dispatch any worker |
| Phase 0/1/2/3 missing | Stop; ask user to run them first |
| Phase 3 has critical AS-IS bugs unresolved | Stop; ask deferral or pause |
| User asks to skip W1 | Refuse — decomposition is non-negotiable |
| User asks to skip W2 (OpenAPI) | Refuse — contract drives W3 |
| TO-BE refactoring already complete (manifest=complete on disk) | Detect as `complete-eligible`; ask user explicitly: skip / re-run / revise. Default recommendation: `skip` (re-running overwrites generated code that may have been hand-edited). |
| TO-BE outputs exist but manifest=partial/failed/in-progress/missing | Detect as `resume-incomplete`; recommend `re-run`; user may override with `revise` |
| Existing TO-BE artifacts | Ask: overwrite / rename / abort |
| `--verify auto` and env not ready | Switch to OFF with warning |
| `mvn compile` fails | Stop W3, escalate to user |
| `ng build` fails | Stop W3, escalate to user |
| Code-reviewer reports blocking issues (sync mode) | Stop, escalate |
| Code-reviewer reports blocking issues (background mode) | Surface in recap, do not block automatically |
| Iteration mode B selected: BC fails | Continue with next BC; flag failed BC in unresolved |
| Worker fails twice | Do not retry; escalate |
| Challenger reports orphan UC | Block Phase 4; surface mapping gap |
| AS-IS source modification detected | Block immediately; verify and revert |

---

## Drift check — INVERSE direction

In Phases 0–3 the drift check forbade target-tech tokens. **In Phase 4 this
rule is inverted.** Target tech is now expected. The new drift to prevent is:

1. **AS-IS-only leak in TO-BE design**: a worker referencing a Streamlit
   primitive (`st.session_state`, `st.cache_data`, `AppTest`) without a
   resolution path through ADR. Such references must be either:
   - resolved (e.g., "session_state → server-side session via Spring Session, see ADR-003")
   - flagged as TODO with explicit ADR ref
   Bare AS-IS technology mention in TO-BE design is `blocking`.

2. **Orphan TO-BE files**: a Java class or Angular component that does not
   implement any UC-NN from Phase 1. Either it's infrastructure (acceptable,
   but must be documented as such) or it's invented scope (block).

3. **Orphan UCs**: a UC-NN from Phase 1 with no TO-BE counterpart. Either
   intentionally descoped (must be in roadmap with rationale) or a coverage
   gap (block).

The challenger runs all three checks formally. Workers also self-check via the
`related_ucs` and `related_bcs` frontmatter fields they're required to fill.

---

## Manifest update

After every wave, update **both** manifests
(`.refactoring-kb/_meta/manifest.json` and
`docs/refactoring/_meta/manifest.json`) — never half-update, never delete prior
entries. Write the entry even on `failed` status.

→ Read [`manifest-schema.md`](manifest-schema.md) for the full schema (common
fields + Phase-4-specific: `resume_mode`, `iteration_model`, `code_scope`,
`verify_policy`, `verify_results`, `traceability_coverage`,
`as_is_bugs_deferred`).

---

## Constraints

- **AS-IS source is READ-ONLY**. Never modify any AS-IS file. Workers that
  produce TO-BE code must write only under `backend/`, `frontend/`,
  `docs/refactoring/`, `.refactoring-kb/`, or `docs/adr/`.
- **Phases 0–3 outputs are READ-ONLY**. Never modify `.indexing-kb/`,
  `docs/analysis/01-functional/`, `docs/analysis/02-technical/`,
  `docs/analysis/03-baseline/`, or `tests/baseline/`.
- **Strict dependency chain**:
  - W1 must complete and HITL CHECKPOINT 1 must be confirmed before W2
  - W2 must complete and HITL CHECKPOINT 2 must be confirmed before W3
  - W3 must complete (with verify pass per policy) and HITL CHECKPOINT 3
    must be confirmed before W4
  - W4 → W5 → W6 are sequential
- **Inverse drift rule**: target tech allowed; AS-IS-only leaks forbidden
  without ADR resolution.
- **Traceability mandatory**: every TO-BE artifact must declare its UC-NN(s)
  and BC. Orphan files trigger challenger blocking finding.
- **Always read worker outputs from disk** after dispatch.
- **Always update both manifests** after each wave.
- **Never silently overwrite** TO-BE artifacts.
- **Never auto-retry** on critical/high failures.
