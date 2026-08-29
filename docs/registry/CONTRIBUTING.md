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

To test a capability locally before opening a PR, add this clone as a marketplace and
enable the plugin you are changing:

```bash
claude plugin marketplace add .
```

Then, from a project directory rather than from the registry, run `/agents` to confirm the
agent is there, or let Claude delegate to it naturally, and work through the scenarios in
`plugins/<plugin>/evals/<name>/evals.json`. Testing from a project is what catches a
`${CLAUDE_PLUGIN_ROOT}` path that resolves in the repository but not in an install.

---

## Workflow

### Adding a new agent capability

```bash
./scripts/new-capability.sh --plugin dev-standards capability-name
# or for a skill:
./scripts/new-capability.sh --plugin dev-standards --type skill skill-name
```

Run it with no arguments to be prompted for the plugin and the name. It creates the
capability file, an `evals.json` and `triggers.json` stub, and the `feat/<type>-<name>`
branch.

Manual steps if you prefer:

```bash
git checkout -b feat/agent-capability-name
# Write plugins/<plugin>/agents/capability-name.md
# Write plugins/<plugin>/examples/capability-name-example.md  (at least 1)
# Write plugins/<plugin>/evals/capability-name/evals.json + triggers.json
#   (at least 3 scenarios, written before the capability)
# Add entry to docs/registry/CHANGELOG.md under "Unreleased"
git push origin feat/agent-capability-name
# Open a PR, then apply review-checklist.md
```

### Adding a new skill

A skill is knowledge and procedure loaded into the current context on demand, not a
subagent. It does not act. It gives the calling agent what it needs to act.

Use a skill when the same domain knowledge would otherwise be copy-pasted into two or
more agent system prompts.

```bash
git checkout -b feat/skill-skill-name
# Write plugins/<plugin>/skills/skill-name/SKILL.md
#   - frontmatter: exactly name and description; model, tools and color are rejected
#   - name equals the directory name; body stays under 500 lines
#   - overflow goes into references/, linked one level deep from the body
# Write plugins/<plugin>/examples/skill-name-example.md  (optional but recommended)
# Write plugins/<plugin>/evals/skill-name/triggers.json  (positive and near-miss prompts)
# Reference the skill from each consuming agent, and make sure that agent has Skill in
#   its tools list, or preload it via the "skills:" frontmatter field when the agent
#   needs it on every run
# Add entry to docs/registry/CHANGELOG.md under "Unreleased"
git push origin feat/skill-skill-name
# Open a PR
```

Skills carry `triggers.json` but no `evals.json`. A skill has no behaviour of its own to
score, so it is judged on whether the right prompt activates it.

To load a skill from an agent, add a `## Skills` section to the agent body and put `Skill`
in its `tools` list. The tool is what makes the instruction work; without it, the agent
silently falls back on its own priors:

```markdown
## Skills

Load the following skills with the `Skill` tool when the task touches their domain:

- `java-spring-standards` for package structure, layering, error handling and observability
- `testing-standards` for testing principles and framework templates
```

### Updating an existing capability

```bash
git checkout -b fix/capability-name
# Edit the relevant files
# Update docs/registry/CHANGELOG.md under "Unreleased"
# If model behavior changes materially, note it in the PR description
git push origin fix/capability-name
# Open a PR, then apply review-checklist.md
```

### Breaking changes

If you're changing the `name` or `description` frontmatter, this is a breaking change:
- Note it clearly in the PR description
- Bump the major version in the release step
- Add a migration note in CHANGELOG.md explaining what teams need to update

---

## PR requirements

### For agent capabilities

- [ ] Subagent file follows the schema in `how-to-write-a-capability.md`
- [ ] `name` in frontmatter matches the filename (without `.md`)
- [ ] `description` is precise enough to guide automatic delegation, and any quote in it
      is escaped so the frontmatter still parses as YAML
- [ ] `Skill` is in `tools` if the body talks about loading skills
- [ ] Body has `## When to invoke`
- [ ] At least one example file in `plugins/<plugin>/examples/`
- [ ] At least three scenarios in `plugins/<plugin>/evals/<name>/evals.json`, plus
      `triggers.json`
- [ ] `docs/registry/CHANGELOG.md` entry under "Unreleased"
- [ ] Reviewer has applied `review-checklist.md`

### For skills

- [ ] Skill file is at `plugins/<plugin>/skills/<name>/SKILL.md`, not under `agents/`
- [ ] Frontmatter is exactly `name` and `description`
- [ ] `name` equals the directory name; `description` is at most 1024 characters and
      third person
- [ ] Body is under 500 lines, with overflow in `references/`
- [ ] Content is declarative knowledge (standards, conventions, templates)
- [ ] Each agent that uses this skill names it and holds the `Skill` tool
- [ ] The skill lives in the same plugin as the agents that always need it. Cross-plugin
      references are declared in the agent body and degrade gracefully
- [ ] `plugins/<plugin>/evals/<name>/triggers.json` exists
- [ ] `docs/registry/CHANGELOG.md` entry under "Unreleased"

---

## What NOT to do

- Do not put credentials, API keys, or secrets anywhere in this repository
- Do not hand-edit `.claude-plugin/marketplace.json` plugin entries to describe something
  that belongs in the plugin's own `plugin.json`
- Do not bypass the review process for "small" fixes. A one-line prompt change can
  significantly alter behavior
- Do not version capabilities in their filenames. Versions live in git tags and in the
  plugin's `plugin.json`
- Do not add knowledge that belongs in a skill directly into an agent system prompt
  if that same knowledge is already defined in a skill
