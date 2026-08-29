# Governance

## Roles

| Role | Responsibilities |
|---|---|
| **Capability Author** | Writes new agents or skills; provides examples and evals |
| **Capability Reviewer** | Reviews PRs using `review-checklist.md`; approves or requests changes |
| **Registry Maintainer** | Merges approved PRs, bumps plugin versions, manages git tags |
| **Consumer** | Installs plugins with `/plugin install <plugin>@claude-registry`; files issues for bugs or gaps |

A team member can hold multiple roles. No dedicated team is required. The process scales
from one maintainer to many.

## Capability types

| Type | Description | Location | Invoked by |
|---|---|---|---|
| **Agent** | Performs a role (architect, developer, analyst). Runs in its own context window with its own tool set. | `plugins/<plugin>/agents/` | Claude automatic delegation, or the user via `/agents` |
| **Skill** | Provides domain knowledge (standards, conventions, brand rules) loaded into the current context. Takes no autonomous action. | `plugins/<plugin>/skills/<name>/SKILL.md` | An agent, via the `Skill` tool, or preloaded through the `skills:` frontmatter field |

A consumer does not install a skill. Skills ship inside the plugin that owns them, and
Claude loads one when the task matches its description, or when an agent asks for it by
name. This is why a capability and the skills it always needs belong to the same plugin.

## Lifecycle states

```
draft → review → approved → released → published → deprecated
```

| State | Meaning | Where it lives |
|---|---|---|
| `draft` | Work in progress on a feature branch | `plugins/<plugin>/` (feature branch) |
| `review` | PR open, review in progress | (PR) |
| `approved` | PR merged to main | `plugins/<plugin>/` (main) |
| `released` | Plugin version bumped, git tag applied (`<plugin>@x.y.z`) | `plugins/<plugin>/.claude-plugin/plugin.json`, git tag |
| `published` | On `main`, so every consumer picks it up in the background | `main` |
| `deprecated` | No longer recommended; kept for compatibility | In place, with a deprecation notice in the `description` |

## Decision process

**Adding a new capability**: Author opens a PR with the subagent file, at least one
example, and at least one eval scenario. One reviewer approval required to merge.

**Modifying an existing capability**: PR with diff, updated changelog entry, and eval
verification. One approval required. If the change modifies model behavior significantly,
bump the minor version (e.g. 1.1.0 → 1.2.0).

**Breaking change**: Any change to a `name` or `description` frontmatter field is
breaking, because it changes how Claude decides to invoke the capability. These require a
major version bump on the plugin and a migration note in CHANGELOG.md.

**Deprecating a capability**: Open a PR that does three things together:
1. Adds a deprecation notice to the capability's `description` field and to the owning
   plugin's `plugin.json` manifest.
2. Adds an entry to `ANTI-PATTERNS.md` recording **what was tried, why it failed, what
   replaced it, and under which conditions a retry would be valid**. This entry is
   permanent. It survives the 90-day removal window.
3. Keeps the file in place for 90 days before removal to allow teams to migrate.

At removal, a fourth step becomes mandatory: add the name to the `RETIRED` dict in
`.github/scripts/validate_registry.py` with what to use instead. CI then fails on any
reference left behind, so the removal cannot leave a dangling dispatch instruction in the
docs or the wiki.

Step 2 is mandatory. Without it, the rationale disappears with the file and the next
contributor proposing a similar capability has no way to learn from the precedent.

## What lives in this registry vs. a project

**This registry**: Horizontal, reusable capabilities that apply across multiple projects
and domains. Generic enough to be useful without modification.

**The project's own `CLAUDE.md` and `.claude/agents/`**: project-specific context and
project-only subagents. Prefer putting project context in `CLAUDE.md`, where it applies to
every capability at once. A fork of a registry capability stops receiving updates and
drifts within a release or two.

When a project-level specialization proves widely useful, promote it back here as a change
to the capability, or as a new one.

## SLA expectations

- PR reviews: within 2 working days
- Bug reports on published capabilities: triaged within 5 working days
- Deprecated capabilities removed: 90 days after deprecation notice
