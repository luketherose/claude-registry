<!--
audience: contributor
diataxis: how-to
last-verified: 2026-08-30
verified-against: c6c780a
-->

# Contributing

How to add or change a capability. This page is the mechanical process. For what makes a
good capability, read
[`docs/registry/how-to-write-a-capability.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/how-to-write-a-capability.md),
which is authoritative.

## TL;DR

1. Branch.
2. Write the evaluations first.
3. Write the capability under `plugins/<plugin>/`.
4. Add an example.
5. Bump the plugin version and add a changelog entry.
6. Run the validator and `claude plugin validate .`.
7. Open a pull request. One approval merges.

## Setup

Plain Git. No build tools, no package managers.

```bash
git clone https://github.com/luketherose/claude-registry.git
cd claude-registry
pip install pyyaml
```

`pyyaml` is what the frontmatter parse gate needs. Install `tiktoken` too if you want
exact token counts instead of an estimate.

To test what you are writing, add this checkout as a marketplace:

```bash
claude plugin marketplace add .
```

Then work **from a project directory rather than from the registry**, run `/agents` to
confirm the agent is there, and walk through the scenarios in
`plugins/<plugin>/evals/<name>/evals.json`. Testing from a project is what catches a
`${CLAUDE_PLUGIN_ROOT}` path that resolves in the repository but not in an install.

## Step 0: pick the type and the plugin

Does the work need its own context window and its own tools? That is an agent. Is it
knowledge or a procedure the current agent should apply itself? That is a skill.

Then pick the plugin that already owns the skills the capability needs.

| Plugin | Scope |
|---|---|
| `replatforming` | The five-phase AS-IS to TO-BE pipeline and anything only useful inside it |
| `dev-standards` | Language and framework standards, developer agents, test authoring, debugging |
| `analysis-architecture` | Architecture, requirements, technical analysis, orchestration, registry auditing |
| `deliberation` | The debate engine and its personas |
| `docs-branding` | Documentation authoring and branded deliverables |
| `caveman` | Output-style skills |

A capability and the skills it always needs belong to the same plugin. Where a
cross-plugin reference is unavoidable, say so in the agent body and describe what the
agent does without it. Never make an agent hard-fail on a skill it does not own.

## Step 1: scaffold

```bash
./scripts/new-capability.sh --plugin dev-standards my-agent
./scripts/new-capability.sh --plugin dev-standards --type skill my-skill
```

Run it with no arguments to be prompted. It creates:

- the capability file, `plugins/<plugin>/agents/<name>.md` or
  `plugins/<plugin>/skills/<name>/SKILL.md` with a `references/` directory
- `plugins/<plugin>/evals/<name>/evals.json` and `triggers.json`
- the branch `feat/agent-<name>` or `feat/skill-<name>`

It refuses a name that is not lowercase alphanumeric with hyphens, and a name containing
`anthropic` or `claude`, which are reserved.

The eval stubs it writes are in the schemas CI enforces, including a `triggers.json`
negative whose placeholder description reads "what makes it out of scope, without naming
the winner". Fill the placeholders in; do not change the shape. Both schemas are in
[Reference](Reference#evaluations).

## Step 2: write the evaluations first

Not after. Writing them afterwards documents an imagined problem.

1. Run Claude on a representative task with no capability installed. Record what it gets
   wrong.
2. Write three scenarios in `evals.json` covering those gaps.
3. Write `triggers.json` covering both the prompts that must activate the capability and
   the near-miss prompts that must not.
4. Write the smallest capability that passes, then iterate against the evaluations rather
   than against your intuition.

Trigger evaluations are what catch a description edit that quietly breaks routing.

Each trigger case's `description` restates what the query is about and never names the
capability that should win. CI rejects a description that states the verdict, and rejects
one that names an agent or skill the query itself does not mention. The rule exists because
the suite once graded itself: an earlier corpus named the winner in 364 of 365
descriptions, and a nine-line keyword table scored 99.7 percent on it without reading a
capability. Choose the sibling you are testing against when you pick the query, then leave
it out of the description.

## Step 3: write the capability

### An agent

```markdown
---
name: my-agent
description: "Use this agent when <trigger>. <What it produces.> Do not use it for <adjacent case> (use <sibling> instead)."
tools: Read, Grep, Glob
model: inherit
color: blue
---

## When to invoke
## Role
## What you always do
## What you never do
## Skills
## Output format
## Quality criteria
```

`## When to invoke` is mandatory and CI warns without it. It carries the worked scenarios
that would otherwise bloat the `description`.

Rules that matter most:

- **Be opinionated.** Name the frameworks, define the output format exactly, leave no
  structure to interpretation.
- **State what the agent delegates**, and to which named sibling.
- **State when the agent escalates** to the user instead of guessing.
- **Include a self-check** the agent runs before responding.
- **Keep the tool list minimal.** An agent whose body invokes skills must carry `Skill`
  in `tools`, or the instruction is inert and CI fails.
- **Reference bundled material with `${CLAUDE_PLUGIN_ROOT}`.** A repository-relative path
  resolves against the consumer's project and silently returns nothing.

For the description: state the trigger condition and the boundary, not a summary of the
system prompt. Worker agents that only ever run under a supervisor need the boundary and
nothing else. User-facing agents benefit from two to four quoted user phrasings, because
those match how people actually ask.

### A skill

```markdown
---
name: my-skill
description: "This skill should be used when <situation>: <topics>. Do not use it for <adjacent case> (use <sibling> instead)."
---
```

Exactly those two frontmatter fields. `model`, `tools` and `color` are rejected by CI.

- Body under 500 lines. When you cross it, move detail into `references/`. Do not
  compress the prose.
- Assume Claude is already smart. Explain only what it does not already know.
- One word per concept, used consistently.
- No time-sensitive statements. Superseded guidance goes into an `## Old patterns`
  section inside `<details>`.
- Give a default and one escape hatch. Do not offer four options.
- Link every reference file explicitly, one line each, saying what is in it. References
  must be one level deep from `SKILL.md`.
- A reference file longer than 100 lines starts with a `## Contents` table, so a partial
  read still shows the full scope.
- Deterministic work belongs in the skill's own `scripts/` directory. When that directory
  exists it carries a mandatory `README.md` giving each script's invocation, inputs,
  outputs and exit codes, so the consuming agent can call it without reading the source.

## Step 4: wire the skill into the agents that use it

On demand, which is the default:

```markdown
## Skills

Load the following skills with the `Skill` tool when the task touches their domain:

- `java-spring-standards` for package structure, layering, error handling and observability
- `spring-data-jpa` when the change touches entities, repositories or transactions
```

Preloaded, only for a skill an agent needs on **every single run**:

```yaml
skills:
  - accenture-branding
```

Preloading five skills defeats progressive disclosure and costs the agent its context.
Four agents preload today, each exactly one skill.

## Step 5: version and changelog

Bump `version` in `plugins/<plugin>/.claude-plugin/plugin.json` per the table in
[Governance](Governance#releases), then add an entry to `docs/registry/CHANGELOG.md`
under `[Unreleased]`.

Also update `README.md` when the capability roster changes, and
`how-to-write-a-capability.md` when a convention changes.

## Step 6: validate locally

```bash
python3 .github/scripts/validate_registry.py
claude plugin validate .
bash hooks/tests/test-pre-tool-safety.sh
bash scripts/test-clean-install.sh
```

All four run in CI, split across the `Validate marketplace` and `Validate catalog` jobs.
Exit code 0 with zero errors is the bar. Warnings do not block, and are worth reading
anyway: they are the rules the structural gates never covered.

The clean-install check installs every plugin into a throwaway `CLAUDE_CONFIG_DIR`, so
running it locally does not touch your own `~/.claude`. It is the one that catches a
reference path which resolves in the repository and not in an install.

Pre-flight checklist:

- [ ] `name` matches the filename (agent) or the directory (skill)
- [ ] `description` is third person, specific, and names the sibling to use instead
- [ ] Agent body has `## When to invoke`
- [ ] `SKILL.md` body is under 500 lines
- [ ] Reference links resolve and are one level deep
- [ ] Bundled paths use `${CLAUDE_PLUGIN_ROOT}`
- [ ] `tools` is a minimal allowlist, and includes `Skill` if the body invokes skills
- [ ] Model choice follows the policy, or is justified in an HTML comment
- [ ] Cross-plugin skill dependencies are declared and degrade gracefully
- [ ] Three evaluation scenarios plus `triggers.json`, in the schemas CI enforces
- [ ] No `triggers.json` description states a verdict or names a capability its query omits
- [ ] One example in the plugin's `examples/`
- [ ] Plugin version bumped and changelog entry added
- [ ] No credentials, tokens or secrets anywhere

## Step 7: open the pull request

```bash
git add -A
git commit -m "feat(dev-standards): add my-agent"
git push -u origin feat/agent-my-agent
gh pr create --title "feat(dev-standards): add my-agent" --body "..."
```

Both CI jobs post their findings as a pull-request comment. One reviewer approval merges.
Reviewers apply
[`docs/registry/review-checklist.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/review-checklist.md).

## Updating an existing capability

```bash
git checkout -b update/<name>
```

Edit the files, bump the plugin version, add the changelog entry, validate, open the pull
request. A change to a `name` or a `description` is a major bump and needs a migration
note, because both drive routing.

## Removing or renaming a capability

Three things in one pull request, plus a fourth at removal:

1. Deprecation notice in the capability's `description`.
2. An `ANTI-PATTERNS.md` entry recording what was tried, why it failed, what replaced it,
   and under which conditions a retry would be valid.
3. The file stays for 90 days so teams can migrate.
4. At removal, add the old name to the `RETIRED` dict in
   `.github/scripts/validate_registry.py`. CI then fails on any leftover reference in
   `plugins/`, `wiki/`, `docs/`, `README.md` or `CLAUDE.md`.

## What not to do

- Do not put credentials, API keys or secrets anywhere in this repository.
- Do not invent frontmatter fields. An unrecognised multi-line key corrupts the value of
  the key above it. Record a model rationale in an HTML comment in the body instead.
- Do not use a repository-relative path for bundled material. Use
  `${CLAUDE_PLUGIN_ROOT}`.
- Do not put knowledge in an agent body when a skill already defines it. Load the skill.
- Do not version a capability in its filename. Versions live in `plugin.json` and in git
  tags.
- Do not bypass review for a small fix. A one-line prompt change can move behaviour a
  long way.
- Do not rename a CI job. The branch ruleset requires the current job names, and a
  required status context that never reports blocks every pull request. Change the
  ruleset first.

## Related

- [Reference](Reference): fields, schemas, gates
- [Governance](Governance): review, versioning, deprecation
- [Architecture](Architecture): how the CI flow and the pipeline fit together
