# Evals

This directory contains evaluation scenarios for testing capability behavior.

An eval is a documented test case: given a specific input and context, what output
should the capability produce? Evals serve two purposes:

1. **Validation before release**: ensure a new or updated capability behaves as expected
2. **Regression detection**: when a capability is updated, re-run evals to confirm
   existing behaviors are preserved

---

## File naming

`{capability-name}-eval.md`

Examples:
- `software-architect-eval.md`
- `functional-analyst-eval.md`
- `developer-java-spring-eval.md`

---

## Eval file format

```markdown
# Evals: {capability-name}

## Eval-001: {Short scenario title}

**Input context**: {Files to provide, or description of what to ask}

**User prompt**: "{The exact prompt to send to Claude with this subagent active}"

**Expected output characteristics**:
- {Specific thing that must appear in the output}
- {Format that must be followed}
- {Behavior that must be present}

**Must NOT contain**:
- {Anti-patterns to check for}

**How to run**:
1. {Step to set up context if needed}
2. {Invoke the capability}
3. {What to check in the output}

---

## Eval-002: {Next scenario}
...
```

---

## Running evals manually

Evals are currently run manually. There is no automated execution framework.

To run an eval:
1. Open Claude Code in a test directory
2. Copy the capability file to `.claude/agents/`
3. Provide the input context described in the eval
4. Run the prompt and compare output against the expected characteristics

Automated eval execution (using the Claude API's batch evaluation features) is
a future improvement tracked in the backlog.

---

## Coverage expectations

Before a capability can be promoted from beta to stable, it must have:
- At least one eval for the happy path (typical use)
- At least one eval for an edge case or difficult scenario
- At least one eval that would catch a common regression (e.g. forgetting to include
  a required output section)
