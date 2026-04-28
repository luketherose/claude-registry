<!--
audience: end-user
diataxis: reference
last-verified: 2026-04-28
verified-against: 1e9445a
-->

# Changelog

The authoritative changelog lives in
[`claude-catalog/CHANGELOG.md`](https://github.com/luketherose/claude-registry/blob/main/claude-catalog/CHANGELOG.md).
This page summarises the format and links to recent highlights.

## Format

```
[name@version] - YYYY-MM-DD   for releases
[Unreleased]                  for pending changes
```

Each PR adds an entry under `[Unreleased]` before merging. Subsections:

- `### Added` — new capabilities, new behaviours
- `### Changed` — modifications to existing capabilities (with version bump)
- `### Fixed` — bug fixes
- `### Deprecated` — capabilities marked for removal in 90 days
- `### Removed` — capabilities removed (after the 90-day window)

## How to read entries

Each entry typically includes:

- the capability name and new version
- a one-sentence summary of the change
- the model
- key tools or behaviour
- (for fixes) a reference to the incident or PR

Example:

```markdown
- **`wiki-writer@0.1.0` (beta)** — sonnet, authors GitHub wikis
  organised around the Diataxis framework. Tools: Read, Grep, Glob,
  Bash, Write, Edit, WebFetch.
```

## Recent highlights

For the actual rolling list, read
[`CHANGELOG.md`](https://github.com/luketherose/claude-registry/blob/main/claude-catalog/CHANGELOG.md).
A few notable recent entries at the time of writing:

- **`wiki-writer@0.1.0`** — new agent for Diataxis-organised GitHub wikis
  with strict push-policy and File-writing rule safety rails.
- **Mermaid shell-injection hardening (2026-04-28)** — non-negotiable
  File-writing rule added across all phase pipelines after a Phase 2
  incident: 48 accidental files were created in a repo root by a
  sub-agent passing Mermaid syntax through a `Bash` heredoc. Now all
  content output goes through `Write`/`Edit` only.
- **TO-BE Testing pipeline (Phase 5)** — 9 new agents; the workflow now
  covers the full AS-IS → TO-BE → equivalence-validation cycle (Phases
  0–5). Final go-live gate produces `01-equivalence-report.md` for PO
  sign-off.
- **`exports-only` resume mode for Phases 1 and 2** — when the analysis
  is complete but the PDF/PPTX export is missing, the supervisor offers
  to regenerate just the missing exports without re-running the
  analysis pipeline.
- **Explicit skip / re-run / revise prompt at bootstrap** — extended to
  Phases 0, 3, and 4 (after originally landing in 1 and 2). When prior
  outputs are detected, the supervisor classifies the on-disk state and
  asks the user before doing anything.

## Versioning policy

See [Reference § Versioning](Reference#versioning) and
[Governance](Governance) for the rules. TL;DR:

| Change | Version bump |
|---|---|
| Fix, no behaviour change | PATCH |
| New behaviour, compatible | MINOR |
| `name` or `description` field change | MAJOR |
| Tool list expansion | MINOR |
| Tool list reduction | MAJOR |

A `description` change is **always** breaking because Claude uses it
for delegation routing.

## Why this page is just a pointer

The wiki page mirrors the format and links to the source. The
authoritative changelog stays in `claude-catalog/CHANGELOG.md` — that
file is the one CI validates (every PR must add an `[Unreleased]`
entry) and the one tied to git history. Duplicating the full changelog
in two places would inevitably drift.

## Related

- [`claude-catalog/CHANGELOG.md`](https://github.com/luketherose/claude-registry/blob/main/claude-catalog/CHANGELOG.md) — authoritative source
- [Governance](Governance) — versioning rules
- [Reference](Reference) — schemas and field definitions
