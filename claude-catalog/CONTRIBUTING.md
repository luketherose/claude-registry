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

## Workflow

### Adding a new capability

```bash
git checkout -b add/capability-name
# Write claude-catalog/agents/capability-name.md
# Write claude-catalog/examples/capability-name-example.md  (at least 1)
# Write claude-catalog/evals/capability-name-eval.md        (at least 2 scenarios)
# Add entry to CHANGELOG.md under "Unreleased"
git push origin add/capability-name
# Open PR → apply review-checklist.md
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

## PR requirements

- [ ] Subagent file follows schema in `how-to-write-a-capability.md`
- [ ] `name` in frontmatter matches filename (without `.md`)
- [ ] `description` is precise enough to guide automatic delegation
- [ ] At least one example file in `examples/`
- [ ] At least two eval scenarios in `evals/`
- [ ] CHANGELOG.md entry under "Unreleased"
- [ ] Reviewer has applied `review-checklist.md`

## What NOT to do

- Do not put credentials, API keys, or secrets anywhere in this repository
- Do not modify files in `claude-marketplace/` directly — use the publish script
- Do not bypass the review process for "small" fixes — a one-line prompt change
  can significantly alter behavior
- Do not version capabilities in their filenames — use git tags
