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
appropriate tier and topic in `claude-marketplace/` and updates `catalog.json`.

```bash
# Publish to stable tier (topic auto-resolved from the catalog source path)
./claude-marketplace/scripts/publish.sh software-architect 1.1.0 stable

# Publish to beta tier with an explicit topic
./claude-marketplace/scripts/publish.sh technical-analyst 0.2.0 beta --topic analysis
```

The script will:
1. Resolve the topic — `--topic` flag, then existing `catalog.json` entry, then catalog source path (`claude-catalog/agents/<topic>/<name>.md`)
2. Copy the `.md` file to `claude-marketplace/{tier}/{topic}/{name}.md`
3. Remove any stale copies of the same capability under the same tier (so a re-grouping never leaves orphan files behind)
4. Update the `version`, `tier`, `file`, and `published` fields in `catalog.json`
5. Commit the marketplace changes with message `release: {name}@{version}`

---

## Step 5: Verify the published capability

```bash
# Resolve the published path from catalog.json (single source of truth)
python3 -c "import json; print([c['file'] for c in json.load(open('claude-marketplace/catalog.json'))['capabilities'] if c.get('name')=='software-architect'][0])"

# Check the published file exists at the resolved path
ls claude-marketplace/stable/architecture/software-architect.md

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

A `beta` capability is eligible for promotion to `stable` when **either** of the
following two conditions is satisfied. The criteria are alternatives, not cumulative —
the second was added because the first is too slow when independent teams converge on
the same need.

### Criterion A — Time + adoption (default path)

The capability has been used in **at least two projects** without critical issues for
**at least 30 days** since the last beta release.

This is the conservative path. Use it when adoption is proceeding as expected and there
is no specific signal that the capability is more mature than the calendar implies.

### Criterion B — Convergence (fast path)

**Two or more independent project specializations** (under different projects'
`.claude/agents/`) have introduced the **same modification** to a beta capability —
typically the same added rule, the same removed constraint, or the same renamed output
section.

When this happens, the modification is no longer project-specific: it is part of the
capability's true behavior, and the original beta version is incomplete. Convergence
across projects is a stronger signal than time-on-shelf, and waiting out the 30-day
window only delays adopting a fix that two teams have already independently identified.

**How to verify convergence**:
1. Diff each project specialization against the beta capability and extract the changed
   lines.
2. Confirm that at least two specializations share the same change (textual or
   semantically equivalent — paraphrased rules count).
3. Cite both specializations in the promotion PR description, with the path under each
   project's `.claude/agents/` and the diff hunk that demonstrates the convergence.

A single project specialization is not sufficient — that is just a project override.
Convergence requires **two independent observations** of the same need.

### Promotion command (both criteria)

```bash
./claude-marketplace/scripts/publish.sh capability-name 1.0.0 stable
```

Update `catalog.json` to change `"tier": "beta"` to `"tier": "stable"`. Add a
`CHANGELOG.md` entry stating which criterion was used (A or B) — for Criterion B,
include the convergence evidence (the two project paths and the shared change).

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
