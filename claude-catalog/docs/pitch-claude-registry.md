# Claude Registry — Business Case

**Prepared for**: Section Head
**Prepared by**: Engineering Team
**Date**: April 2026

---

## Executive Summary

Our teams use Claude Code every day for development, analysis, and review.
Today each developer builds their own prompts from scratch, producing results
of variable quality with no accumulated knowledge over time.

**Claude Registry** is the infrastructure that transforms this picture: the team's
best capabilities are defined, approved, versioned, and made available to everyone —
exactly like a shared code library, but for Claude's behaviour.

**In three points:**

- **Productivity**: a developer uses a ready-made capability instead of building it from scratch;
  the same quality is available at every seniority level.
- **Quality and governance**: every capability goes through an approved review before being
  published; Claude's behaviour is predictable and traceable.
- **Organisational asset**: the team's domain knowledge and best practices become
  a versioned asset — they are not lost with staff turnover.

---

## The Current Problem

When a team adopts Claude Code without shared structure, recurring patterns emerge
that limit the tool's value:

| Scenario | Consequence |
|---|---|
| Every developer writes their own code review prompt | Different outputs, no shared quality standard |
| A senior defines an excellent prompt for architectural analysis | The knowledge stays in their head or in a personal file |
| A new team member starts using Claude Code | Starts from scratch, without building on the team's experience |
| Claude produces unexpected results on a critical project | No way to understand which instruction generated the behaviour |
| The team changes approach on a topic (e.g. logging standards) | Every developer updates their own prompt inconsistently |

**The cost is not in the tool — it is in the lack of structure around the tool.**

---

## The Solution: Shared Capabilities

A **capability** is a specialisation of Claude for a specific role:
*Software Architect*, *Functional Analyst*, *Developer Java/Spring*, *Code Reviewer*, etc.

Each capability:
- Defines **exactly** how Claude should behave in that role
- Specifies the expected **output format** (ADR, structured report, code with tests, etc.)
- Enforces **team standards** (naming conventions, error handling, logging, security)
- Is **updatable** — prompt improvements are distributed to the whole team

Capabilities live in the **Claude Registry**: a Git repository with two layers —
*catalog* (development and internal review) and *marketplace* (distribution to teams).

---

## Key Benefits

### 1. Seniority becomes scalable

Today the output difference between a senior and a junior developer using Claude
depends primarily on how well they can instruct the tool. With shared capabilities,
the senior's instructions become the standard for everyone.

> A junior using the `developer-java-spring` capability produces code with
> the same architectural structure, the same error handling patterns, and
> the same test coverage that a senior following our guidelines would produce.

### 2. Accelerated onboarding

A new team member only needs to:
1. Clone the registry
2. Run a setup script
3. Open Claude Code

They immediately have access to all the team's capabilities, with standards and conventions
already built in. There is no week of alignment on "how we use Claude here".

### 3. Consistent and verifiable quality

Every published capability:
- Has gone through a **Pull Request with review** by at least one team member
- Has passed **automated validation** (GitHub Actions) checking structure,
  completeness, and correctness
- Is **versioned** with SemVer: you know exactly what changed and when

If a capability produces unsatisfactory output, open a PR, fix it, republish.
The whole team benefits from the improvement.

### 4. Real governance and control

The `main` branch is protected: no capability change reaches production
without explicit review and approval. The team has full visibility into:

- Who proposed every change (git history)
- Exactly what changed (diff)
- When it was approved and by whom (PR history)
- Which version each project is using (git tag + catalog.json)

This is the level of governance expected from any critical software asset.

### 5. Knowledge that is not lost

When an experienced colleague leaves the team or moves to another project, their best
practices remain in the registry. The knowledge belongs to the organisation, not to individuals.

---

## How It Works in Practice

```
Author writes capability
        ↓
Pull Request on GitHub
        ↓
GitHub Actions validates automatically (structure, naming, completeness)
        ↓
Manual review by maintainer
        ↓
Publication to marketplace (stable or beta)
        ↓
Team installs with one command:
  ./setup-capabilities.sh /path/to/project
```

For a developer who wants to **use** a capability: copy a `.md` file into
`.claude/agents/` of their project. Claude Code recognises it automatically.

For a developer who wants to **contribute**: create a branch, run the scaffolding
script, write the prompt, open a PR. GitHub Actions comments immediately with
any issues to fix.

---

## Investment vs. Return

### Setup cost (already incurred)

The repository is operational, the first capabilities are available, and the governance
pipeline is configured. There are no additional infrastructure costs:
GitHub (already in use), Claude Code (already in use).

### Maintenance cost

| Activity | Frequency | Estimated effort |
|---|---|---|
| PR review for new capability | On demand | 30–60 min per PR |
| Update to existing capability | ~Monthly | 20–30 min per update |
| Onboarding new member to registry | Once | 30 min |

### Expected return

| Scenario | Estimated saving |
|---|---|
| Developer uses existing capability instead of building prompt from scratch | 20–40 min per task |
| Elimination of rework due to low-quality output | 1–2h per sprint per developer |
| Onboarding new member on Claude standards | 1–2 working days |
| Rapid identification of regressions in Claude's behaviour | Variable — avoids escalation |

For a team of 5 developers, with 2 capabilities used per task per day,
the estimated saving is in the order of **2–4 hours/week per person**.

---

## Current State and Roadmap

### Available today

| Capability | Tier | Description |
|---|---|---|
| `software-architect` | Stable | Architectural analysis, ADRs, trade-offs |
| `functional-analyst` | Stable | Requirements, use cases, business processes |
| `developer-java-spring` | Stable | Java/Spring Boot enterprise development |
| `technical-analyst` | Beta | Technical analysis, debt, security |
| `developer-python` | Beta | Python/FastAPI development |
| `developer-frontend` | Beta | Multi-framework frontend development |
| `code-reviewer` | Beta | Structured code review |
| `test-writer` | Beta | JUnit/pytest test writing |
| `debugger` | Beta | Bug diagnosis |
| `api-designer` | Beta | REST/OpenAPI API design and review |
| `documentation-writer` | Beta | Technical documentation |

### Proposed next steps

1. **Team adoption**: distribute capabilities to current active projects
2. **Feedback loop**: collect developer feedback after 2–4 weeks of use
3. **Beta → stable promotion**: stabilise beta capabilities based on feedback
4. **Domain capabilities**: develop capabilities specialised for our specific application
   domains (e.g. `developer-payments`, `analyst-compliance`, etc.)
5. **Usage metrics**: add lightweight telemetry to understand which capabilities
   are used most and where there are gaps

---

## In Summary

Claude Registry is not an experimental project — it is the governance infrastructure
for a tool the team is already using. The question is not "is it worth doing?"
but "do we want the value of Claude Code to remain fragmented per developer,
or to become a shared organisational asset?"

The registry answers this question concretely: Git repository, PR reviews,
versioning, automation. The same standards we apply to code, applied
to the behaviour of the AI that helps produce it.

---

*For technical details, operational documentation, and repository access:
`github.com/luketherose/claude-registry`*
