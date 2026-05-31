# Refactoring Supervisor — Protocol Reference

Read this document at bootstrap start, before any escalation or HITL prompt,
and whenever consulting the workflow phase map or output format rules.

---

## Pipeline state

The `refactoring-supervisor` uses a different state mechanism from the phase supervisors: `docs/refactoring/workflow-manifest.json` (schema in `workflow-manifest-spec.md`). This is intentional — Phase 4 is driven directly by this supervisor across multiple sub-sessions, and the manifest tracks fine-grained per-step state.

**File**: `docs/refactoring/workflow-manifest.json`

### Bootstrap protocol
1. Read `workflow-manifest-spec.md` for the full schema.
2. Check if `workflow-manifest.json` exists:
   - Missing → first run; create before dispatching Phase 0.
   - Exists → read `phases[]` entries to determine which phases are `complete`, `in-progress`, or `pending`. Ask user per-phase: skip / re-run / revise / regenerate-exports (never auto-skip silently).
3. For Phase 4: read `phase4.steps[]` to detect the current step and resume from the first non-`complete` step.

### Update protocol
Update `workflow-manifest.json` after every phase completion AND after every Phase 4 step completion. Fields to update: `status`, `completed_at`, `execution_time_ms`, `outputs`.

### Note on phase supervisors
Phases 0–3 each maintain their own `_meta/pipeline-state.yaml` (see their respective `supervisor-protocol.md`). The `workflow-manifest.json` is the top-level index; the phase-level `pipeline-state.yaml` is the detail.

---

## Phase 4 invariants (BootSmokeTest)

Every Step 2 feature iteration MUST pass `BootSmokeTest` (`@SpringBootTest`, no `@ActiveProfiles`) before the supervisor advances to the next feature. This catches default-profile wiring regressions that profile-scoped tests mask — the canonical example is the InfoSync 2026-05 regression where `mvn test` reported 177/177 pass while `java -jar target/*.jar` crashed with a missing repository bean.

- Gate applies at the END of each Step 2 iteration, before marking the feature complete.
- Gate also applies at Step 0 (Bootstrap hard gate) and at every Step 3 Mandatory Validation sub-loop.
- A failing BootSmokeTest stops forward progress immediately; enter Step 3 sub-loop; never defer.

Full Phase 4 gate table in `decision-rules.md`.

---

## Workflow phases

| Phase | Name | Supervisor | Output root | Status |
|---|---|---|---|---|
| 0 | Codebase Indexing | `indexing-supervisor` | `.indexing-kb/` | implemented |
| 1 | AS-IS Functional Analysis | `functional-analysis-supervisor` | `docs/analysis/01-functional/` | implemented |
| 2 | AS-IS Technical Analysis | `technical-analysis-supervisor` | `docs/analysis/02-technical/` | implemented |
| 3 | AS-IS Baseline Testing | `baseline-testing-supervisor` | `tests/baseline/` + `docs/analysis/03-baseline/` | implemented |
| 4 | Application Replatforming | this agent (drives 7-step loop directly) | `docs/refactoring/` + `backend/` + `frontend/` + `e2e/` | implemented |

**Phase outputs (highlights).** Phase 0 produces a Bronze/Silver/Gold KB plus `evidence-ledger.jsonl` and a `graph/` context graph (canonical stack path: `.indexing-kb/bronze/stack.json`). Phase 1 and Phase 2 produce `normalized/` JSONL alongside the markdown (`use-case-candidates.jsonl`, `feature-candidates.jsonl`, `technical-findings.jsonl`, `risk-register.jsonl`, plus audit verdicts). **Phase 4 must consume normalized JSONL**, not narrative markdown alone, and must NOT treat `candidate_not_confirmed` UCs as certain requirements.

**No Phase 5.** The previous Phase 5 (TO-BE Testing & Equivalence Verification) has been absorbed into Phase 4 Step 6 in v3.0.0. If the user references "Phase 5", clarify that the workflow now ends at Phase 4 and final validation is Step 6.

**Unimplemented phases** (go-live automation, post-launch monitoring, performance tuning loops, deprecation of AS-IS). Respond: "Phase N is not yet implemented. Currently supported: Phase 0–4." Do not invent content for unsupported phases. Do not silently extend scope.

---

## Escalation triggers — always ask the user

- **Bootstrap, pre-phase, post-phase**: always.
- **Mid-phase**: never — phase supervisors own their mid-phase HITL.
- **Phase failure**: always; offer `iterate`/`revise` or `stop`, never auto-retry.
- **Unimplemented phase requested**: refuse and clarify.
- **Output-paths conflict** with existing files: confirm before allowing overwrite.

---

## Output format for user-facing messages

Keep updates terse between protocol steps. The verbose blocks are the pre-phase brief and the post-phase recap (templates in `per-phase-protocol.md`) — those are shown verbatim. Anything outside of those should be one to three lines.
