# Baseline Testing Supervisor — Protocol Reference

Operational content extracted from the supervisor body.
Read this doc at bootstrap start, before any escalation or decision, and when consulting constraints.

---

## Pipeline state

**File**: `tests/baseline/_meta/pipeline-state.yaml`

### Bootstrap protocol
1. Check if `pipeline-state.yaml` exists.
   - Missing → first run; create before dispatching Wave 0.
   - `status: complete` → ask user: skip / re-run / revise. Default: skip.
   - `status: in-progress` → resume from first incomplete wave.
2. Adaptive execution policy: detect `pytest` availability at bootstrap and write `execute_policy: execute` or `execute_policy: write-only` into the state file.

### Update protocol
Write `pipeline-state.yaml` after each wave. Record `execute_policy` so resume runs use the same mode.

### Schema
```yaml
phase: "Phase 3 — Baseline Testing"
use_case: "application-replatforming"
run_id: "<uuid>"
started_at: "<ISO 8601>"
last_updated_at: "<ISO 8601>"
status: "in-progress"
execute_policy: "execute"   # execute | write-only
waves:
  W0:
    status: pending
    agents:
      - { name: fixture-builder, status: pending, output: tests/baseline/conftest.py }
  W1:
    status: pending
    agents:
      - { name: usecase-test-writer, status: pending, output: "tests/baseline/test_uc_<id>.py" }   # fan-out
      - { name: integration-test-writer, status: pending, output: tests/baseline/test_integration.py }
      - { name: benchmark-writer, status: pending, output: tests/baseline/benchmarks/ }
      - { name: service-collection-builder, status: skipped, output: null }   # conditional
  W2:
    status: pending
    agents:
      - { name: baseline-runner, status: pending, output: tests/baseline/_meta/oracle/ }
  W3:
    status: pending
    agents:
      - { name: baseline-challenger, status: pending, output: tests/baseline/_meta/challenger-report.md }
```

---

## Inputs

- **Required source of truth (KB)**: `<repo>/.indexing-kb/` (Phase 0)
- **Required Phase 1**: `<repo>/docs/analysis/01-functional/` — use cases
  drive the test fan-out (one worker per UC)
- **Required Phase 2**: `<repo>/docs/analysis/02-technical/` —
  integrations, performance hotspots, service inventory
- Optional: prior partial outputs in `tests/baseline/` and
  `docs/analysis/03-baseline/` (resume support)
- Optional dispatch flag: `--mode parallel | batched | sequential | auto`
  (default `auto`)
- Optional execution flag: `--execute on | off | auto` (default `auto`)

If Phase 1 or Phase 2 outputs are missing or `status: failed`, **stop and
ask the user**:
- offer to run the missing phases first;
- or proceed with degraded coverage and clearly flag the gap;
- or abort.

Never invent a knowledge base. Workers read from disk via Read/Glob.

---

## Escalation triggers — always ask the user

- Phase 1 or Phase 2 outputs missing or `failed`
- Existing `tests/baseline/` or oracle artifacts (`snapshot/`, benchmark
  JSON) → explicit overwrite confirmation required
- Environment cannot run pytest in `--execute auto` mode → confirm
  fallback to write-only
- `baseline-runner` reports `critical` or `high` failures → escalate
  with full bug context
- `baseline-challenger` reports `≥ 1 blocking` issue
- Worker fails twice on the same UC → do not retry; escalate
- > 50 UCs detected → ask for prioritization (top-N by complexity from
  Phase 1)
- > 5 unresolved questions in any single wave
- Service detection ambiguous → ask if Postman collection should be
  generated
- AS-IS code modification proposed by any worker → block immediately;
  the rule "never fix AS-IS source" is non-negotiable

---

## Decision rules

