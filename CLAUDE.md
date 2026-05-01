# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Common commands

```bash
# Validate catalog locally (runs the same check as CI gate 1)
python3 .github/scripts/validate_catalog.py

# Validate marketplace locally (runs the same check as CI gate 2)
python3 .github/scripts/validate_marketplace.py

# Scaffold a new agent or skill
./claude-catalog/scripts/new-capability.sh --type agent my-agent-name
./claude-catalog/scripts/new-capability.sh --type skill my-skill-name

# Publish a capability from catalog to marketplace
./claude-marketplace/scripts/publish.sh <name> <version> <tier>   # tier: stable | beta

# Install all capabilities globally (updates ~/.claude/agents/)
./claude-catalog/scripts/setup-capabilities.sh --global
```

---

## Primary rule: always update documentation

**Every time you make a change to this repository, update the documentation too.**

In practice:

| Type of change | What to update |
|----------------|----------------|
| New agent (`agents/*.md`) | `README.md` (capability table), `claude-catalog/docs/quick-start.md` (table), `CHANGELOG.md` ([Unreleased]), `catalog.json` |
| New skill (`skills/*.md`) | `README.md` (skill table), `CHANGELOG.md` ([Unreleased]), `catalog.json` (skill entry + dependencies of agents that use it) |
| Changed agent behaviour | `CHANGELOG.md` ([Unreleased] with version bump), `catalog.json` (version) |
| Changed script (`scripts/`) | Header comment in the script (usage), `guida-operativa.pdf` if UX changes |
| Changed governance or process | Corresponding `.md` file in `claude-catalog/` |
| Any significant change | `guida-operativa.pdf` and `pitch-claude-registry.pptx` if content becomes stale |

**Rule for `CHANGELOG.md`**: every PR must have an entry under `[Unreleased]` before it is opened. If the entry is missing, add it before pushing.

**Rule for `catalog.json`**: the file at `claude-marketplace/catalog.json` is the authoritative manifest. When a capability changes (version, dependencies, description), update `catalog.json` too.

---

## How catalog and marketplace work together

This repository has two areas with distinct responsibilities:

| Area | Purpose | Who modifies it |
|------|---------|-----------------|
| `claude-catalog/` | Development source — capabilities are written, reviewed, and versioned here | Developers, PRs |
| `claude-marketplace/` | Distribution — contains only approved capabilities, copied from the catalog | Publish script only, never by hand |

**Fundamental rule**: a capability is not "available" until it is published to the marketplace. Modifying only the catalog is not enough.

### Publish flow

```
claude-catalog/agents/<topic>/foo.md  ── publish script ──→  claude-marketplace/beta/<topic>/foo.md
claude-catalog/skills/<topic>/bar.md  ── publish script ──→  claude-marketplace/skills/<topic>/bar.md
                                                                claude-marketplace/catalog.json  ← manifest
```

To publish: `./claude-marketplace/scripts/publish.sh <name> <version> <tier> [--topic <topic>]`

The publish script auto-resolves `<topic>` from (1) the `--topic` flag, (2) the
existing `catalog.json` entry, (3) the catalog source path
(`claude-catalog/agents/<topic>/<name>.md`), in that order. It also removes any
stale copies of the capability under the same tier (e.g. left behind by a
re-grouping) so no orphan file remains in the marketplace.

### CI validation flow (sequential)

PRs go through two gates in sequence — the second only starts if the first is green:

```
1. validate-catalog   — checks files in claude-catalog/
   ├── valid YAML frontmatter (name, description, tools, model)
   ├── system prompt present with ## Role section
   ├── skills without forbidden tools (Edit, Write, Bash, Agent)
   ├── CHANGELOG.md has an [Unreleased] entry
   └── check_marketplace_sync: every agent/skill in the catalog
       must have an entry in claude-marketplace/catalog.json  ← BLOCKS if missing

2. validate-marketplace   — (only if validate-catalog is green)
   ├── catalog.json valid (semver, tier, status, required fields)
   ├── every referenced file exists on disk
   ├── file frontmatter name matches the catalog entry name
   ├── path convention: {tier}/<topic>/{name}.md or skills/<topic>/{name}.md
   │     (flat {tier}/{name}.md and skills/{name}.md still accepted —
   │      see "Marketplace directory layout" below)
   └── no orphan files in stable/, beta/, skills/ (recursive)
```

**Practical consequence**: if you open a PR that adds capabilities to the catalog without publishing them to the marketplace, `validate-catalog` blocks the PR before `validate-marketplace` even starts.

