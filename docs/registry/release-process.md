# Release process

A release publishes a **plugin**, not an individual capability. Versioning is semver on
`plugins/<plugin>/.claude-plugin/plugin.json`.

> Until August 2026 the registry versioned each capability separately and moved it between
> a `beta` and a `stable` tier in `catalog.json`. Both are gone. See "Old process" below.

## Step 1: determine the version bump

| Change | Bump |
|---|---|
| A capability's `name` or `description` changes | **major** |
| A capability is removed or moved to another plugin | **major** |
| The output format a consumer parses changes | **major** |
| A new capability is added to the plugin | **minor** |
| A capability gains behaviour without changing its contract | **minor** |
| Prose, examples, evaluations, reference material | **patch** |

`name` and `description` are contract, not documentation. They drive delegation and skill
activation, so changing them can silently break a consumer's routing. That is why they are
a major bump.

Removing or renaming a capability carries one more obligation: add the old name to the
`RETIRED` dict in `.github/scripts/validate_registry.py`, with what to use instead. CI then
fails on any reference left behind in `plugins/`, `wiki/`, `docs/`, `README.md` or
`CLAUDE.md`, so a dangling dispatch instruction cannot survive the release.

## Step 2: update the manifest and the changelog

Bump `"version"` in `plugins/<plugin>/.claude-plugin/plugin.json`, then add a
`docs/registry/CHANGELOG.md` entry in the form `[<plugin>@<version>] - YYYY-MM-DD` listing
every capability touched. Keep pending work under `[Unreleased]`.

## Step 3: validate

```bash
python3 .github/scripts/validate_registry.py
```

```bash
claude plugin validate .
```

```bash
bash hooks/tests/test-pre-tool-safety.sh
```

```bash
bash scripts/test-clean-install.sh
```

All four run in CI on the pull request, split across the `Validate marketplace` and
`Validate catalog` jobs. The validator fails on schema errors, frontmatter that does not
parse as YAML, an agent that invokes a skill without holding the `Skill` tool, an
oversized `SKILL.md`, a broken reference link, an unresolvable `${CLAUDE_PLUGIN_ROOT}`
path, a `references/...` path that neither resolves in its own plugin nor names its owner,
an eval file whose key set does not match or whose fixture does not resolve, a
`triggers.json` description that states the verdict or names a capability its query omits,
a workflow DAG that disagrees with the tree, a reference to a retired capability, an
unpinned MCP server spec, and a combined description budget over 15000 tokens. Over 13000
is a warning. The full gate table is in `how-to-write-a-capability.md` under "What CI
enforces".

## Step 4: merge and tag

Merging to `main` publishes. Consumers tracking `main` pick the change up in the background
on their next session, because the resolved version changed.

```bash
git tag dev-standards@1.3.0 && git push origin dev-standards@1.3.0
```

Tags are how a consumer pins a version, using `ref` in their marketplace source.

## Step 5: verify a clean install

Before announcing a release that changes structure, install it from scratch:

```bash
/plugin marketplace add luketherose/claude-registry
```

Then confirm, from a project directory and not from the registry, that the plugin's skills
appear under the `Skill` tool and that an agent which reads bundled material resolves its
`${CLAUDE_PLUGIN_ROOT}` paths. A path that resolves in the repository but not in an install
is precisely the failure this step exists to catch.

## Renaming or removing a plugin

Add a `renames` entry to `.claude-plugin/marketplace.json` so existing installs migrate
instead of breaking. `null` marks a plugin as removed.

```json
{
  "renames": {
    "quality-testing": "dev-standards",
    "old-plugin": null
  }
}
```

## Old process

<details>
<summary>Per-capability tiers and publish.sh (superseded 2026-08)</summary>

Each capability carried its own `version`, `tier` (`beta` or `stable`) and `status` in
`claude-marketplace/catalog.json`. A publish script copied the file from `claude-catalog/`
into the tier directory and updated the catalog. Promotion from beta to stable required
either 30 days plus use in two projects, or an explicit exemption stated in the PR
description.

The mechanism existed because there was no versioning primitive. Plugins have one, so
per-capability tiering was retired as unnecessary bookkeeping over 129 capabilities.

</details>
