# Contributing

## Before you start

Read `how-to-write-a-capability.md`. It covers the schema, quality criteria, and common
pitfalls. This file covers the mechanical process.

## Setup

This is a plain Git repository. No build tools, no package managers. Clone and edit.

```bash
git clone <repo-url>
cd claude-registry
```

To test a subagent locally before opening a PR:
1. Copy the `.md` file to your project's `.claude/agents/` directory
2. Invoke it in Claude Code: `/agents` → select the agent, or let Claude delegate naturally
3. Run through the eval scenarios in `evals/{capability-name}-eval.md`

---

## Workflow

### Adding a new agent capability

```bash
./claude-catalog/scripts/new-capability.sh capability-name
# or for a skill:
./claude-catalog/scripts/new-capability.sh --type skill skill-name
```

The script creates the agent file, example, eval, and branch.

Manual steps if you prefer:

```bash
git checkout -b add/capability-name
# Write claude-catalog/agents/capability-name.md
# Write claude-catalog/examples/capability-name-example.md  (at least 1)
# Write claude-catalog/evals/capability-name-eval.md        (at least 2 scenarios)
# Add entry to CHANGELOG.md under "Unreleased"
git push origin add/capability-name
# Open PR → apply review-checklist.md
```

### Adding a new skill

Skills are atomic knowledge providers (standards, conventions, brand rules) shared
across multiple agent capabilities. They are not autonomous agents — they do not act,
they return information.

Use a skill when the same domain knowledge would otherwise be copy-pasted into two or
more agent system prompts.

```bash
git checkout -b add/skill-name
# Write claude-catalog/skills/skill-name.md
#   - model: haiku  (knowledge retrieval, no deep reasoning needed)
#   - tools: Read   (read-only; skills do not modify files or run commands)
#   - No Agent tool (skills are leaf nodes — they cannot spawn subagents)
# Write claude-catalog/examples/skill-name-example.md  (optional but recommended)
# Write claude-catalog/evals/skill-name-eval.md        (optional but recommended)
# Add "skill-name" to the "dependencies" list of each agent that uses it in catalog.json
# Add entry to CHANGELOG.md under "Unreleased"
git push origin add/skill-name
# Open PR
```

To invoke a skill from an agent, add a `## Skills` section to the agent's system prompt:

```markdown
## Skills

Before starting any task, invoke the following skills to load shared standards:

- `java-spring-standards` — Java/Spring Boot conventions
- `testing-standards` — testing principles and framework templates
```

### Updating an existing capability

```bash
git checkout -b update/capability-name
# Edit the relevant files
# Update CHANGELOG.md under "Unreleased"
# If model behavior changes materially, note in PR description
git push origin update/capability-name
# Open PR → apply review-checklist.md
```

### Breaking changes

If you're changing the `name` or `description` frontmatter, this is a breaking change:
- Note it clearly in the PR description
- Bump the major version in the release step
- Add a migration note in CHANGELOG.md explaining what teams need to update

---

## PR requirements

### For agent capabilities

- [ ] Subagent file follows schema in `how-to-write-a-capability.md`
- [ ] `name` in frontmatter matches filename (without `.md`)
- [ ] `description` is precise enough to guide automatic delegation
- [ ] At least one example file in `examples/`
- [ ] At least two eval scenarios in `evals/`
- [ ] CHANGELOG.md entry under "Unreleased"
- [ ] Reviewer has applied `review-checklist.md`

### For skills

- [ ] Skill file is in `claude-catalog/skills/`, not `agents/`
- [ ] `model: haiku` (override with justification if reasoning depth requires more)
- [ ] `tools: Read` only (no Edit, Write, Bash, or Agent)
- [ ] No `## Skills` section (skills are leaf nodes, they do not invoke other skills)
- [ ] Content is purely declarative knowledge (standards, conventions, templates)
- [ ] Each agent that uses this skill lists it in its `## Skills` section
- [ ] `catalog.json` updated: skill entry added + dependent agents have the skill in `"dependencies"`
- [ ] CHANGELOG.md entry under "Unreleased"

---

## What NOT to do

- Do not put credentials, API keys, or secrets anywhere in this repository
- Do not modify files in `claude-marketplace/` directly — use the publish script
- Do not bypass the review process for "small" fixes — a one-line prompt change
  can significantly alter behavior
- Do not version capabilities in their filenames — use git tags
- Do not add knowledge that belongs in a skill directly into an agent system prompt
  if that same knowledge is already defined in a skill
