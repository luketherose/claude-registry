# Functional Analysis Supervisor: Protocol Reference

This document holds the operational protocol for `functional-analysis-supervisor`. Read it at bootstrap start, before any escalation or decision, before manifest update, and for constraints reference.

---

## Contents

- [Pipeline state](#pipeline-state): the `pipeline-state.yaml` file, its bootstrap and update protocol, and its schema.
- [Inputs](#inputs): the `.indexing-kb/` source of truth and the evidence ledger the phase reads from.
- [Escalation triggers: always ask the user](#escalation-triggers-always-ask-the-user): the conditions that stop the supervisor, starting with an absent or stale KB.
- [Decision rules](#decision-rules): the situation by decision table the supervisor applies without asking.
- [Manifest update](#manifest-update): what to update after every wave, and where the full manifest schema lives.
- [Constraints](#constraints): the non-negotiables, above all that no output may reference a target technology.

## Pipeline state

**File**: `docs/analysis/01-functional/_meta/pipeline-state.yaml`

### Bootstrap protocol
1. Check if `pipeline-state.yaml` exists.
   - Missing → first run; create it with `status: pending` before dispatching Wave 1.
   - `status: complete` → ask user: skip / re-run / revise / regenerate-exports. Never auto-skip.
   - `status: in-progress` or `status: partial` → resume from first incomplete wave.
2. On `Resume mode: iterate` (re-dispatched by refactoring-supervisor): read `iteration` field, increment it, snapshot prior outputs before re-dispatching affected sub-agents.

### Update protocol
Write `pipeline-state.yaml` after each wave completes. Update `iteration` on each iterate-mode re-dispatch.

### Schema
```yaml
phase: "Phase 1 — Functional Analysis"
use_case: "application-replatforming"
run_id: "<uuid>"
started_at: "<ISO 8601>"
last_updated_at: "<ISO 8601>"
status: "in-progress"       # pending | in-progress | complete | partial | failed
iteration: 1                # increments on each iterate-mode re-dispatch
waves:
  W1:
    status: complete
    agents:
      - name: actor-feature-mapper
        status: complete
        output: docs/analysis/01-functional/raw/01-actors-features.md
      - name: ui-surface-analyst
        status: complete
        output: docs/analysis/01-functional/raw/02-ui-surface.md
      - name: io-catalog-analyst
        status: complete
        output: docs/analysis/01-functional/raw/03-io-catalog.md
  W2:
    status: pending
    agents:
      - name: user-flow-analyst
        status: pending
        output: docs/analysis/01-functional/raw/04-user-flows.md
      - name: implicit-logic-analyst
        status: pending
        output: docs/analysis/01-functional/raw/05-implicit-logic.md
  W3:
    status: pending
    agents:
      - name: functional-analysis-challenger
        status: pending        # skipped when not Streamlit and user did not opt in
        output: docs/analysis/01-functional/_meta/challenger-report.md
      - name: functional-traceability-auditor
        status: pending
        output: docs/analysis/01-functional/_meta/traceability-audit.md
exports:
  pdf: null                  # path when generated
  pptx: null
```

---

## Inputs

- **Single source of truth**: `<repo>/.indexing-kb/` (produced by Phase 0
  indexing pipeline).
- **Evidence layer**: `<repo>/.indexing-kb/evidence-ledger.jsonl` (central evidence registry), `<repo>/.indexing-kb/bronze/` (deterministic facts), `<repo>/.indexing-kb/silver/` (agentic extractions with evidence_ids): primary evidence sources for all sub-agent claims.
- Optional: user-provided scope filter (e.g., "focus on the billing module").
- Optional: prior partial outputs in `docs/analysis/01-functional/` (resume
  support).

If `.indexing-kb/` is missing or incomplete, **stop and ask the user**:
- offer to run the indexing pipeline first;
- or proceed with whatever exists (degraded mode), clearly flagging gaps;
- or abort.

Never invent a knowledge base. Never read source code as a substitute for
the KB at this stage. Only the `implicit-logic-analyst` is allowed to
descend into source code, and only for narrowly scoped patterns the KB
cannot cover.

---

## Escalation triggers: always ask the user

Stop and ask before proceeding when:

- **`.indexing-kb/` is absent or incomplete**: never auto-run indexing;
  ask for permission.
- **`.indexing-kb/` says `status: needs-review` on its own index**: warn
  the user that downstream analysis will inherit the uncertainty.
- **Stack mode unclear**: ask explicitly (Streamlit? web app? CLI?
  library? hybrid?).
- **Existing `docs/analysis/01-functional/` with `status: complete` files**:
  ask whether to overwrite, augment (only missing sections), or abort.
- **Existing exports** in `_exports/` (PDF or PPTX): explicit overwrite
  confirmation required (this is non-negotiable, same policy as Phase 2).
- **Sub-agent reports > 5 unresolved items in `## Open questions`**.
- **Scope expansion mid-run**: a sub-agent identifies significant
  functional surface outside the initially confirmed scope (e.g., a
  hidden admin panel, a CLI not mentioned in the KB). Confirm whether
  to extend.
- **Sub-agent fails twice on the same input**: do not retry a third time
escalate.
- **Conflict between sub-agent outputs** that you cannot resolve from
  the KB (e.g., actor list says only "user", but UC analysis discovers
  flows requiring an admin role).
- **Destructive operation suggested by yourself**: e.g., overwriting an
  existing complete analysis, deleting `_meta/manifest.json`.

---

## Decision rules

| Situation | Decision |
|---|---|
| Phase 0 confirmation not given | Do not dispatch any sub-agent |
| Streamlit detected | Inject Streamlit-specific instructions in W1+W2 prompts; default challenger ON |
| Streamlit not detected, stack unclear | Ask user; do not assume web app |
| W1 sub-agent fails | If foundational (actor-feature-mapper, ui-surface-analyst), stop. If io-catalog-analyst, proceed but flag |
| W2 sub-agent fails | Continue with the other; flag failure |
| Challenger reports ≥ 1 blocking contradiction | Stop, do not declare Phase 1 complete; escalate |
| functional-traceability-auditor verdict is FAIL | Stop, do not declare Phase 1 complete; escalate to user with audit details |
| `.indexing-kb/` partial coverage | Run analysis but mark every output `status: partial` and inherit the gaps |
| Resume requested | Read manifest, skip waves with `status: complete`, ask user if a refresh is wanted |
| `Resume mode: iterate` (re-dispatched by refactoring-supervisor with a delta) | Read `_meta/iteration-log.jsonl` latest entry; snapshot prior outputs to `_meta/snapshots/iter-<K>/`; re-dispatch only the sub-agents impacted by the delta per the mapping in `phase-plan.md` § "Wave 4"; always re-run Wave 3 synthesis + Wave 3b auditor + Wave 3c narrative + Wave 3d verification report |
| Iteration delta contains a debate trigger (lexicon match ≥ 0.7) OR a contested adjustment vs prior sub-agent output | Route the contested adjustment through `deliberative-decision-engine` BEFORE re-dispatching the worker sub-agents; record the trace ID in the iteration-log entry |
| Wave 3c (narrative) cannot be produced because the supervisor lacks inputs | Mark phase status `partial`; surface in the verification report's section 2 with a clear gap entry; do NOT silently skip |
| Verification report `recommendation` is `iterate` and user picks `approve` | The supervisor still runs the Export Wave; the workflow supervisor handles the `--override` flow per the per-phase protocol |
| Analysis complete + ≥ 1 export missing | Offer `exports-only` mode (default recommendation); otherwise full-rerun or skip |
| > 50 screens or > 30 UCs detected | Ask user for prioritization; default to top-N by complexity |
| Export already exists | Ask: overwrite / keep / rename (with timestamp) |
| `document-creator` or `presentation-creator` unavailable | Skip export, flag in recap; do not block Phase 1 |

---

## Manifest update

After every wave, update `docs/analysis/01-functional/_meta/manifest.json`. For the full schema (fields, run/wave structure), see the `Manifest schema` section of [`output-layout.md`](output-layout.md). If the file does not exist, create it. Append to `runs` for resumed sessions.

---

## Constraints

- **Strictly AS-IS**. Never reference target technologies, target
  architectures, TO-BE patterns, or "how this would map to <X>". If a
  sub-agent output contains target-tech references, flag it as
  `needs-review` and ask the sub-agent to revise.
- **`.indexing-kb/` is the source of truth**. Never read source code
  yourself; sub-agents (specifically `implicit-logic-analyst`) may
  descend into source code only for narrowly scoped patterns.
- **Never invent**. If the KB does not support a claim, mark `blocked`
  and add to `14-unresolved-questions.md`.
- **Never write code or refactor source files**.
- **Never invoke yourself recursively**.
- **Never let a sub-agent write outside `docs/analysis/01-functional/`**.
  Verify after each dispatch.
- **Always read sub-agent outputs from disk** after dispatch: the
  Agent tool result text is a summary, not the source of truth.
- **Always update `_meta/manifest.json`** after each wave.
- **Never skip Phase 0 confirmation** unless the user has explicitly
  authorized full-pipeline execution in the same conversation.
- **Aggregate open questions** into `14-unresolved-questions.md` after
  Wave 2, then again after challenger (if run).
- **Never silently overwrite exports**. Explicit user confirmation is
  required (same policy as Phase 2).
- **All file content output via `Write`**, never via `Bash` heredoc /
  echo redirect / `tee` / `printf > file`. Mermaid, code blocks, and
  any text containing `[`, `{`, `}`, `>`, `<`, `*` are unsafe to pass
  through the shell. Reference: Phase 2 incident of 2026-04-28
  (48 accidental files, executed `store` command via redirect).
  This rule MUST be propagated to every sub-agent dispatch prompt
  (template above already includes it, verify on every dispatch).
- **Redact secrets** in any output you produce or any error you echo to
  the user. Never quote a connection string with real password.
- **Grounding policy**: All sub-agent prompts must include the grounding policy injection. Sub-agents must cite evidence_ids from evidence-ledger.jsonl for every claim. Never create a use case as "confirmed" without at least one evidence_id. If evidence is missing, create a gap/open question, not a hallucination. Reference: `grounding-policy.md` in docs/indexing/.
- **functional-traceability-auditor is always ON**: It runs in Wave 3b (after challenger if enabled). Do not skip it even if the challenger is disabled.
- **Wave 3c (feature narrative) is always ON**: The supervisor writes `00b-feature-narrative.md` directly (no sub-agent). Plain prose, feature-by-feature chapters, references to stable IDs. Audience is the human reviewer running the workflow. Hard rules in `output-layout.md` § "The feature narrative".
- **Wave 3d (verification report) is always ON**: The supervisor writes `_meta/phase-verification-report.md` directly per the canonical structure in `../refactoring-workflow/phase-verification-report.md`. This is the document the human reads before the iteration-loop prompt. Skipping it is a hard error.
- **Iteration loop is owned by `refactoring-supervisor`.** This supervisor does NOT prompt the user with `approve / iterate / stop`. After Wave 3d it returns control to the workflow supervisor, which presents the prompt and re-dispatches this supervisor with `Resume mode: iterate` when needed.
- **Snapshot before overwrite on iterate.** When re-dispatched in `Resume mode: iterate`, snapshot every file that will be regenerated to `_meta/snapshots/iter-<K>/` BEFORE the sub-agents run. The snapshot is the source of the "What changed since iteration N-1" section of the verification report.
- **Exports are gated on `approve`.** During iterations 1..N-1 the Export Wave does not run. It runs only on `approve` from the iteration loop, or on `Resume mode: exports-only` when an approved analysis has missing exports.
