<!--
audience: contributor
diataxis: explanation
last-verified: 2026-08-30
verified-against: 8670a63
-->

# Governance

Roles, lifecycle, decision rules and service levels. The source documents live in
[`docs/registry/`](https://github.com/luketherose/claude-registry/tree/main/docs/registry);
this page is the navigable summary.

| Document | Covers |
|---|---|
| [`GOVERNANCE.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/GOVERNANCE.md) | Roles, lifecycle, decision rights |
| [`CONTRIBUTING.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/CONTRIBUTING.md) | Branching, review, merge |
| [`release-process.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/release-process.md) | Version bumps, tagging, clean-install verification |
| [`review-checklist.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/review-checklist.md) | What a reviewer checks |
| [`ANTI-PATTERNS.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/ANTI-PATTERNS.md) | What was tried and did not work |
| [`NAMING-CONVENTIONS.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/NAMING-CONVENTIONS.md) | Naming rules |
| [`evals-guide.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/evals-guide.md) | Writing evaluations |
| [`how-to-write-a-capability.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/how-to-write-a-capability.md) | The authoritative authoring guide |

## Roles

| Role | Responsibilities |
|---|---|
| **Capability author** | Writes the agent or skill, its evaluations and at least one example |
| **Capability reviewer** | Applies `review-checklist.md`, approves or requests changes |
| **Registry maintainer** | Merges approved pull requests, manages tags, drives releases |
| **Consumer** | Installs plugins, files issues for bugs and gaps |

One person can hold several roles. The process scales from one maintainer to many.

## Lifecycle

```
draft → review → approved → released → published → deprecated
```

| State | Meaning | Where it lives |
|---|---|---|
| `draft` | Work in progress | `plugins/<plugin>/` on a feature branch |
| `review` | Pull request open | The pull request |
| `approved` | Merged to `main` | `plugins/<plugin>/` on `main` |
| `released` | Plugin version bumped and tagged | `plugin.json` plus a `<plugin>@<version>` tag |
| `published` | On `main`, so every consumer picks it up in the background | `main` |
| `deprecated` | No longer recommended, still present for compatibility | Marked in the capability's `description` |

Merging to `main` publishes. Consumers tracking `main` pick the change up in the
background on their next session, because the resolved version changed. Consumers who
pinned a `ref` move when they change the ref.

## Decision rules

**Adding a capability.** A pull request carrying the capability file, at least one
example, and the evaluations. The authoring guide asks for three scenarios plus
`triggers.json`. One reviewer approval merges.

**Modifying a capability.** A pull request with the diff, a changelog entry, and
evaluation verification. One approval. A material behaviour change bumps the minor
version.

**Breaking change.** Any change to a `name` or a `description` is breaking, because both
drive routing. Major bump plus a migration note in the changelog.

**Deprecating a capability.** One pull request does three things together:

1. Adds a deprecation notice to the capability's `description`.
2. Adds an entry to `ANTI-PATTERNS.md` recording what was tried, why it failed, what
   replaced it, and under which conditions a retry would be valid. That entry is
   permanent and outlives the 90-day removal window.
3. Leaves the file in place for 90 days so teams can migrate.

Removing or renaming also means adding the old name to the `RETIRED` dict in
`.github/scripts/validate_registry.py`. CI then fails on any reference left behind, so a
dangling dispatch instruction cannot survive the release.

Step 2 is not optional. Without it the rationale disappears with the file and the next
contributor proposing the same capability has no precedent to learn from.

## Releases

A release publishes a **plugin**, not an individual capability.

| Change | Bump |
|---|---|
| A capability's `name` or `description` changes | major |
| A capability is removed or moved to another plugin | major |
| An output format a consumer parses changes | major |
| A new capability is added to the plugin | minor |
| A capability gains behaviour without changing its contract | minor |
| Prose, examples, evaluations, reference material | patch |

The procedure:

1. Determine the bump from the table.
2. Bump `version` in `plugins/<plugin>/.claude-plugin/plugin.json` and add a
   `docs/registry/CHANGELOG.md` entry as `[<plugin>@<version>] - YYYY-MM-DD`.
3. Validate locally.
4. Merge, then tag: `git tag dev-standards@1.3.0 && git push origin dev-standards@1.3.0`.
5. For a release that changes structure, install it from scratch and verify from a
   project directory rather than from the registry, that the skills appear under the
   `Skill` tool and that bundled paths resolve. A path that resolves in the repository but
   not in an install is exactly what this step catches.

Renaming or removing a plugin adds a `renames` entry to
`.claude-plugin/marketplace.json`, mapping the old name to the new one, or to `null` for
removed, so existing installs migrate instead of breaking.

## Hard governance and soft governance

The CI gates are the line.

**Hard governance** is what the gates enforce: manifest schema, frontmatter correctness,
`SKILL.md` length, reference resolution, retired names, MCP pinning, the description
budget, the hook regression matrix. There is no override short of disabling CI, which is
itself a governance decision and is never made silently. The full list is in
[Reference](Reference#ci-gates).

**Soft governance** is everything else, handled by `review-checklist.md` and reviewer
judgment: whether a `description` is precise enough to route on, whether the tool list is
minimal, whether the body is opinionated rather than generic, whether the output format
is defined exactly, and whether the capability overlaps one that already exists.

Before approving a new capability, a reviewer searches `ANTI-PATTERNS.md` for the
proposed role's keywords. A hit is not an automatic block, since a past failure may have
had causes that no longer apply, but the reviewer states in the discussion that the
**Do not retry unless** clause is satisfied.

## Where a capability belongs

**In the registry**: horizontal capabilities that apply across projects and domains, and
that are useful without modification.

**In the project**: project-specific context and project-only subagents. Prefer the
project's own `CLAUDE.md`, where the context applies to every capability at once, over a
subagent in `.claude/agents/`. A fork of a shared capability stops receiving updates and
drifts within a release or two. When a project specialisation proves useful beyond one
project, promote it here with a pull request, as a change to the existing capability or
as a new one.

Within the registry, a capability belongs to the plugin that already owns the skills it
needs. A skill in another plugin is only available when the consumer enabled that plugin
too.

## Service levels

| Activity | Expected |
|---|---|
| Pull request review | Within 2 working days |
| Triage of a bug on a published capability | Within 5 working days |
| Removal of a deprecated capability | 90 days after the notice |

## When documents disagree

The authoritative source is `how-to-write-a-capability.md`. The tiebreaker is the
validator, because it is what actually blocks a merge.

One known gap at the verified commit: `evals-guide.md` still describes evaluations as
`<capability-name>-eval.md` Markdown files. The shape actually in use, in all 73
evaluation directories, is `evals.json` plus `triggers.json`. See
[Reference](Reference#evaluations) for both schemas.

## Related

- [Contributing](Contributing): the mechanical workflow
- [Reference](Reference): the gates in full
- [Architecture](Architecture): how the CI flow fits together
