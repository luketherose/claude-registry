---
doc: supervisor-protocol
scope: technical-analysis-supervisor
---

# Technical Analysis Supervisor: Protocol Reference

Read this document: at Phase 0 bootstrap start; before any escalation decision; before
applying any decision rule; as constraints reference throughout execution.

---

## Contents

- [Pipeline state](#pipeline-state): the `pipeline-state.yaml` file, its bootstrap and update protocol, and its schema.
- [Inputs](#inputs): the `.indexing-kb/` source of truth and the Phase 1 cross-reference.
- [Escalation triggers: always ask the user](#escalation-triggers-always-ask-the-user): the conditions that stop the supervisor, starting with an absent or incomplete KB.
- [Decision rules](#decision-rules): the situation by decision table applied without asking.
- [Manifest update](#manifest-update): what to update after every wave, and where the manifest schema lives.
- [Constraints](#constraints): the non-negotiables, above all that no output may reference a target technology.

## Pipeline state

**File**: `docs/analysis/02-technical/_meta/pipeline-state.yaml`

### Bootstrap protocol
1. Check if `pipeline-state.yaml` exists.
   - Missing → first run; create it before dispatching Wave 1.
   - `status: complete` → ask user: skip / re-run / revise / regenerate-exports.
   - `status: in-progress` → resume from first incomplete wave.
2. On `Resume mode: iterate`: increment `iteration`, snapshot prior outputs before re-dispatch.

### Update protocol
Write `pipeline-state.yaml` after each wave. Use it to skip already-complete waves on resume.

### Schema
```yaml
phase: "Phase 2 — Technical Analysis"
use_case: "application-replatforming"
run_id: "<uuid>"
started_at: "<ISO 8601>"
last_updated_at: "<ISO 8601>"
status: "in-progress"
iteration: 1
waves:
  W1:
    status: pending
    agents:
      - { name: code-quality-analyst,        status: pending, output: docs/analysis/02-technical/raw/01-code-quality.md }
      - { name: state-runtime-analyst,       status: pending, output: docs/analysis/02-technical/raw/02-state-runtime.md }
      - { name: dependency-security-analyst, status: pending, output: docs/analysis/02-technical/raw/03-dependency-security.md }
      - { name: data-access-analyst,         status: pending, output: docs/analysis/02-technical/raw/04-data-access.md }
      - { name: integration-analyst,         status: pending, output: docs/analysis/02-technical/raw/05-integration.md }
      - { name: performance-analyst,         status: pending, output: docs/analysis/02-technical/raw/06-performance.md }
      - { name: resilience-analyst,          status: pending, output: docs/analysis/02-technical/raw/07-resilience.md }
      - { name: security-analyst,            status: pending, output: docs/analysis/02-technical/raw/08-security.md }
  W2:
    status: pending
    agents:
      - { name: risk-synthesizer, status: pending, output: docs/analysis/02-technical/risk-register.md }
  W3:
    status: pending
    agents:
      - { name: technical-analysis-challenger, status: pending, output: docs/analysis/02-technical/_meta/challenger-report.md }
      - { name: technical-evidence-auditor,    status: pending, output: docs/analysis/02-technical/_meta/evidence-audit.md }
exports:
  pdf: null
  pptx: null
```

---

## Inputs

- **Required source of truth**: `<repo>/.indexing-kb/` (Phase 0 output).
- **Recommended cross-reference**: `<repo>/docs/analysis/01-functional/`
  (Phase 1 output): used by `risk-synthesizer` to map technical risks
  back to features and use cases.
- **Evidence layer**: `<repo>/.indexing-kb/evidence-ledger.jsonl` (central evidence registry), `<repo>/.indexing-kb/bronze/` (deterministic facts), `<repo>/.indexing-kb/silver/` (agentic extractions with evidence_ids): primary evidence sources for all technical findings.
- Optional: user-provided scope filter (e.g., "skip the migrations folder").
- Optional: prior partial outputs in `docs/analysis/02-technical/` (resume support).
- Optional dispatch flag: `--mode parallel | batched | sequential | auto` (default `auto`).

If `.indexing-kb/` is missing or incomplete, **stop and ask the user**:
- offer to run the indexing pipeline first (Phase 0);
- or proceed with whatever exists (degraded mode), clearly flagging gaps;
- or abort.

If `docs/analysis/01-functional/` is missing, proceed: flag in the recap that
risk-to-feature traceability will be partial.

Never invent a knowledge base. Sub-agents read from `.indexing-kb/`, optionally from
`docs/analysis/01-functional/`, and (only where listed per-agent) from source code for
narrow patterns.

---

## Escalation triggers: always ask the user

Stop and ask before proceeding when:

- **`.indexing-kb/` is absent or incomplete**: never auto-run indexing; ask for permission.
- **Existing exports** in `_exports/`: explicit overwrite confirmation required
  (this is non-negotiable per project policy).
- **Existing `docs/analysis/02-technical/` with `status: complete` files**:
  ask whether to overwrite, augment (only missing sections), or abort.
- **Sub-agent reports > 5 unresolved items in `## Open questions`**.
- **Critical security finding** discovered by `security-analyst`: surface immediately,
  before Wave 2, with a focused summary.
- **Sub-agent fails twice on the same input**: do not retry a third time; escalate.
- **Conflict between sub-agent outputs** that you cannot resolve from the KB.
- **Drift detected** (target-tech reference in any output): block the output, ask the
  responsible worker to revise, escalate if revision fails.
- **Destructive operation suggested by yourself**: e.g., overwriting existing complete
  analysis, deleting `_meta/manifest.json`.

---

## Decision rules

| Situation | Decision |
|---|---|
| Phase 0 confirmation not given | Do not dispatch any sub-agent |
| Streamlit detected | Inject Streamlit instructions in W1 prompts where applicable |
| Phase 1 outputs missing | Proceed; flag risk-to-feature traceability as partial |
| W1 worker fails (foundational: code-quality, dependency-security) | Stop, escalate |
| W1 worker fails (other) | Continue with the rest; flag failure |
| Synthesizer reports orphan findings | Include in unresolved questions, do not auto-resolve |
| Challenger reports ≥ 1 blocking contradiction | Stop, do not declare Phase 2 complete; escalate |
| technical-evidence-auditor verdict is FAIL | Stop, do not declare Phase 2 complete; escalate to user with audit details |
| `.indexing-kb/` partial coverage | Run analysis but mark every output `status: partial` and inherit gaps |
| Resume requested | Read manifest, skip waves with `status: complete`, ask if refresh wanted |
| `Resume mode: iterate` (re-dispatched by refactoring-supervisor with a delta) | Read `_meta/iteration-log.jsonl` latest entry; snapshot prior outputs to `_meta/snapshots/iter-<K>/`; re-dispatch only the workers impacted by the delta per § "Wave 4" mapping in `phase-plan.md`; always re-run Wave 2 (synthesizer) + Wave 3b (auditor) + Wave 3c (verification report) |
| Iteration delta contains a debate trigger (lexicon match ≥ 0.7) OR a contested severity / cross-domain assignment | Route the contested adjustment through `deliberative-decision-engine` BEFORE re-dispatching the worker sub-agents; record trace ID in the iteration-log entry |
| Verification report at `_meta/phase-verification-report.md` cannot be produced (missing manifest / audit file) | Do NOT proceed to Export Wave; surface to user as a blocking error |
| Analysis complete + ≥ 1 export missing | Offer `exports-only` mode (default recommendation); otherwise full-rerun or skip |
| > 100 vulnerabilities reported | Ask user for prioritization; default to top-N by CVSS |
| Export already exists | Ask: overwrite / keep / rename (with timestamp) |
| Document-creator or presentation-creator unavailable | Skip export, flag in recap; do not block Phase 2 |

---

## Manifest update

After every wave, update `docs/analysis/02-technical/_meta/manifest.json` per the schema
in [`output-layout.md`](output-layout.md#manifest-contract-_metamanifestjson). Append to
`runs` for resumed sessions; create the file if missing.

---

## Constraints

- **Strictly AS-IS**. Never reference target technologies, target architectures, TO-BE
  patterns. Drift check after every wave.
- **`.indexing-kb/` is the source of truth**. Sub-agents may descend into source code
  only for narrowly scoped patterns explicitly permitted in their role.
- **Never invent**. If the KB does not support a claim, mark `blocked` and add to
  `14-unresolved-questions.md`.
- **Never write code or refactor source files**.
- **Never invoke yourself recursively**.
- **Never let a sub-agent write outside `docs/analysis/02-technical/`**. Verify after
  each dispatch.
- **Always read sub-agent outputs from disk** after dispatch: the Agent tool result
  text is a summary, not the source of truth.
- **Always update `_meta/manifest.json`** after each wave.
- **Never skip Phase 0 confirmation** unless the user has explicitly authorized
  full-pipeline execution in the same conversation.
- **Aggregate open questions** into `14-unresolved-questions.md` after each wave.
- **Never silently overwrite exports**. Explicit user confirmation is required.
- **Redact secrets** in any output you produce or any error you echo to the user.
  Never quote a connection string with real password.
- **All file content output via `Write`**, never via `Bash` heredoc / echo redirect /
  `tee` / `printf > file`. Mermaid, code blocks, and any text containing `[`, `{`, `}`,
  `>`, `<`, `*` are unsafe to pass through the shell. Reference: Phase 2 incident of
  2026-04-28 (48 accidental files, executed `store` command via redirect). This rule
  MUST be propagated to every sub-agent dispatch prompt (template above already includes
  it, verify on every dispatch).
- **Grounding policy**: All sub-agent prompts must include the grounding policy
  injection. Every technical finding must cite at least one evidence_id from
  evidence-ledger.jsonl. High/critical findings must have evidence_ids AND
  validation.status of verified or requires_validation (never empty). Reference:
  `grounding-policy.md` in docs/indexing/.
- **technical-evidence-auditor is always ON**: Runs in Wave 3b after challenger (or
  after Wave 2 if challenger is disabled).
- **Wave 3c (verification report) is always ON**: The supervisor writes
  `_meta/phase-verification-report.md` directly per the canonical structure in
  `../refactoring-workflow/phase-verification-report.md`. Skipping it is a hard error.
- **Iteration loop is owned by `refactoring-supervisor`.** This supervisor does NOT
  prompt the user with `approve / iterate / stop`. After Wave 3c it returns control to
  the workflow supervisor.
- **Snapshot before overwrite on iterate.** When re-dispatched in `Resume mode: iterate`,
  snapshot every file that will be regenerated to `_meta/snapshots/iter-<K>/` BEFORE the
  workers run.
- **Exports are gated on `approve`.** During iterations 1..N-1 the Export Wave does not
  run. It runs only on `approve` from the iteration loop, or on `Resume mode:
  exports-only` when an approved analysis has missing exports.
