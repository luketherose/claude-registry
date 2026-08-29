# Claude Registry: business case

**Prepared for**: Section Head
**Prepared by**: Engineering Team
**Date**: 2026-08-30

---

## Executive summary

Our teams use Claude Code every day for development, analysis, and review. Today each
developer builds their own prompts from scratch, producing results of variable quality
with no accumulated knowledge over time.

**Claude Registry** is the infrastructure that changes this. The team's best capabilities
are defined, approved, versioned, and distributed to everyone, exactly like a shared code
library but for Claude's behaviour.

In three points:

- **Productivity.** A developer uses a ready-made capability instead of building one from
  scratch. The same quality is available at every seniority level.
- **Quality and governance.** Every capability goes through review before it is published.
  Claude's behaviour becomes predictable and traceable.
- **Organisational asset.** The team's domain knowledge and best practices become a
  versioned asset, not something lost with staff turnover.

---

## The current problem

When a team adopts Claude Code without shared structure, recurring patterns emerge that
limit the tool's value:

| Scenario | Consequence |
|---|---|
| Every developer writes their own code review prompt | Different outputs, no shared quality standard |
| A senior defines an excellent prompt for architectural analysis | The knowledge stays in their head or in a personal file |
| A new team member starts using Claude Code | Starts from scratch, without building on the team's experience |
| Claude produces unexpected results on a critical project | No way to understand which instruction generated the behaviour |
| The team changes approach on a topic, for example logging standards | Every developer updates their own prompt inconsistently |

The cost is not in the tool. It is in the lack of structure around the tool.

---

## The solution: shared capabilities

The registry ships two kinds of capability.

An **agent** is a specialisation of Claude for a role: software architect, functional
analyst, Java developer, technical analyst. It runs in its own context window with its own
tool set, and Claude delegates to it automatically based on its description.

A **skill** is knowledge loaded into the current context on demand: the team's Spring
conventions, REST design rules, testing standards, Accenture branding. Agents load the
skills they need. Nobody invokes a skill by hand.

Each capability:

- Defines exactly how Claude behaves in that role
- Specifies the expected output format (ADR, structured report, code with tests)
- Enforces team standards (naming, error handling, logging, security)
- Is updatable, so a prompt improvement reaches the whole team at once

Capabilities are distributed as **plugins** through the official Claude Code plugin
marketplace mechanism. There is no installer script and no file to copy.

---

## Key benefits

### 1. Seniority becomes scalable

Today the output difference between a senior and a junior developer using Claude depends
mostly on how well they can instruct the tool. With shared capabilities, the senior's
instructions become the standard for everyone.

> A junior using the `developer-java` capability produces code with the same architectural
> structure, the same error handling patterns, and the same test coverage a senior
> following our guidelines would produce.

### 2. Accelerated onboarding

A new team member runs two commands:

```bash
/plugin marketplace add luketherose/claude-registry
/plugin install dev-standards@claude-registry
```

They immediately have the team's capabilities, with standards and conventions already
built in. Better still, a project can commit its marketplace and its enabled plugin set
into `.claude/settings.json`, so a teammate who trusts the project gets the right
capabilities with no commands at all. There is no week of alignment on "how we use Claude
here".

### 3. Consistent and verifiable quality

Every published capability:

- Has gone through a pull request reviewed by at least one team member
- Has passed automated validation in GitHub Actions, covering manifest schema, frontmatter
  correctness, description budget, reference-link resolution, and the retired-capability
  and MCP-pinning gates
- Is versioned with semver on its plugin, so you know exactly what changed and when

If a capability produces unsatisfactory output, open a pull request, fix it, merge. The
whole team gets the improvement.

### 4. Real governance and control

The `main` branch is protected. No capability change reaches consumers without review and
approval. The team has full visibility into:

- Who proposed each change (git history)
- Exactly what changed (diff)
- When it was approved and by whom (pull request history)
- Which version each project is using (the plugin version, plus an optional `ref` pinning
  a release tag)

This is the level of governance expected of any critical software asset.

### 5. Knowledge that is not lost

When an experienced colleague leaves the team or moves to another project, their practices
stay in the registry. The knowledge belongs to the organisation, not to individuals.

