# CLAUDE.md

Guidance for Claude Code when working in the `claude-registry` repository.

This repo is a **Claude Code plugin marketplace**. It publishes the team's agents, skills
and supporting material as plugins that teammates install with `/plugin install`.

## Common commands

```bash
# Validate the whole registry (same gate as CI)
python3 .github/scripts/validate_registry.py

# Validate marketplace and plugin manifests with the official CLI
claude plugin validate .

# Scaffold a new agent or skill
./scripts/new-capability.sh

# Install this marketplace locally for development
claude plugin marketplace add .
```

## Primary rule: always update documentation

Any change to a capability updates, in the same commit:

1. The capability file itself
2. `docs/registry/CHANGELOG.md`
3. The plugin's `version` in `plugins/<plugin>/.claude-plugin/plugin.json` when behaviour changes
4. `README.md` when the capability roster changes
5. `docs/registry/how-to-write-a-capability.md` when a convention changes

Never leave a convention change undocumented. The next author will not infer it.

## Repository structure

```
.claude-plugin/marketplace.json   the marketplace manifest, one entry per plugin
plugins/<plugin>/                 the distribution unit
  .claude-plugin/plugin.json      name, description, version, author, component wiring
  agents/                         subagents, optionally nested by domain
  skills/<name>/SKILL.md          Agent Skills, with references/ scripts/ assets/
  references/                     shared reference material for the plugin's agents
  evals/ examples/                per-capability evaluations and worked examples
  .mcp.json                       optional MCP servers, wired via plugin.json
docs/registry/                    governance and authoring documentation
templates/ policies/ hooks/       scaffolding and shared configuration
scripts/                          maintenance tooling
archive/                          superseded material kept for provenance
```

There is a single tier. There is no `claude-catalog` and no `claude-marketplace`, and no
per-capability beta or stable flag. Versioning is semver on the plugin.

## Plugins

| Plugin | Scope |
|---|---|
| `replatforming` | Five-phase AS-IS to TO-BE pipeline: indexing, functional analysis, technical analysis, baseline testing, TO-BE construction, equivalence verification |
| `dev-standards` | Language and framework standards, developer agents, test authoring, debugging |
| `analysis-architecture` | Architecture design, requirement extraction, technical analysis, orchestration, registry auditing |
| `deliberation` | Multi-agent debate engine and its personas |
| `docs-branding` | Documentation authoring and Accenture-branded deliverables |
| `caveman` | Output-style skills |

## Conventions that are enforced by CI

- Combined subagent descriptions stay under **12000 tokens** across all plugins enabled at
  once. The hard platform ceiling is 15000.
- `SKILL.md` bodies stay under **500 lines**. Overflow goes into `references/`.
- Skill `description` stays under 1024 characters and is written in the third person.
- Skill `name` equals its directory name. Agent `name` equals its filename.
- `model`, `tools` and `color` are not SKILL.md frontmatter fields.
- Bundled material is referenced with `${CLAUDE_PLUGIN_ROOT}`, never with a repo-relative
  path. A repo-relative path resolves against the user's project and silently returns
  nothing.
- Every agent body has a `## When to invoke` section.

## Model policy

| Class | Model |
|---|---|
| Supervisors, challengers, auditors, deliberation personas | `opus` plus `effort: high` |
| User-facing agents | `inherit` |
| Pipeline workers dispatched in fan-out | `sonnet` |

`inherit` is the platform default. Pinning a model is a deliberate act and is justified in
an HTML comment in the agent body, never in a custom frontmatter field. A custom
multi-line key corrupts the value of the key above it.

## Skills

A skill is knowledge loaded into the current context, not a subagent. Agents load skills
on demand with the `Skill` tool. The `skills:` frontmatter field preloads full content at
startup and is reserved for the one or two skills an agent needs on **every** run.

A capability and the skills it always needs belong to the same plugin. When a cross-plugin
reference is unavoidable, the agent body says so and describes what to do without it.

## BMAD patterns

- **Progressive disclosure.** Supervisor bodies stay under 10000 characters; the phase
  protocol, dispatch templates and output schemas live in `references/`.
- **Document as cache.** Pipeline state lives in files under `.indexing-kb/`,
  `docs/analysis/` and `.refactoring-kb/`, never in conversation context.
- **Workflow registry.** `bmad/workflows.json` holds the phase DAG.

## Evaluations

Write evaluations before the capability. Three scenarios minimum in
`plugins/<plugin>/evals/<name>/evals.json`, plus `triggers.json` covering both the prompts
that must activate the capability and the near-miss prompts that must not. Trigger evals
are what catch a description edit that quietly breaks routing.

## Adding a new capability

1. Decide the type: agent, skill or command. See `docs/registry/how-to-write-a-capability.md`.
2. Decide the plugin. Prefer the plugin that already owns the skills it needs.
3. Write the evaluations.
4. Write the capability.
5. Run the validator, then `claude plugin validate .`.
6. Update the CHANGELOG and bump the plugin version.