---

## Repository structure

- `claude-catalog/` — development source (agents, skills, governance documents)
- `claude-marketplace/` — distribution (approved files only; do not modify directly)
- `guida-operativa.pdf` — Accenture-branded operational guide (regenerate with `document-creator`)
- `pitch-claude-registry.pptx` — Accenture-branded pitch deck (regenerate with `presentation-creator`)

---

## Capabilities available in this project

The catalog currently holds **76 agents** and **41 skills**. The ones most useful while working on the registry itself:

- `registry-auditor` — audits agents/skills/CLAUDE.md against Anthropic's official rubrics; produces a structured report with grade, registry-wide patterns, top files to rewrite, and quick wins. Read-only.
- `code-reviewer` — for PR review on the registry source itself
- `document-creator` — to regenerate `guida-operativa.pdf`
- `presentation-creator` — to regenerate `pitch-claude-registry.pptx`
- `software-architect` — for architectural decisions on the registry itself
- `documentation-writer` — to update governance `.md` files and guides
- `wiki-writer` — to keep the GitHub wiki in sync with capability changes

The full catalog is in `claude-marketplace/catalog.json`; the README capability table is the human-readable index.

---

## Conventions

- Language: English for all `.md` files and capability system prompts
- Capability file names: `kebab-case`, no version in the name (`developer-java-spring.md`, not `developer-java-spring-v1.md`)
- Versioning: SemVer with git tag `name@MAJOR.MINOR.PATCH`
- Skills: `model: haiku`, `tools: Read` — do not add other tools without justification in the PR
- Agents using `model: opus`: must either (a) be the meta-orchestrator (auto-allowed), or (b) carry a `model_justification:` frontmatter field of at least 40 chars explaining the reasoning-depth requirement. Without one, the validator emits a warning asking for justification in the PR description. Inline frontmatter is preferred — the rationale stays with the agent definition.
- **Skill description rubric (Anthropic `skill-development`)**: every skill description must (a) start with `This skill should be used when…` (or the pushy variant `ALWAYS use this skill when…` for skills Claude tends to undertrigger), (b) include 2–3 verbatim trigger phrases between double quotes, (c) carry an explicit `Do not use…` (or equivalent) scope-out clause to disambiguate sibling skills. Enforced by `validate_catalog.py`.
- **Agent rubric (Anthropic `agent-development`)**: every agent body should contain a `## When to invoke` section listing 2–4 worked scenarios as prose bullets and a `Do NOT use this agent for:` line. Body length should stay under 10 000 chars; supervisors with phase-by-phase content should extract per-phase narrative into `claude-catalog/docs/<topic>/`. Both checks emit warnings in `validate_catalog.py` (gradual rollout — not yet errors).
- **Color frontmatter**: only `red`, `blue`, `green`, `yellow`, `magenta`, `cyan` are accepted (Anthropic spec). `purple`, `orange`, `pink` are not valid.
- **Catalog directory layout**: agents and skills are grouped into thematic subdirectories (e.g., `agents/indexing/`, `agents/orchestration/`, `agents/quality/`, `skills/frontend/angular/`, `skills/orchestrators/`, `skills/documentation/`). Single-file root entries are tolerated for transitional states but should be moved into a topic folder when the topic gains a second sibling. Validation scans recursively (`rglob`).
- **Marketplace directory layout**: mirrors the catalog grouping. Files live at `stable/<topic>/<name>.md`, `beta/<topic>/<name>.md`, or `skills/<topic>[/<sub>]/<name>.md`. The `file` field in `catalog.json` is the single source of truth — both the publish script and `setup-capabilities.sh` read it directly. Both flat paths (`<tier>/<name>.md`, `skills/<name>.md`) and nested paths are accepted by the validator, but new capabilities should always be published into a topic folder.
- **Marketplace topics** (used as folder names): for agents — `analysis`, `api`, `architecture`, `baseline-testing`, `developers`, `documentation`, `functional-analysis`, `indexing`, `orchestration`, `quality`, `refactoring-tobe`, `technical-analysis`, `tobe-testing`. For skills — `analysis`, `api`, `backend`, `branding`, `database`, `documentation`, `frontend` (with framework subfolders `angular/`, `react/`, `qwik/`, `vue/`, `vanilla/`), `orchestrators`, `python`, `refactoring`, `testing`, `utils`. Add a new topic folder when a third capability of the same kind appears; until then place the capability in the closest existing folder rather than spawning a one-off topic.
