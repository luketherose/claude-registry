<!--
audience: mixed
diataxis: explanation
last-verified: 2026-08-30
verified-against: c6c780a
-->

# Claude Registry

The team's Claude Code **plugin marketplace**. Agents, skills and their supporting
reference material are published as plugins that install and update themselves.

## TL;DR

- **What it is.** A marketplace manifest at `.claude-plugin/marketplace.json` plus six
  plugins under `plugins/`, holding 86 subagents and 46 Agent Skills.
- **What it gives you.** Consistent expert behaviour across projects (Java/Spring,
  Python, Go, Rust, Kotlin, C#, PHP, Ruby, Angular, React, Vue, Qwik, PostgreSQL,
  REST design, testing, documentation, replatforming pipelines) without every project
  re-inventing prompts.
- **How you install it.** `/plugin marketplace add luketherose/claude-registry`, then
  `/plugin install <plugin>@claude-registry`. Where enterprise policy blocks adding
  marketplaces, `scripts/install-local.sh` copies the same material into `~/.claude/`.
- **How you contribute.** Branch, write the evaluations first, add the capability under
  `plugins/<plugin>/`, run `python3 .github/scripts/validate_registry.py`, open a PR.

## Plugins

| Plugin | Agents | Skills | Scope |
|---|---:|---:|---|
| [`replatforming`](Capability-catalog#replatforming) | 58 | 4 | Five-phase AS-IS to TO-BE replatforming pipeline |
| [`dev-standards`](Capability-catalog#dev-standards) | 12 | 29 | Language and framework standards, developer agents, tests, debugging |
| [`deliberation`](Capability-catalog#deliberation) | 7 | 0 | Multi-agent debate engine for high-stakes decisions |
| [`docs-branding`](Capability-catalog#docs-branding) | 4 | 7 | Documentation authoring and Accenture-branded deliverables |
| [`analysis-architecture`](Capability-catalog#analysis-architecture) | 5 | 3 | Architecture, requirements, technical analysis, orchestration |
| [`caveman`](Capability-catalog#caveman) | 0 | 3 | Terse output style for prose, commits and reviews |

Enable only what a project needs. Every enabled subagent description competes for the
same 15000-token delegation budget, and a smaller enabled set produces sharper routing.

## Where to go next

| You want to... | Read |
|---|---|
| Install a plugin right now | [Quick start](Quick-start) |
| Install without the marketplace, under enterprise policy | [Installation](Installation) |
| Understand what this thing actually is | [What is Claude Registry](What-is-Claude-Registry) |
| See every agent and skill that ships today | [Capability catalog](Capability-catalog) |
| Add your own capability | [Contributing](Contributing) |
| Understand how the pieces fit | [Architecture](Architecture) |
| Look up a field, a gate or a path | [Reference](Reference) |
| Read the review and release rules | [Governance](Governance) |
| Find out why something works the way it does | [FAQ](FAQ) |

## Status

The registry migrated to the official Claude Code plugin marketplace format on
2026-08-29. Versioning is semver on each plugin, declared in
`plugins/<plugin>/.claude-plugin/plugin.json`. There are no per-capability tiers.
See [Changelog](Changelog) for what the migration changed.

## Quick links

- Source repository: [github.com/luketherose/claude-registry](https://github.com/luketherose/claude-registry)
- Authoring guide: [`docs/registry/how-to-write-a-capability.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/how-to-write-a-capability.md)
- Version floors per feature: [`docs/registry/version-requirements.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/version-requirements.md)
- Operational guide (Italian, PDF): `guida-operativa.pdf` in the repository root
