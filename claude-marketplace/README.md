# claude-marketplace

Published catalog of approved Claude Code shared capabilities.

This directory is the **distribution layer** of the claude-registry. It contains only
capabilities that have been reviewed, approved, tagged, and published from the
`../claude-catalog/` source directory.

**Do not edit files in this directory directly.** All changes must go through the
authoring and review process in `claude-catalog/`, then be published here via the
release process (`claude-catalog/release-process.md`).

---

## Directory structure

```
claude-marketplace/
  stable/         — Production-ready capabilities, safe to use in all projects
  beta/           — New or experimental capabilities, use with awareness
  docs/           — User-facing documentation
  scripts/        — Publish and promote automation
  catalog.json    — Master manifest of all published capabilities
```

---

## Tiers

| Tier | Meaning | When to use |
|------|---------|-------------|
| `stable` | Reviewed, tested, used in production | Default for all projects |
| `beta` | New or significantly updated, limited production use | Pilots and non-critical projects |

A capability moves from `beta` to `stable` when:
- It has been used in at least two projects
- No critical issues have been reported for 30+ days
- It has passed all eval scenarios in `claude-catalog/evals/`

---

## How to consume a capability

1. Browse this directory or read `catalog.json` to find the capability you need
2. Copy the `.md` file to your project's `.claude/agents/` directory
3. Claude Code will automatically make it available in your session
4. See `../claude-catalog/docs/quick-start.md` for detailed instructions

---

## Versioning

Each capability in `catalog.json` has a `version` field (SemVer). When a capability
is updated:
- PATCH (1.0.0 → 1.0.1): prompt fix, no behavior change
- MINOR (1.0.0 → 1.1.0): new behavior added, backward compatible
- MAJOR (1.0.0 → 2.0.0): breaking change (name, description, or tools changed)

For MAJOR changes, the previous version is kept in the catalog with a deprecation
notice for 90 days.

To pin a specific version in your project, use the git tag:
```bash
git show software-architect@1.0.0:claude-marketplace/stable/software-architect.md > .claude/agents/software-architect.md
```

---

## catalog.json

`catalog.json` is a **team convention**, not an official Claude Code format.
It is a manifest that records metadata about published capabilities for discoverability
and version tracking. There is no official Claude Code marketplace for custom subagents.
