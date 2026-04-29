<!--
audience: contributor
diataxis: how-to
last-verified: 2026-04-28
verified-against: 1e9445a
-->

# Contributing

How to add or modify a capability. This page covers the mechanical
process. For depth on _what makes a good capability_ read
[`how-to-write-a-capability.md`](https://github.com/luketherose/claude-registry/blob/main/claude-catalog/how-to-write-a-capability.md)
in the repo.

## TL;DR

1. Branch off `main`.
2. Add or modify a `.md` file under `claude-catalog/agents/` (or
   `claude-catalog/skills/`).
3. Add or update an entry in `claude-marketplace/catalog.json`. Mirror
   the file to `claude-marketplace/{tier}/`.
4. Add an `[Unreleased]` entry to `claude-catalog/CHANGELOG.md`.
5. Run both validators locally — they're the same scripts CI runs.
6. Open a PR. One approval merges.

## Setup

Plain git, no build tools.

```bash
git clone https://github.com/luketherose/claude-registry.git
cd claude-registry
```

Test a subagent locally before opening the PR:

```bash
# Copy the file into the project where you'll test it
cp claude-catalog/agents/your-new-thing.md /path/to/test-project/.claude/agents/
# Or install everything globally
./claude-catalog/scripts/setup-capabilities.sh --global
```

Then in Claude Code: `/agents` to see it listed, or use it implicitly
by asking something its `description` should match.

## Adding a new agent

### Use the scaffold script

```bash
./claude-catalog/scripts/new-capability.sh my-agent-name
```

The script:
- creates `claude-catalog/agents/my-agent-name.md` from a template
- creates `claude-catalog/examples/my-agent-name-example.md`
- creates `claude-catalog/evals/my-agent-name-eval.md`
- creates the git branch `add/my-agent-name`

### Or do it manually

```bash
git checkout -b add/my-agent-name
```

Create:

- `claude-catalog/agents/my-agent-name.md` (the agent itself; see
  [Reference § Subagent file format](Reference#subagent-file-format))
- `claude-catalog/examples/my-agent-name-example.md` (at least one
  invocation example)
- `claude-catalog/evals/my-agent-name-eval.md` (at least two scenarios)

Add an entry to `claude-marketplace/catalog.json`:

```json
{
  "name": "my-agent-name",
  "version": "0.1.0",
  "tier": "beta",
  "type": "agent",
  "status": "active",
  "description": "Use when ...",
  "file": "beta/<topic>/my-agent-name.md",
  "dependencies": [],
  "tools": ["Read", "Grep", "Glob", "Write"],
  "model": "sonnet",
  "tags": ["..."],
  "published": "2026-04-28",
  "changelog": "Initial release"
}
```

Mirror the file (use the topic subfolder — see "Marketplace topics" in the
project `CLAUDE.md` or the `claude-marketplace/README.md` for the full list):

```bash
mkdir -p claude-marketplace/beta/<topic>
cp claude-catalog/agents/<topic>/my-agent-name.md claude-marketplace/beta/<topic>/my-agent-name.md
```

Add a `CHANGELOG.md` entry under `[Unreleased]`:

```markdown
- **`my-agent-name@0.1.0` (beta)** — sonnet, [one-paragraph description].
  Tools: Read, Grep, Glob, Write.
```

Validate locally:

```bash
python3 .github/scripts/validate_catalog.py
python3 .github/scripts/validate_marketplace.py
```

Both must be green before pushing.

```bash
git add -A
git commit -m "feat(agent): add my-agent-name"
git push -u origin add/my-agent-name
gh pr create --title "feat(agent): add my-agent-name" --body "..."
```

## Adding a new skill

Skills are atomic knowledge providers — `model: haiku`, `tools: Read`
only. They are invoked by agents, not by users.

### Constraints

- `model: haiku` — knowledge retrieval, not reasoning.
- `tools: Read` only — no `Edit`, `Write`, `Bash`, or `Agent`. The CI
  catalog gate enforces this.
- No `## Skills` section — skills are leaf nodes; they cannot delegate.

### Workflow

```bash
git checkout -b add/my-skill-name
# Write claude-catalog/skills/<topic>/my-skill-name.md
# Mirror to claude-marketplace/skills/<topic>/my-skill-name.md
# Add entry to catalog.json with "type": "skill", "tier": "skill",
#   "file": "skills/<topic>/my-skill-name.md"
# Add "my-skill-name" to the "dependencies" list of every agent that uses it
# Add CHANGELOG.md entry under [Unreleased]
# Validate, commit, push, PR
```

### How an agent invokes a skill

Add a `## Skills` section to the agent's system prompt:

```markdown
## Skills

Before starting any task, invoke the following skills to load shared
standards:

- `java-spring-standards` — Java/Spring Boot conventions
- `testing-standards` — testing principles and framework templates
```

Then list each skill in the agent's `dependencies` field in
`catalog.json` so the setup script auto-installs them.

## Updating an existing capability

```bash
git checkout -b update/capability-name
# Edit the .md file in claude-catalog/
# Mirror the change to claude-marketplace/{tier}/capability-name.md
# Bump the version in catalog.json (PATCH for fixes, MINOR for new behaviour)
# Add a CHANGELOG.md entry under [Unreleased]
# Validate, commit, push, PR
```

See [Reference § Versioning](Reference#versioning) for when to bump
which segment.

## Bug fixes

```bash
git checkout -b fix/<topic>
```

For fixes affecting multiple capabilities (e.g. the 2026-04-28 Mermaid
shell-injection hardening), it is OK to bump every affected file's PATCH
version in a single PR, with a single `CHANGELOG.md` `[Unreleased] ###
Fixed` block listing each.

## What gets reviewed

Reviewers apply
[`claude-catalog/review-checklist.md`](https://github.com/luketherose/claude-registry/blob/main/claude-catalog/review-checklist.md).
Common asks:

- Is the `description` precise enough that Claude will delegate
  correctly? "Use when …" + concrete trigger conditions.
- Is the tool list minimal? Default to read-only; expand only when
  necessary.
- Is the system prompt **opinionated**? Generic prompts produce generic
  output.
- Are output formats explicitly defined? "Produce a Markdown report"
  isn't enough — define the sections.
- Are completeness checks declared? "Before responding, verify X, Y, Z."
- Is escalation defined? When should the agent ask for context rather
  than guess?
- For skills: `model: haiku`, `tools: Read` only, no `## Skills`
  section.
- For agents that produce file content: include the **File-writing rule**
  block (mandates `Write`/`Edit`, forbids `Bash` heredoc/redirect; this
  was added repo-wide after the 2026-04-28 incident — see
  [Changelog](Changelog)).

## What NOT to do

- Do not put credentials, API keys, or secrets anywhere in this
  repository.
- Do not modify files in `claude-marketplace/` directly without also
  updating `catalog.json` and the matching `claude-catalog/` source.
- Do not bypass the review process for "small" fixes — a one-line prompt
  change can significantly alter behaviour.
- Do not version capabilities in their filenames (use git tags).
- Do not add knowledge that belongs in a skill directly into an agent
  system prompt if that same knowledge is already defined in a skill.

## Local validation cheat sheet

```bash
# CI gate 1
python3 .github/scripts/validate_catalog.py

# CI gate 2
python3 .github/scripts/validate_marketplace.py

# Scaffold a new capability + branch
./claude-catalog/scripts/new-capability.sh --type agent my-agent
./claude-catalog/scripts/new-capability.sh --type skill my-skill

# Install your in-progress capability for testing
./claude-catalog/scripts/setup-capabilities.sh --global
```

## Related

- [Reference](Reference) — schemas, fields, conventions
- [Governance](Governance) — lifecycle, versioning, SLAs
- [`how-to-write-a-capability.md`](https://github.com/luketherose/claude-registry/blob/main/claude-catalog/how-to-write-a-capability.md) — depth on writing good prompts
- [`review-checklist.md`](https://github.com/luketherose/claude-registry/blob/main/claude-catalog/review-checklist.md) — what reviewers check
