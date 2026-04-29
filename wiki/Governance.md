<!--
audience: contributor
diataxis: explanation
last-verified: 2026-04-28
verified-against: 1e9445a
-->

# Governance

Roles, lifecycle, decision rules, and SLAs. The authoritative source is
[`claude-catalog/GOVERNANCE.md`](https://github.com/luketherose/claude-registry/blob/main/claude-catalog/GOVERNANCE.md);
this page presents the same content as a quick reference.

## Roles

| Role | Responsibilities |
|---|---|
| **Capability Author** | Writes new agents or skills; provides examples and evals |
| **Capability Reviewer** | Reviews PRs using `review-checklist.md`; approves or requests changes |
| **Catalog Maintainer** | Merges approved PRs; manages git tags; runs the publish process |
| **Consumer** | Uses published capabilities from `claude-marketplace/`; files issues for bugs and gaps |

A team member can hold multiple roles. The process scales from one
maintainer to many.

## Capability types

| Type | Description | Location | Invoked by |
|---|---|---|---|
| **Agent** | Performs a role (architect, developer, reviewer, …). Has behaviour and tool access. | `agents/` | Claude automatic delegation or `/agents` |
| **Skill** | Provides domain knowledge (standards, conventions, brand rules). Read-only, `haiku`. | `skills/` | Other agents via the `Agent` tool |

Skills are not visible to end users — they are implementation details
of the agents that depend on them. When a consumer installs an agent,
the setup script automatically installs its skill dependencies.

## Lifecycle

```
draft → review → approved → released → published → deprecated
```

| State | Meaning | Where it lives |
|---|---|---|
| `draft` | Work in progress on a feature branch | `claude-catalog/agents/` or `skills/` (branch) |
| `review` | PR open, review in progress | (PR) |
| `approved` | PR merged to main | `claude-catalog/` (main) |
| `released` | Git tag applied (`name@x.y.z`) | Git tag |
| `published` | Copied to marketplace tier | `claude-marketplace/stable/`, `beta/`, or `skills/` |
| `deprecated` | No longer recommended; kept for compatibility | Marketplace with deprecation notice |

## Decision rules

### Adding a new capability

- Author opens a PR with the `.md` file, at least one example, and at
  least one eval scenario.
- One reviewer approval required to merge.

### Modifying an existing capability

- PR with diff, updated changelog entry, and eval verification.
- One approval required.
- If the change modifies model behaviour significantly, bump the **minor**
  version (e.g. 1.1.0 → 1.2.0).

### Breaking changes

- Any change to `name` or `description` is breaking — it changes how
  Claude decides to invoke the subagent.
- Requires a **major** version bump and a migration note in
  `CHANGELOG.md`.

### Deprecating a capability

- PR adding a deprecation notice to the subagent's `description` field
  and to the `catalog.json` entry.
- Keep the file for **90 days** after the notice, then remove.

## Tier promotion

| Tier | Criteria for promotion |
|---|---|
| **draft → beta** | PR merged with examples and evals; CI green |
| **beta → stable** | Used in **at least two projects** AND **30 days** without critical issues |

Promotion is initiated by the Catalog Maintainer (PR moving the file
from `marketplace/beta/` to `marketplace/stable/` and updating the
`tier` field in `catalog.json`).

## Versioning

The registry follows **SemVer** with a per-capability scope.

| Change | Bump | Example |
|---|---|---|
| Bug fix, no behaviour change | PATCH | `1.0.0` → `1.0.1` |
| New behaviour, backwards-compatible | MINOR | `1.0.1` → `1.1.0` |
| `name` or `description` change | MAJOR | `1.1.0` → `2.0.0` |
| Tool list expansion (more capable) | MINOR | `1.0.0` → `1.1.0` |
| Tool list reduction (less capable) | MAJOR | `1.0.0` → `2.0.0` |

The git tag format is `name@MAJOR.MINOR.PATCH`. The repository's overall
"version" is implicit — there is no monorepo version tag because each
capability evolves independently.

## CI gates (sequential)

PRs go through two gates in order. The second only starts if the first
is green.

```
1. validate-catalog
   ├── valid YAML frontmatter (name, description, tools, model)
   ├── system prompt present with ## Role
   ├── skills without forbidden tools (Edit, Write, Bash, Agent)
   ├── CHANGELOG.md has an [Unreleased] entry
   └── check_marketplace_sync: every catalog file has a marketplace entry
                                                         BLOCKS PR if missing

2. validate-marketplace                  (only runs if gate 1 is green)
   ├── catalog.json valid (semver, tier, status, required fields)
   ├── every referenced file exists on disk
   ├── frontmatter name matches catalog entry name
   ├── path convention: {tier}/{name}.md or skills/{name}.md
   └── no orphan files in stable/, beta/, skills/
```

The gate-1 → gate-2 ordering exists so first-time contributors get a
clear "you forgot to publish" message before being blasted with details
about manifest schema.

## Catalog vs project specialisations

**This catalog** holds horizontal, reusable capabilities that apply
across projects — generic enough to be useful without modification.

**A project's `.claude/agents/`** holds project-specific subagents or
local specialisations. A project may copy a catalog subagent and rename
it (e.g. `developer-java-spring-payments.md`) to add domain-specific
constraints.

When a project-level specialisation proves widely useful, it should be
**promoted** back to this catalog as a new capability.

## SLAs

| Activity | Expected time |
|---|---|
| PR review | within 2 working days |
| Bug triage on published capabilities | within 5 working days |
| Deprecated capabilities removed | 90 days after deprecation notice |

## Catalog directory layout (advisory)

Agents and skills MAY be grouped into thematic subdirectories
(`agents/indexing/`, `skills/orchestrators/`). Validation scans
recursively. Marketplace stays **flat** regardless of catalog
grouping — this is what consumers see.

## Where governance ends and engineering begins

The CI gates are the line. Anything that the gates don't enforce is
soft governance — handled by review-checklist.md and reviewer judgment.
Anything that the gates do enforce is hard governance — there is no
override mechanism short of disabling CI, which is itself a governance
decision and never made silently.

## Related

- [Contributing](Contributing) — the workflow
- [Reference](Reference) — schema and conventions
- [Architecture](Architecture) — how the pieces connect
- [`claude-catalog/GOVERNANCE.md`](https://github.com/luketherose/claude-registry/blob/main/claude-catalog/GOVERNANCE.md) — authoritative source