| Situation | Decision |
|---|---|
| Phase 0 confirmation not given | Do not dispatch any worker |
| Phase 1 / Phase 2 missing | Stop; ask user |
| Streamlit detected | Inject AppTest hints in usecase-test-writer prompt |
| Baseline already complete (manifest=complete on disk) | Detect as `complete-eligible`; ask user explicitly: skip / re-run / revise. Default recommendation: `skip` (oracle is precious — re-running resets the equivalence reference for Phase 5). |
| Baseline outputs exist but manifest=partial/failed/missing | Detect as `resume-incomplete`; recommend `re-run`; user may override with `revise` |
| Existing oracle artifacts | Ask: overwrite / keep / rename (timestamp suffix) |
| `--execute auto` and env not ready | Switch to write-only with warning; ask user |
| `--execute on` and pytest install fails | Fall back to write-only; warn |
| Test failure with severity = critical | Stop, escalate, do not declare complete |
| Test failure with severity = high | Escalate; default to xfail with bug note (user confirms) |
| Test failure with severity = medium / low | Mark xfail with reason; continue |
| Flaky / env-related failure | Mark skip; document; continue |
| Worker proposes AS-IS source change | Reject; never fix AS-IS; flag worker output |
| Service detection: yes | service-collection-builder ON |
| Service detection: no | OFF; note in bootstrap |
| Service detection: ambiguous | Ask user |
| Worker fails twice | Do not retry; escalate |
| > 50 UCs | Ask user for prioritization |
| `Resume mode: iterate` (re-dispatched by refactoring-supervisor with a delta) | Read `_meta/iteration-log.jsonl` latest entry; snapshot prior outputs to `_meta/snapshots/iter-<K>/`; re-dispatch only the workers impacted by the delta per § "Wave 4" mapping in `phase-plan.md`; always re-run Wave 2 (baseline-runner) + Wave 3b (verification report) |
| Iteration delta contains a debate trigger (lexicon match ≥ 0.7) OR a contested test disposition (xfail vs blocking) | Route the contested adjustment through `deliberative-decision-engine` BEFORE re-dispatching the workers; record trace ID in the iteration-log entry |
| Verification report at `_meta/phase-verification-report.md` cannot be produced (missing manifest / bug register) | Do NOT exit to the HITL gate; surface as a blocking error |

---

## Manifest update

After every wave, update `docs/analysis/03-baseline/_meta/manifest.json`.
For the full schema, field rules, timing computation, and update cadence,
see [`manifest-schema.md`](manifest-schema.md).

Hard rules — applied on every update:

- Always populate `started_at` / `completed_at` / `duration_seconds` from
  ISO-8601 timestamps; never approximate.
- After W2, populate `test_results.{passed, xfail, skipped, failed_unresolved}`
  and `as_is_bugs_{critical,high,medium,low}` from `as-is-bugs-found.md`.
- `failed_unresolved` must be `0` at completion — non-zero means the
  supervisor stopped on a critical/high failure pending user triage.
- If a wave is partial or failed, still write the block with `status`
  reflecting the outcome — never omit.

---

## Constraints

- **Strictly AS-IS**. Tests target Python + pytest. Never reference
  target technologies. Drift check after every wave.
- **AS-IS source is read-only**. Never modify production code, even to
  fix a baseline-test failure. The fix cycle for AS-IS bugs is OUT OF
  SCOPE for Phase 3.
- **`.indexing-kb/`, Phase 1, and Phase 2 are the source of truth**.
  Workers may read source code only for narrow patterns explicitly
  allowed in their role.
- **Never invent tests**. If the spec is ambiguous, mark `needs-review`
  with a `## Open questions` entry. The user is the oracle of last
  resort.
- **Never invoke yourself recursively**.
- **Never let a worker write outside `tests/baseline/` or
  `docs/analysis/03-baseline/`**. Verify after each dispatch.
- **Always read worker outputs from disk** — Agent tool result text is
  a summary, not the source of truth.
- **Always update `_meta/manifest.json`** after each wave with timing
  fields populated.
- **Never silently overwrite oracle artifacts** (snapshots, benchmark
  JSON) — explicit user confirmation required.
- **Never skip the failure policy** — every red test gets a disposition
  per Q2.
- **Never auto-retry critical/high failures** — escalate to user.
- **Redact secrets** in any output you produce or any error you echo.
- **All file content output via `Write`** (or `Edit` for in-place
  changes), never via `Bash` heredoc / echo redirect / `tee` /
  `printf > file`. Markdown and Python text containing `[`, `{`, `}`,
  `>`, `<`, `*` are unsafe through the shell. Ref: Phase 2 incident
  2026-04-28. This rule MUST be propagated to every sub-agent dispatch
  prompt (the template already includes it — verify on every dispatch).
- **Wave 3b (verification report) is always ON**: The supervisor writes `_meta/phase-verification-report.md` directly per the canonical structure in `../refactoring-workflow/phase-verification-report.md`. This is the document the human reads before the iteration-loop prompt. Skipping it is a hard error.
- **Iteration loop is owned by `refactoring-supervisor`.** This supervisor does NOT prompt the user with `approve / iterate / stop`. After Wave 3b it returns control to the workflow supervisor, which presents the prompt and re-dispatches this supervisor with `Resume mode: iterate` when needed.
- **Snapshot before overwrite on iterate.** When re-dispatched in `Resume mode: iterate`, snapshot every file that will be regenerated to `_meta/snapshots/iter-<K>/` BEFORE the workers run. Particular care for the oracle (`oracle/snapshot/`): never overwrite without snapshotting first.
- **Oracle is the precious artifact.** When the user iterates on Phase 3, the supervisor must explicitly warn if a re-dispatch will regenerate the oracle snapshot — the oracle is the Phase 4 equivalence reference and silently regenerating it changes the meaning of equivalence. Require explicit user confirmation in the iteration delta if the adjustment touches oracle scope.
