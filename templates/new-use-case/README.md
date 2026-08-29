# New Use Case — Step-by-Step Guide

This template scaffolds a new workflow use case. A "use case" is a self-contained
workflow module with its own supervisor agent, set of worker agents, reference
docs, and eval suite.

Currently the registry has one use case: **application-replatforming**. This
guide shows how to add a second (e.g., code-audit, documentation-generation,
security-assessment).

---

## Prerequisites

Before starting, decide:
1. **Use case ID** — kebab-case identifier (e.g., `code-audit`)
2. **Name** — human-readable (e.g., "Code Audit Workflow")
3. **Entry point** — which agent the user invokes (usually `<id>-supervisor`)
4. **Phases** — ordered sequence of analysis/work phases
5. **Which shared agents it uses** — from the existing pool (see `bmad/workflows.json` `shared_agents`)

---

## Step 1 — Scaffold the supervisor

```bash
./claude-catalog/scripts/new-capability.sh --type agent <use-case-id>-supervisor
```

Then replace the template body with the contents of
`claude-catalog/templates/new-use-case/supervisor-template.md`.

Key things to set:
- `## Role` — one paragraph describing what the supervisor orchestrates
- `## When to invoke` — 3–4 trigger scenarios + `Do NOT use` line
- `## Reference docs` table — points to `claude-catalog/docs/<use-case-id>/`
- `model: sonnet`
- `tools: Read, Glob, Bash, Agent`
- `color:` — pick one not already used by a sibling supervisor

---

## Step 2 — Create reference docs directory

```bash
mkdir -p claude-catalog/docs/<use-case-id>/
```

Copy from this template:
```
claude-catalog/templates/new-use-case/docs/supervisor-protocol.md → claude-catalog/docs/<use-case-id>/supervisor-protocol.md
claude-catalog/templates/new-use-case/docs/dispatch-prompt-template.md → claude-catalog/docs/<use-case-id>/dispatch-prompt-template.md
```

Then fill in:
- `supervisor-protocol.md` — decision rules, escalation triggers, constraints specific to this use case
- `dispatch-prompt-template.md` — boilerplate prompt text for Agent tool calls

---

## Step 3 — Identify workers

List the workers for each phase/wave of your use case. For each worker decide:
- Is it a **new** agent (write from `worker-template.md`) or a **shared** agent (already exists)?
- What is its output target directory?
- Is it always on, conditional, or fan-out per item?

---

## Step 4 — Scaffold new workers

For each new worker:
```bash
./claude-catalog/scripts/new-capability.sh --type agent <worker-name>
```

Then replace the template body with `worker-template.md` contents.

Workers must:
- Never include the `Agent` tool (workers do not dispatch sub-agents)
- Write only to their declared output directory
- Have `model: sonnet` and file I/O tools only (`Read, Glob, Grep, Bash, Write`)

---

## Step 5 — Add pipeline-state.yaml schema

Each phase of your workflow writes its state to `_meta/pipeline-state.yaml`.
Define the schema in `claude-catalog/docs/<use-case-id>/supervisor-protocol.md`
under a `## State schema` section. Follow the format from
`bmad/design/mapping.md` § "Document-as-cache".

---

## Step 6 — Register the workflow

Add an entry to `bmad/workflows.json`:

```json
{
  "id": "<use-case-id>",
  "name": "<Name>",
  "description": "...",
  "entry_agent": "<use-case-id>-supervisor",
  "status": "beta",
  "trigger_phrases": ["..."],
  "phases": [
    {
      "id": "phase-0",
      "name": "...",
      "supervisor": "<use-case-id>-supervisor",
      "output_dir": "docs/<use-case-id>/",
      "state_file": "docs/<use-case-id>/_meta/pipeline-state.yaml",
      "can_run_standalone": true
    }
  ],
  "shared_agents": ["code-reviewer", "software-architect"]
}
```

---

## Step 7 — Add catalog entries and sync DAG

**Option A (recommended)**: Add the new agents to `bmad/design/workflow-dag-draft.json` with their `preceded_by` / `followed_by` arrays, then run:
```bash
python3 bmad/scripts/backfill-dag.py
```
This auto-populates the `bmad` block in `catalog.json` for all new agents.

**Option B (manual)**: For each new agent, add an entry to `claude-marketplace/catalog.json` using `catalog-entry-template.json` and fill in the `bmad` block by hand.

Either way, publish to the marketplace:
```bash
./claude-marketplace/scripts/publish.sh <agent-name> 1.0.0 beta
```

---

## Step 8 — Write evals

Copy both eval templates to `claude-catalog/evals/<supervisor-name>/`:
```bash
cp claude-catalog/templates/new-use-case/evals/triggers.json claude-catalog/evals/<supervisor-name>/triggers.json
cp claude-catalog/templates/new-use-case/evals/evals.json    claude-catalog/evals/<supervisor-name>/evals.json
```

Fill in `triggers.json` with at least:
- 2 positive trigger queries (should fire the supervisor)
- 2 negative trigger queries (should NOT fire it — common confusables)

Fill in `evals.json` with at least:
- `eval-001`: primary full-pipeline invocation with ≥5 verifiable expectations
- `eval-002`: resume / partial-run scenario

---

## Checklist

- [ ] Supervisor body ≤ 10k chars (Anthropic ratchet)
- [ ] All workers body ≤ 10k chars
- [ ] `## When to invoke` present in every agent with `Do NOT use` line
- [ ] Description rubric: starts with `Use this agent when`, has 2–3 quoted triggers, closes with `See "When to invoke"...`
- [ ] `bmad/workflows.json` entry added
- [ ] `catalog.json` entries added for all new agents
- [ ] `catalog.json` entries include `bmad` block with DAG fields
- [ ] Agents published to marketplace
- [ ] `claude-catalog/evals/<supervisor>/triggers.json` written (≥2 positive, ≥2 negative)
- [ ] `claude-catalog/evals/<supervisor>/evals.json` written (≥2 scenarios including resume path)
- [ ] `CHANGELOG.md` [Unreleased] updated
- [ ] CI passes: `python3 .github/scripts/validate_catalog.py && python3 .github/scripts/validate_marketplace.py`
