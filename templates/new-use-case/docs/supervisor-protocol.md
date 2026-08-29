# REPLACE-ME Supervisor Protocol

This document contains the operational protocol for `REPLACE-ME-supervisor`:
decision rules, escalation triggers, constraints, and state schema.

---

## Bootstrap dialog

On every invocation:
1. Check for `_meta/pipeline-state.yaml`:
   - If absent → first run; ask user to confirm inputs are ready; create state file.
   - If `status: complete` → ask: skip / re-run / revise.
   - If `status: in-progress` or `status: partial` → resume from first incomplete wave.
2. Verify required inputs exist (list them here).
3. Post the pre-phase brief to the user (what the workflow will do, expected outputs).

---

## Decision rules

| Situation | Decision |
|---|---|
| Required input missing | Stop; ask user to provide before proceeding |
| Wave N worker fails | DESCRIBE-FAILURE-POLICY |
| Worker retried once already | Do not retry; escalate to user |
| Challenger reports blocking issue | Stop; surface to user; do not mark phase complete |
| User requests scope change mid-run | Stop current wave; ask for confirmation; resume |

---

## Escalation triggers — always ask the user

- DESCRIBE-ESCALATION-TRIGGER-1
- DESCRIBE-ESCALATION-TRIGGER-2
- Sub-agent fails twice on the same input.
- Conflict between sub-agent outputs that cannot be resolved from inputs.
- Destructive operation suggested by yourself (e.g., overwriting complete output).

---

## State schema

```yaml
phase: "REPLACE-ME workflow"
use_case: "REPLACE-ME"
run_id: "<uuid>"
started_at: "<ISO 8601>"
last_updated_at: "<ISO 8601>"
status: "in-progress"   # pending | in-progress | complete | partial | failed
waves:
  W1:
    status: pending     # pending | in-progress | complete | failed | skipped
    agents:
      - name: WORKER-NAME
        status: pending
        output: OUTPUT-PATH
```

---

## Constraints

- Never write outside the declared output directory.
- Never invoke yourself recursively.
- Always read sub-agent outputs from disk after dispatch (not from Agent tool result).
- Always update `_meta/pipeline-state.yaml` after each wave.
- All file content output via `Write` tool — never via Bash heredoc / echo redirect.
- Redact credentials in any output or error message.