---

## How it works in practice

```
Author writes the evaluations, then the capability
        ↓
Pull request on GitHub
        ↓
GitHub Actions validates: marketplace and plugin manifests, then agents,
skills, references and the description budget
        ↓
Manual review by a maintainer
        ↓
Merge to main, plugin version bumped
        ↓
Every consumer picks the change up in the background
```

A developer who wants to **use** a capability adds the marketplace and enables a plugin.
Updates arrive without any further action.

A developer who wants to **contribute** creates a branch, runs the scaffolding script,
writes the evaluations and then the capability, and opens a pull request. GitHub Actions
comments on the pull request with anything that needs fixing.

---

## Investment and return

### Setup cost (already incurred)

The repository is operational, the capabilities are published, and the governance pipeline
runs on every pull request. There are no additional infrastructure costs: GitHub is
already in use, Claude Code is already in use.

### Maintenance cost

| Activity | Frequency | Estimated effort |
|---|---|---|
| Pull request review for a new capability | On demand | 30 to 60 min per pull request |
| Update to an existing capability | Roughly monthly | 20 to 30 min per update |
| Onboarding a new member to the registry | Once | 30 min |

### Expected return

| Scenario | Estimated saving |
|---|---|
| Developer uses an existing capability instead of building a prompt from scratch | 20 to 40 min per task |
| Rework avoided because output quality is consistent | 1 to 2 h per sprint per developer |
| Onboarding a new member on Claude standards | 1 to 2 working days |
| Regressions in Claude's behaviour caught early | Variable, avoids escalation |

For a team of 5 developers, with 2 capabilities used per task per day, the estimated saving
is in the order of 2 to 4 hours per week per person.

---

## What is available today

Six plugins, 86 agents and 46 skills. A project enables only the plugins it needs, which
keeps subagent routing sharp.

| Plugin | What it covers |
|---|---|
| `dev-standards` | Language and framework standards, developer agents for Java, Python, frontend, Go, Rust, Kotlin, C#, PHP and Ruby, plus test authoring, REST API design and bug diagnosis |
| `analysis-architecture` | Architecture design and ADRs, functional requirement extraction, technical debt and security assessment, registry auditing, multi-domain orchestration |
| `replatforming` | The AS-IS to TO-BE pipeline: codebase indexing, functional and technical analysis, baseline testing, TO-BE scaffolding, equivalence verification |
| `docs-branding` | Documentation authoring and Accenture-branded deliverables: READMEs, wikis, runbooks, PDF, Word, PowerPoint |
| `deliberation` | Multi-agent structured debate for high-stakes or irreversible decisions, with an auditable decision record |
| `caveman` | Terse output mode for prose, commit messages and review comments |

The most frequently used agents are `developer-java`, `developer-python`,
`developer-frontend`, `test-writer`, `debugger`, `api-designer`, `software-architect`,
`functional-analyst`, `technical-analyst` and `documentation-writer`. Code review is
covered by Anthropic's own `pr-review-toolkit` plugin, which this registry treats as an
optional dependency rather than duplicating.

### Proposed next steps

1. **Team adoption.** Roll the plugins out to the active projects.
2. **Feedback loop.** Collect developer feedback after 2 to 4 weeks of use.
3. **Evaluation coverage.** Extend the trigger evaluations, which are what catch a
   description edit that quietly breaks routing.
4. **Domain capabilities.** Build capabilities specialised for our application domains,
   for example `developer-payments` or `analyst-compliance`.
5. **Usage metrics.** Add lightweight telemetry to see which capabilities are used and
   where the gaps are.

---

## In summary

Claude Registry is not an experimental project. It is the governance infrastructure for a
tool the team already uses. The question is not whether it is worth doing. It is whether
we want the value of Claude Code to stay fragmented per developer, or to become a shared
organisational asset.

The registry answers that concretely: a Git repository, reviewed pull requests, versioning,
automation. The same standards we apply to code, applied to the behaviour of the AI that
helps produce it.

---

*For technical details, operational documentation, and repository access:
`github.com/luketherose/claude-registry`*
