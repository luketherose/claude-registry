# Release Process

This document covers how to tag a release in the catalog and publish it to the marketplace.

---

## Prerequisites

- PR is merged to `main`
- All items in `review-checklist.md` are satisfied
- CHANGELOG.md has an entry for the capability being released
- You have write access to the repository

---

## Step 1: Determine the version

Check the current version in `claude-marketplace/catalog.json` for the capability.
Apply version bump rules from `NAMING-CONVENTIONS.md`:

```bash
# See the current published version
cat claude-marketplace/catalog.json | grep -A3 '"name": "software-architect"'
```

---

## Step 2: Update CHANGELOG.md

Move the capability's changes from `[Unreleased]` to a versioned section:

```markdown
## [software-architect@1.1.0] - 2026-05-01

### Changed
- Enhanced trade-off output to include cost dimension
```

---

## Step 3: Apply git tag

```bash
git checkout main
git pull origin main
git tag software-architect@1.1.0
git push origin software-architect@1.1.0
```

For a coordinated catalog-wide release (all capabilities together):

```bash
git tag catalog@2026-04-19
git push origin catalog@2026-04-19
```

---

## Step 4: Run the publish script

The publish script copies the subagent file from `claude-catalog/agents/` to the
appropriate tier in `claude-marketplace/` and updates `catalog.json`.

```bash
# Publish to stable tier
./claude-marketplace/scripts/publish.sh software-architect 1.1.0 stable

# Publish to beta tier (for new or experimental capabilities)
./claude-marketplace/scripts/publish.sh technical-analyst 0.2.0 beta
```

The script will:
1. Copy the `.md` file to `claude-marketplace/{tier}/{name}.md`
2. Update the `version`, `tier`, and `published` fields in `catalog.json`
3. Commit the marketplace changes with message `release: {name}@{version}`

---

## Step 5: Verify the published capability

```bash
# Check the published file exists
ls claude-marketplace/stable/software-architect.md

# Check catalog.json is updated
cat claude-marketplace/catalog.json | grep -A8 '"name": "software-architect"'
```

---

## Step 6: Communicate to consumers

For minor/patch releases: update the team Slack/Teams channel with a brief note.

For major releases or breaking changes: send a notice with:
- What changed
- What teams need to do (update their local copy, check for conflicts with project overrides)
- Timeline for deprecating the old version if it's a replacement

---

## Promotion: beta → stable

When a `beta` capability has been used in at least two projects without critical issues
for at least 30 days:

```bash
./claude-marketplace/scripts/publish.sh capability-name 1.0.0 stable
```

Update `catalog.json` to change `"tier": "beta"` to `"tier": "stable"`.

---

## Rollback

If a published capability introduces regressions:

```bash
# Re-publish the previous version
git checkout software-architect@1.0.0 -- claude-catalog/agents/software-architect.md
./claude-marketplace/scripts/publish.sh software-architect 1.0.0 stable
git tag -d software-architect@1.1.0   # only if not yet distributed
```

Document the rollback in CHANGELOG.md under a new `[name@previous-version] - YYYY-MM-DD` entry.
