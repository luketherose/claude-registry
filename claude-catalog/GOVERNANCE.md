# Governance

## Roles

| Role | Responsibilities |
|---|---|
| **Capability Author** | Writes new subagents or updates existing ones; provides examples and evals |
| **Capability Reviewer** | Reviews PRs using `review-checklist.md`; approves or requests changes |
| **Catalog Maintainer** | Merges approved PRs, manages git tags, runs the publish process |
| **Consumer** | Uses published capabilities from `claude-marketplace/`; files issues for bugs or gaps |

A team member can hold multiple roles. There is no dedicated team required — the process
scales from one maintainer to many.

## Lifecycle states

```
draft → review → approved → released → published → deprecated
```

| State | Meaning | Where it lives |
|---|---|---|
| `draft` | Work in progress on a feature branch | `claude-catalog/agents/` (branch) |
| `review` | PR open, review in progress | `claude-catalog/agents/` (PR) |
| `approved` | PR merged to main | `claude-catalog/agents/` (main) |
| `released` | Git tag applied (`name@x.y.z`) | Git tag |
| `published` | Copied to marketplace tier | `claude-marketplace/stable/` or `beta/` |
| `deprecated` | No longer recommended; kept for compatibility | `claude-marketplace/stable/` with deprecation notice |

## Decision process

**Adding a new capability**: Author opens a PR with the subagent file, at least one
example, and at least one eval scenario. One reviewer approval required to merge.

**Modifying an existing capability**: PR with diff, updated changelog entry, and eval
verification. One approval required. If the change modifies model behavior significantly,
bump the minor version (e.g. 1.1.0 → 1.2.0).

**Breaking change**: Any change to `name` or `description` frontmatter fields is
breaking — it changes how Claude decides to invoke the subagent. These require a major
version bump and a migration note in CHANGELOG.md.

**Deprecating a capability**: Open a PR adding a deprecation notice to the subagent's
description field and to the marketplace catalog.json entry. Keep the file for 90 days
before removal to allow teams to migrate.

## What lives in this catalog vs. a project

**This catalog**: Horizontal, reusable capabilities that apply across multiple projects
and domains. Generic enough to be useful without modification.

**Project `.claude/agents/`**: Project-specific subagents, or local specializations of
catalog capabilities. A project may copy a catalog subagent and rename it
(e.g. `developer-java-spring-payments.md`) to add domain-specific constraints.

When a project-level specialization proves widely useful, it should be promoted back to
this catalog as a new capability.

## SLA expectations

- PR reviews: within 2 working days
- Bug reports on published capabilities: triaged within 5 working days
- Deprecated capabilities removed: 90 days after deprecation notice
