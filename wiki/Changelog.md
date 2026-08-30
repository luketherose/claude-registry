<!--
audience: end-user
diataxis: reference
last-verified: 2026-08-30
verified-against: c6c780a
-->

# Changelog

The authoritative changelog is
[`docs/registry/CHANGELOG.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/CHANGELOG.md).
This page explains the format and summarises what changed recently.

## Format

```
[<plugin>@<version>] - YYYY-MM-DD   a release
[Unreleased]                        pending work
```

Every pull request adds an entry under `[Unreleased]` before merging, in one of the usual
subsections: `Added`, `Changed`, `Fixed`, `Deprecated`, `Removed`.

Entries are written for the next contributor rather than for a release announcement. A
good one states what broke, why it was not caught, what the fix is, and what the
consequence is for authors. Several recent entries end with an explicit "Consequence for
contributors" sentence, which is the part worth reading.

## Recent highlights

### The plugin migration, 2026-08-29

The single largest change. The registry became an official Claude Code plugin
marketplace.

- **Distribution.** The two-directory layout collapsed into `plugins/`, with
  `.claude-plugin/marketplace.json` at the root and a `plugin.json` per plugin.
  Installation moved to `/plugin marketplace add` and `/plugin install`, and updates now
  arrive in the background.
- **Skills.** All skills converted from `haiku` subagents to Agent Skills at
  `plugins/<plugin>/skills/<name>/SKILL.md`. `model`, `tools` and `color` were removed
  from skill frontmatter. Six oversized skills were split into `references/`, putting
  every body under the 500-line guidance. Agents load skills with the `Skill` tool, and
  four agents preload one via the `skills:` frontmatter field.
- **Bundled references.** 123 references across 62 files were rewritten to
  `${CLAUDE_PLUGIN_ROOT}/references/**`. Those paths had not resolved at runtime, because
  the previous installer copied only agent files.
- **Description budget.** Combined subagent descriptions dropped from about 14200 tokens
  to about 10200, against the 15000-token platform ceiling. Enabling per plugin means a
  typical development session now loads roughly 1900 tokens of descriptions instead of
  all of them.
- **Frontmatter.** `model: inherit` for user-facing agents, `opus` plus `effort: high`
  for supervisors, challengers, auditors and deliberation personas, `sonnet` retained for
  fan-out workers. Supervisors gained `experimental.cacheTtl: 1h`.
- **Validator.** One `validate_registry.py` replaced the two previous scripts, adding
  gates on the description budget, `SKILL.md` length, frontmatter correctness, reference
  link resolution and `${CLAUDE_PLUGIN_ROOT}` resolution.
- **Removed.** Per-capability tiers, the in-house code reviewer (superseded by
  `pr-review-toolkit` from the official Anthropic marketplace), the old distribution
  directory in full, and the one-off bulk-edit scripts, which moved to `archive/`.

### Post-migration corrections, 2026-08-29 and 2026-08-30

- **52 capability paths still addressed the old category directories.** The migration
  flattened skills and agents out of their category folders, but in-body references across
  15 files still named them. A reference the runtime cannot resolve is a silent failure,
  so the sweep now reports zero. Capability names are flat.
- **Broken frontmatter now fails the build.** An unescaped quote in two descriptions
  stopped their frontmatter parsing as YAML. Claude Code loads such an agent with only the
  filename-derived name and drops every other field without an error. A new gate runs
  `yaml.safe_load` over every capability file.
- **The `Skill` tool gate stopped keying on a heading.** It matched a literal `## Skills`
  heading and so missed an agent that routes to skills in different words. It now matches
  how a body actually refers to skills.
- **`claude plugin validate` became a real gate.** The step had swallowed its exit code,
  so a plugin Claude Code itself rejects still produced a green check.
- **The safety hook's recursive-delete check was inverted.** It substring-matched one
  exact spelling, so several genuinely destructive forms passed while a harmless scratch
  delete was blocked. It now parses the command. A 24-case regression matrix runs in CI.
- **The retired-name gate widened to the pages people read first.** It scanned only
  `plugins/`, so the wiki and parts of `docs/` still listed capabilities that no longer
  exist. The scan now covers `plugins/`, `wiki/`, `docs/`, `bmad/`, `README.md` and
  `CLAUDE.md`, and matches on word boundaries rather than on backticks, so a mention in
  ordinary prose fails too.
- **One evaluation scenario schema.** Two incompatible shapes had accumulated in
  `evals.json`. All scenarios now use `{agent, query, files, expected_behavior}`, with
  `agent` equal to the eval directory name. `validate_evals()` locks both key sets, checks
  that every fixture path resolves, and fails on invalid JSON.
- **The trigger suites stopped grading themselves.** Descriptions named the routing winner
  in 364 of 365 cases, which let a nine-line keyword table with no semantics score 99.7
  percent. Every description now states what the query is about and never the verdict, and
  the same gate rejects a new one that names a capability its own query does not mention.
- **The agent-level workflow DAG is compared against the tree.** `workflow-dag-draft.json`
  had drifted with two removed capabilities listed and two existing supervisors missing.
  Because those cancelled out, the totals matched and a count check would have passed. The
  gate compares names.
- **A cross-plugin reference has to name its owner.** A `references/...` path in an agent
  body or a `SKILL.md` now has to resolve inside its own plugin, or the same line has to
  say which plugin owns it, and that plugin has to hold the file. Plugins install
  independently, so a relative path can never reach another one's tree.
- **A clean-machine install check runs in CI.** `scripts/test-clean-install.sh` installs
  every plugin into a throwaway config directory and asserts the result is usable, then
  asserts that uninstall leaves nothing behind.
- **Five substance rules are reported as warnings.** An oversized agent body, an
  unjustified `opus` pin, a long `SKILL.md` with no `references/`, a `when to use` heading
  inside a `SKILL.md`, and a long reference file with no `## Contents`. They do not fail
  the build. The audit that added them found the gated surface clean and the ungated one
  drifted.
- **MCP server specs must be pinned.** The root config pulled `@latest` and an unpinned
  Git ref while the plugin-level configs for the same servers were pinned, so the same
  server ran a different build depending on which config won. A new gate fails on either
  form.
- **A prohibition no longer swallows its own alternative.** Four bullets under
  `## What you never do` joined a prohibition to its recommended alternative with a colon,
  which reads as forbidding the alternative too. The convention for authors: under a
  negative heading, put the alternative in its own sentence.

## Versioning

A release publishes a plugin. See [Governance](Governance#releases) for the procedure.

| Change | Bump |
|---|---|
| A capability's `name` or `description` changes | major |
| A capability is removed or moved to another plugin | major |
| An output format a consumer parses changes | major |
| A new capability is added to the plugin | minor |
| A capability gains behaviour without changing its contract | minor |
| Prose, examples, evaluations, reference material | patch |

A `name` or `description` change is always breaking, because both drive delegation and
skill activation.

## Historical note: the pre-migration vocabulary

Terms you may still find in old branches, old pull requests or an outdated local
checkout. None of these exist on `main`.

| Old term | What replaced it |
|---|---|
| `claude-catalog/`, the development source directory | `plugins/<plugin>/`, a single tier |
| `claude-marketplace/`, the distribution directory | The same, published through the plugin marketplace |
| `claude-marketplace/catalog.json`, the hand-maintained manifest | `.claude-plugin/marketplace.json` plus one `plugin.json` per plugin |
| `setup-capabilities.sh`, the bash installer | `/plugin install`, or `scripts/install-local.sh` under a restrictive policy |
| Per-capability `beta` and `stable` tiers | Semver on the plugin |
| `validate_catalog.py` and `validate_marketplace.py` | One `.github/scripts/validate_registry.py` |
| Skills as `haiku` subagents invoked through the `Agent` tool | Agent Skills loaded with the `Skill` tool |

## Why this page is a summary

The rolling list stays in `docs/registry/CHANGELOG.md`, because that file is the one tied
to git history and the one a pull request must update. Mirroring it here in full would
guarantee drift.

## Related

- [`docs/registry/CHANGELOG.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/CHANGELOG.md): the authoritative source
- [Governance](Governance): versioning and release rules
- [Reference](Reference): schemas and gates
