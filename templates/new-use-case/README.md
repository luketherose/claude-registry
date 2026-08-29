# New use case: step-by-step guide

This template scaffolds a new workflow use case. A "use case" is a self-contained workflow
module with its own supervisor agent, its worker agents, its reference docs, and its
evaluations.

The registry currently has one: **application-replatforming**, in the `replatforming`
plugin. This guide shows how to add a second, for example code-audit,
documentation-generation or security-assessment.

Read [`docs/registry/how-to-write-a-capability.md`](../../docs/registry/how-to-write-a-capability.md)
first. It is authoritative for frontmatter, the model policy, the description budget and
the CI gates. This guide covers only the workflow-specific assembly on top.

---

## Prerequisites

Decide, before writing anything:

1. **Use case ID.** Kebab-case identifier, for example `code-audit`.
2. **Name.** Human-readable, for example "Code Audit Workflow".
3. **Plugin.** Which plugin owns it. Prefer the plugin that already owns the skills the
   workers need, because a skill in another plugin is only available when the user has
   that plugin enabled.
4. **Entry point.** The agent the user invokes, normally `<use-case-id>-supervisor`.
5. **Phases.** The ordered sequence of work phases.
6. **Shared agents.** Which existing agents it reuses. See `shared_agents` in
   `bmad/workflows.json`.

---

## Step 1: scaffold the supervisor

```bash
./scripts/new-capability.sh --plugin <plugin> --type agent <use-case-id>-supervisor
```

Run it with no arguments to be prompted for the plugin and the name. It creates the agent
file, an `evals.json` and `triggers.json` stub, and a `feat/agent-<name>` branch.

Then replace the generated body with the contents of
[`supervisor-template.md`](supervisor-template.md) and fill in every `REPLACE-ME`.

Key things to set:

- `## Role`: one paragraph on what the supervisor orchestrates
- `## When to invoke`: 3 or 4 trigger scenarios, plus the `Do NOT use` line
- `## Reference docs`: a table pointing at `${CLAUDE_PLUGIN_ROOT}/references/<use-case-id>/`
- `model: opus` with `effort: high`, per the model policy for supervisors
- `tools: Read, Glob, Bash, Agent`, plus `Skill` only if the body loads skills
- `color`: one not already used by a sibling supervisor

---

## Step 2: create the reference docs directory

```bash
mkdir -p plugins/<plugin>/references/<use-case-id>/
cp templates/new-use-case/docs/supervisor-protocol.md \
   plugins/<plugin>/references/<use-case-id>/supervisor-protocol.md
cp templates/new-use-case/docs/dispatch-prompt-template.md \
   plugins/<plugin>/references/<use-case-id>/dispatch-prompt-template.md
```

Reference docs live inside the plugin, not under `docs/`. Only what is inside the plugin
ships to a consumer's install, and only `${CLAUDE_PLUGIN_ROOT}` paths resolve there.

Then fill in:

- `supervisor-protocol.md`: decision rules, escalation triggers, constraints, state schema
- `dispatch-prompt-template.md`: the boilerplate prompt text for `Agent` tool calls

---

## Step 3: identify the workers

List the workers for each phase or wave. For each one decide:

- New agent (write it from [`worker-template.md`](worker-template.md)) or an existing
  shared agent?
- What is its output target directory?
- Is it always on, conditional, or fanned out per item?

---

## Step 4: scaffold the new workers

```bash
./scripts/new-capability.sh --plugin <plugin> --type agent <worker-name>
```

Replace the generated body with [`worker-template.md`](worker-template.md).

Workers must:

- Never hold the `Agent` tool. Workers do not dispatch sub-agents.
- Write only to their declared output directory.
- Use `model: sonnet` and file I/O tools only: `Read, Glob, Grep, Bash, Write`.
- Carry a boundary-only description. A worker is dispatched by name and never
  auto-delegated, so trigger enumerations and quoted user phrasings cost delegation
  budget and buy nothing.

---

## Step 5: define the pipeline state schema

Each phase writes its state to `_meta/pipeline-state.yaml`. Define the schema in
`plugins/<plugin>/references/<use-case-id>/supervisor-protocol.md` under a
`## State schema` section, following the format in `bmad/design/mapping.md` under
"Document-as-cache".

---

## Step 6: register the workflow

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
  "shared_agents": ["software-architect", "test-writer"]
}
```

Every name in `shared_agents` must be an agent that exists in the tree. Check it against
`plugins/*/agents/**/*.md` before committing.

---

## Step 7: record the dependency graph

Add one entry per new agent to the `agents` array in
`bmad/design/workflow-dag-draft.json`, using
[`dag-entry-template.json`](dag-entry-template.json) as the shape, with the
`preceded_by` and `followed_by` arrays filled in.

There is no separate registry manifest to update. Agents are discovered from
`plugins/<plugin>/agents/`, and the only manifests are the plugin's `plugin.json` and the
root `.claude-plugin/marketplace.json`. Nothing needs publishing: merging to `main` is
what ships the change, and consumers pick it up in the background.

> `bmad/scripts/backfill-dag.py` still writes the DAG into `claude-marketplace/catalog.json`,
> a file the plugin migration removed. It does not run. Edit
> `workflow-dag-draft.json` by hand until the script is repointed.

---

## Step 8: write the evaluations

Write these **before** the capability, not after. Copy both templates into the plugin:

```bash
mkdir -p plugins/<plugin>/evals/<use-case-id>-supervisor/
cp templates/new-use-case/evals/evals.json \
   plugins/<plugin>/evals/<use-case-id>-supervisor/evals.json
cp templates/new-use-case/evals/triggers.json \
   plugins/<plugin>/evals/<use-case-id>-supervisor/triggers.json
```

`evals.json` is a flat list of `{agent, query, files, expected_behavior}`, where `agent`
equals the directory name. Fill in at least:

- The primary full-pipeline invocation, with 5 or more checkable expectations
- A resume or partial-run scenario

`triggers.json` is a flat list of `{query, should_trigger, description}`. Fill in at least
2 positive queries and 2 negative ones, each negative naming the sibling that should
handle it instead. Check every negative case against the supervisor's own description
first: a prompt the description claims it handles cannot be a valid negative case.

Nothing in CI validates either schema, so a file written to the wrong shape passes review
and fails only when the suite is run.

---

## Checklist

- [ ] Supervisor body under 10k chars, workers under 10k chars
- [ ] `## When to invoke` present in every agent, with a `Do NOT use` line
- [ ] Every description starts with "Use this agent when", escapes its quotes, and does
      not end with a pointer to the body
- [ ] Supervisor is `opus` plus `effort: high`; workers are `sonnet`
- [ ] `Skill` is in `tools` for any agent whose body loads skills
- [ ] Every reference path uses `${CLAUDE_PLUGIN_ROOT}` and resolves inside the plugin
- [ ] Every capability the bodies name exists, under its flat name
- [ ] `bmad/workflows.json` entry added
- [ ] `bmad/design/workflow-dag-draft.json` entry added for every new agent
- [ ] `plugins/<plugin>/evals/<supervisor>/triggers.json` written, 2 or more positive and
      2 or more negative
- [ ] `plugins/<plugin>/evals/<supervisor>/evals.json` written, 2 or more scenarios
      including the resume path
- [ ] `plugins/<plugin>/.claude-plugin/plugin.json` version bumped (minor: new capability)
- [ ] `docs/registry/CHANGELOG.md` `[Unreleased]` updated
- [ ] CI passes locally:

```bash
python3 .github/scripts/validate_registry.py
claude plugin validate .
bash hooks/tests/test-pre-tool-safety.sh
```
