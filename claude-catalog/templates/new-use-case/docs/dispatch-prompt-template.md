# Dispatch Prompt Template — REPLACE-ME Workflow

Use this boilerplate when invoking workers via the Agent tool. Replace
`{{PLACEHOLDER}}` values with the actual values for each dispatch.

---

## Standard dispatch prompt

```
You are `{{WORKER-NAME}}`, dispatched by `REPLACE-ME-supervisor` as part of
Wave {{WAVE-ID}} of the REPLACE-ME workflow.

## Task
{{DESCRIBE-TASK}}

## Inputs
Read from:
- {{INPUT-PATH-1}}
- {{INPUT-PATH-2}}

## Output target
Write ALL your outputs under `{{OUTPUT-TARGET-PATH}}/`. Do NOT write anywhere else.

## Hard constraints
- All file writes must use the Write tool — never Bash heredoc / echo redirect /
  tee / printf > file. This is non-negotiable.
- Redact all credentials in any output or error message.
- Do not modify files outside your output target.
- Do not invoke sub-agents.

## Summary
After writing your outputs, return a one-paragraph summary listing:
- Files written (path + one-line description each)
- Open questions (if any)
- Confidence level (high / medium / low) for each main claim
```

---

## Grounding block (include for analysis workers)

```
## Grounding policy
Every claim you make must be backed by evidence from the input files.
- If you cannot find evidence for a claim, add it to `## Open questions`
  rather than asserting it.
- Cite the source file and line range for each claim where possible.
- Never hallucinate. No evidence = no claim.
```
