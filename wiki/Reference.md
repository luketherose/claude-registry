<!--
audience: contributor
diataxis: reference
last-verified: 2026-04-28
verified-against: 1e9445a
-->

# Reference

Schemas, fields, conventions. Look here when you need an exact answer
about a field name, an enum value, or a path convention.

## Subagent file format

A capability is a `.md` file with YAML frontmatter and a Markdown body
(the system prompt).

```markdown
---
name: your-capability-name
description: When and why Claude should use this subagent. Be precise.
tools: Read, Grep, Glob, Bash, Write, Edit
model: sonnet
---

The system prompt goes here. This is the full instruction set for the subagent.
It replaces the default Claude Code system prompt when the subagent is active.
```

### Required frontmatter fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Lowercase, hyphens only. Must match the filename without `.md`. |
| `description` | string | Controls when Claude delegates to this subagent. The most critical field; start with "Use when" or "Use for". |

### Optional frontmatter fields

| Field | Type | Example | Notes |
|---|---|---|---|
| `tools` | string | `Read, Grep, Glob, Bash` | Comma-separated. Omitting inherits all tools. Prefer explicit allowlists. |
| `disallowedTools` | string | `Write, Edit` | Tools to explicitly deny. |
| `model` | string | `sonnet`, `opus`, `haiku` | Default: inherits from parent session. Use `opus` only when reasoning depth justifies it. |
| `maxTurns` | integer | `10` | Limits agentic turns. Useful for bounded tasks. |
| `color` | string | `blue`, `green`, `red`, `cyan`, `yellow` | Visual indicator in the Claude UI. |

Unrecognised fields are silently ignored — do not add fields outside
this list.

## Tool reference

| Tool | Purpose | Grant when |
|---|---|---|
| `Read` | Read files | Always grant to analysis roles |
| `Grep` | Search code and content | Always grant to analysis roles |
| `Glob` | Find files by pattern | Always grant to analysis roles |
| `Write` | Create new files | When producing deliverables |
| `Edit` | Modify existing files | Developer roles only |
| `Bash` | Run shell commands | Developer and debugger roles; scope carefully |
| `WebFetch` | Fetch external URLs | Architecture/research; risks for sensitive projects |
| `WebSearch` | Web search | Research roles only |
| `Agent` | Spawn other subagents | Orchestrator roles only |

### Standard tool profiles

| Profile | Tools | Use for |
|---|---|---|
| Read-only analyst | `Read, Grep, Glob` | Analysis-only roles |
| Read + report | `Read, Grep, Glob, Write` | Analysis with written output |
| Full developer | `Read, Edit, Write, Bash, Grep, Glob` | Code writing and execution |
| Research | `Read, Grep, Glob, WebFetch` | Architecture / design with web lookup |
| Skill | `Read` only | Knowledge providers (mandatory) |

## Catalog manifest

`claude-marketplace/catalog.json` is the authoritative manifest of every
distributable capability. It is read by `setup-capabilities.sh` and
validated by the marketplace CI gate.

### Top-level fields

```json
{
  "_comment": "Team convention — not an official Claude Code format.",
  "version": "1.0",
  "generated": "2026-04-28",
  "repository": "claude-registry",
  "capabilities": [ ... ]
}
```

### Capability entry fields

```json
{
  "name": "developer-java-spring",
  "version": "1.0.0",
  "tier": "stable",
  "type": "agent",
  "status": "active",
  "description": "...",
  "file": "stable/developer-java-spring.md",
  "dependencies": ["java-spring-standards", "testing-standards"],
  "tools": ["Read", "Edit", "Write", "Bash", "Grep", "Glob"],
  "model": "sonnet",
  "tags": ["java", "spring", "backend"],
  "published": "2026-04-19",
  "changelog": "Initial release"
}
```

| Field | Type | Allowed values | Notes |
|---|---|---|---|
| `name` | string | matches filename | Authoritative identifier |
| `version` | semver | `MAJOR.MINOR.PATCH` | Bumped per [Governance](Governance) |
| `tier` | enum | `stable`, `beta`, `skill` | Controls marketplace folder |
| `type` | enum | `agent`, `skill` | Determines validation rules |
| `status` | enum | `active`, `deprecated` | Deprecated kept for 90 days |
| `file` | string | `{tier}/{name}.md` (or `skills/{name}.md`) | Path is **flat** in marketplace |
| `dependencies` | string[] | skill names | Auto-installed by setup script |
| `tools` | string[] | tool names | Mirrors agent's frontmatter |
| `model` | enum | `sonnet`, `opus`, `haiku` | Mirrors agent's frontmatter |
| `published` | date | ISO YYYY-MM-DD | Updated on every publish |
| `changelog` | string | one-liner | Summarised in CHANGELOG.md `[Unreleased]` |

### Path conventions

| File location | Path in `catalog.json` |
|---|---|
| `claude-catalog/agents/foo.md` (top-level) | `file: "stable/foo.md"` or `file: "beta/foo.md"` |
| `claude-catalog/agents/indexing/foo.md` (subdirectory) | still **flat**: `file: "beta/foo.md"` — marketplace stays flat regardless of catalog grouping |
| `claude-catalog/skills/orchestrators/foo.md` | `file: "skills/foo.md"` |

