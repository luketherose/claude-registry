# Versioning Guide

This document explains the versioning strategy for published capabilities.

---

## Version format

Capabilities use Semantic Versioning: `MAJOR.MINOR.PATCH`

| Change | Version bump | Example |
|--------|-------------|---------|
| Prompt bug fix, no behavior change | PATCH | 1.0.0 → 1.0.1 |
| New behavior added, backward compatible | MINOR | 1.0.0 → 1.1.0 |
| `name` field changed | MAJOR | 1.0.0 → 2.0.0 |
| `description` field changed significantly | MAJOR | 1.0.0 → 2.0.0 |
| A tool removed from `tools` list | MAJOR | 1.0.0 → 2.0.0 |
| `model` changed | MINOR | 1.0.0 → 1.1.0 |

**Why does name or description change trigger MAJOR?**
The `name` field is used in `Agent(name)` permission rules in `settings.json`.
If a project has `"allow": ["Agent(software-architect)"]`, changing the name to
`software-architect-v2` breaks that rule silently. The `description` field is used
for automatic delegation — significant changes may cause different tasks to be routed
to the capability than before.

---

## Git tags

Every release is tagged in git:

```
software-architect@1.0.0
functional-analyst@1.2.0
developer-java@1.0.1
```

To see all releases of a capability:
```bash
git tag | grep "software-architect"
```

To view a specific historical version:
```bash
git show software-architect@1.0.0:claude-marketplace/stable/software-architect.md
```

To pin a specific version in your project:
```bash
git show software-architect@1.0.0:claude-marketplace/stable/software-architect.md \
  > .claude/agents/software-architect.md
```

Document pinned versions in your project's CLAUDE.md:
```markdown
## Pinned capabilities
- software-architect@1.0.0 — pinned pending review of v1.1.0 breaking output change
```

---

## Tier aliases

Instead of pinning exact versions, you can use tier aliases:

| Alias | Resolves to | Stability |
|-------|------------|-----------|
| `stable` | Latest stable version | High — suitable for production |
| `beta` | Latest beta version | Medium — suitable for pilots |

When you copy from `claude-marketplace/stable/`, you are using the `stable` alias
(always the latest stable). This is the recommended approach for most teams — copy
the latest stable and review the diff before adopting it.

---

## Deprecation policy

When a MAJOR version is released, the previous version:
1. Remains in `catalog.json` with `"status": "deprecated"`
2. Its file in `stable/` is updated with a deprecation notice in the description
3. It will be removed after 90 days from the deprecation date

Deprecated capabilities still work — they are not deleted immediately. But they will
not receive further updates, and consuming projects should migrate.

---

## changelog.json (future)

Currently, version history is in `../claude-catalog/CHANGELOG.md` and in `catalog.json`.
A machine-readable `changelog.json` is planned for a future version of the marketplace.
