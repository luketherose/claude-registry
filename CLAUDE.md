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
claude-catalog/agents/foo.md   ── publish script ──→   claude-marketplace/beta/foo.md
claude-catalog/skills/bar.md   ── publish script ──→   claude-marketplace/skills/bar.md
                                                         claude-marketplace/catalog.json  ← manifest
```

To publish: `./claude-marketplace/scripts/publish.sh <name> <version> <tier>`

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
   ├── path convention: {tier}/{name}.md or skills/{name}.md
   └── no orphan files in stable/, beta/, skills/
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

This repository has its own capabilities installed in `.claude/agents/`.
Use them when appropriate:

- `document-creator` — to regenerate `guida-operativa.pdf`
- `presentation-creator` — to regenerate `pitch-claude-registry.pptx`
- `software-architect` — for architectural decisions on the registry itself
- `documentation-writer` — to update governance `.md` files and guides

---

## Conventions

- Language: English for all `.md` files and capability system prompts
- Capability file names: `kebab-case`, no version in the name (`developer-java-spring.md`, not `developer-java-spring-v1.md`)
- Versioning: SemVer with git tag `name@MAJOR.MINOR.PATCH`
- Skills: `model: haiku`, `tools: Read` — do not add other tools without justification in the PR
- Agents using `model: opus`: must either (a) be the meta-orchestrator (auto-allowed), or (b) carry a `model_justification:` frontmatter field of at least 40 chars explaining the reasoning-depth requirement. Without one, the validator emits a warning asking for justification in the PR description. Inline frontmatter is preferred — the rationale stays with the agent definition.
- **Catalog directory layout**: agents and skills MAY be grouped into thematic subdirectories (e.g., `agents/indexing/`, `skills/orchestrators/`, `skills/documentation/`). Validation scans recursively (`rglob`).
- **Marketplace directory layout**: stays FLAT regardless of catalog grouping. Files live at `stable/<name>.md`, `beta/<name>.md`, or `skills/<name>.md` directly. The `file` field in `catalog.json` reflects this flat path.