The catalog directory layout is a developer convenience; the marketplace
layout is the contract with consumers.

## Frontmatter contract for sub-agent outputs

Sub-agents in the multi-phase refactoring pipelines write Markdown files
with a standardised frontmatter for traceability:

```yaml
---
agent: <sub-agent-name>
generated: <ISO-8601 timestamp>
sources:
  - .indexing-kb/<path>#<anchor-or-line>
  - docs/analysis/01-functional/<path>
  - <repo>/<source-path>:<line>
confidence: high | medium | low
status: complete | partial | needs-review | blocked
---
```

For findings with stable IDs (risks, vulnerabilities, bottlenecks,
dependencies, integrations, security findings), each item has its own
YAML header:

```yaml
id: RISK-NN | VULN-NN | PERF-NN | DEP-NN | INT-NN | SEC-NN | ST-NN
title: <human title>
severity: critical | high | medium | low | info
related: [<other-ids>, <feature-id>, <use-case-id>]
sources: [<.indexing-kb/... or repo/...:line>]
status: draft | needs-review | blocked
```

## Stable ID prefixes (sub-agent outputs)

| Prefix | Domain | Owner agent |
|---|---|---|
| `RISK-NN` | Generic risk in risk register | `risk-synthesizer` |
| `VULN-NN` | Library vulnerability (CVE / GHSA) | `dependency-security-analyst` |
| `PERF-NN` | Performance hotspot | `performance-analyst` |
| `DEP-NN` | Dependency entry | `dependency-security-analyst` |
| `INT-NN` | External integration | `integration-analyst` |
| `SEC-NN` | OWASP / threat-model finding | `security-analyst` |
| `ST-NN` | State / runtime finding | `state-runtime-analyst` |
| `RISK-DA-NN` | Data-access risk | `data-access-analyst` |
| `RISK-INT-NN` | Integration risk | `integration-analyst` |
| `S-NN` | Screen | `ui-surface-analyst` (Phase 1) |
| `UC-NN` | Use case | `user-flow-analyst` (Phase 1) |
| `BC-NN` | Bounded context | `decomposition-architect` (Phase 4) |
| `ADR-NNN` | Architecture decision record | `decomposition-architect`, `hardening-architect`, `api-contract-designer` |
| `BUG-NN` | AS-IS bug found in baseline | `baseline-runner` (Phase 3) |
| `TBUG-NN` | TO-BE bug found in equivalence | `tobe-test-runner` (Phase 5) |

## CI gate references

### `validate-catalog`

Located at [`.github/scripts/validate_catalog.py`](https://github.com/luketherose/claude-registry/blob/main/.github/scripts/validate_catalog.py).
Runs first; blocks merge if it fails.

Checks:
- valid YAML frontmatter (`name`, `description`, `tools`, `model`)
- system prompt present with `## Role`
- skills do not declare forbidden tools (`Edit`, `Write`, `Bash`, `Agent`)
- `claude-catalog/CHANGELOG.md` has an `[Unreleased]` section with at
  least one entry
- every agent / skill in the catalog has an entry in
  `claude-marketplace/catalog.json` (this is the most common failure
  for first-time contributors)

### `validate-marketplace`

Located at [`.github/scripts/validate_marketplace.py`](https://github.com/luketherose/claude-registry/blob/main/.github/scripts/validate_marketplace.py).
Runs only if `validate-catalog` is green.

Checks:
- `catalog.json` valid (semver, tier, status, required fields)
- every referenced file exists on disk
- file frontmatter `name` matches the catalog entry name
- path convention: `{tier}/{name}.md` or `skills/{name}.md`
- no orphan files in `stable/`, `beta/`, `skills/`

## Naming conventions

- **Capability name**: `kebab-case`, no version (`developer-java-spring`,
  not `developer-java-spring-v1`).
- **Filename**: matches `name` exactly, with `.md` extension.
- **Branch name** (when contributing): `add/<name>` for new
  capabilities, `update/<name>` for changes, `fix/<topic>` for bug
  fixes.
- **Git tag**: `name@MAJOR.MINOR.PATCH` (e.g.
  `software-architect@1.0.0`).

## Versioning

| Change | Version bump | Example |
|---|---|---|
| Bug fix, no behaviour change | PATCH | `1.0.0` → `1.0.1` |
| New behaviour, backwards-compatible | MINOR | `1.0.1` → `1.1.0` |
| `name` or `description` field change | MAJOR | `1.1.0` → `2.0.0` |
| Tool list expansion (more capable agent) | MINOR | `1.0.0` → `1.1.0` |
| Tool list reduction (less capable) | MAJOR | `1.0.0` → `2.0.0` |

A `description` change is **always** breaking because it changes how
Claude decides to invoke the subagent.

## Related

- [Architecture](Architecture) — how the pieces connect
- [Contributing](Contributing) — the workflow for adding a capability
- [Governance](Governance) — lifecycle, decision rules, SLAs
