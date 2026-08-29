<!--
audience: contributor
diataxis: explanation
last-verified: 2026-08-30
verified-against: 8670a63
-->

# Architecture

How the repository is organised and how its flows work. This page assumes you know what
the registry is; if not, read [What is Claude Registry](What-is-Claude-Registry) first.

## Repository layout

```
.claude-plugin/marketplace.json   the marketplace manifest, one entry per plugin
plugins/<plugin>/                 the distribution unit
  .claude-plugin/plugin.json      name, description, version, author, component wiring
  agents/                         subagents, optionally nested by domain
  skills/<name>/SKILL.md          Agent Skills, with references/ scripts/ assets/
  references/                     shared reference material for the plugin's agents
  evals/<name>/                   evals.json and triggers.json
  examples/                       worked examples
  .mcp.json                       optional MCP servers, wired via plugin.json
.github/workflows/validate-pr.yml the two CI jobs
.github/scripts/validate_registry.py  the validator both jobs run
docs/registry/                    governance and authoring documentation
bmad/workflows.json               the phase DAG for the pipeline workflows
templates/ policies/ settings/    scaffolding and shared configuration
hooks/scripts/ hooks/tests/       session hooks and their regression matrix
scripts/                          maintenance tooling
wiki/                             the published GitHub wiki, mirrored here
archive/                          superseded material kept for provenance
```

There is a single tier. Versioning is semver on the plugin, declared in each
`plugin.json`. There is no per-capability version and no per-capability status flag.

Bulk figures at the verified commit: 86 agents, 46 skills, 158 bundled reference files
(143 of them in `replatforming`), 73 evaluation directories, 7 worked examples.

## How a plugin resolves at runtime

```
.claude-plugin/marketplace.json
    declares plugins[] with source "./plugins/<name>"
    and metadata.pluginRoot "./plugins"
                 │
                 ▼
plugins/<name>/.claude-plugin/plugin.json
    name, description, version, author, license, keywords,
    optional "mcpServers": "./.mcp.json"
                 │
                 ▼
components are discovered by convention
    agents/**/*.md          subagent definitions, loaded by name
    skills/<name>/SKILL.md   Agent Skills, discovered by the Skill tool
    commands/*.md            slash commands (none shipped here today)
                 │
                 ▼
${CLAUDE_PLUGIN_ROOT} expands to the installed plugin directory
    so agents/**/*.md can point at references/ from any project
```

`${CLAUDE_PLUGIN_ROOT}` is the mechanism that makes bundled material portable. A
repository-relative path resolves against the consumer's project instead, finds nothing,
and fails silently. That is why CI rejects a `${CLAUDE_PLUGIN_ROOT}` path that does not
exist inside the owning plugin, and why the local installer rewrites the variable to an
absolute path when it copies agent files out of the plugin layout.

## Progressive disclosure

Context is the scarce resource, so content loads in three levels.

| Level | Content | Loaded |
|---|---|---|
| 1 | Every installed skill's `name` and `description` | Always, at session start |
| 2 | The `SKILL.md` body, capped at 500 lines | When Claude decides the skill is relevant |
| 3 | `references/*.md` | Only when the body links to that specific file |

`scripts/` inside a skill is executed and never loaded. `assets/` is used in output and
never loaded.

The same idea applies to agents. Supervisor bodies stay under about 10000 characters, and
the phase protocols, dispatch templates and output schemas live in `references/`, read on
demand per step.

References must be **one level deep** from `SKILL.md`. Claude previews files reached
through a chain of references rather than reading them fully, so a two-hop reference
arrives incomplete. CI warns on a link that goes deeper.

## The delegation budget

Every enabled subagent's `description` is loaded at session start. The combined total
shares a **15000-token platform ceiling**. Past it, Claude Code warns and routing quality
degrades, because Claude has to discriminate between too many similar descriptions.

The validator reports the per-plugin cost and gates on the total:

| Plugin | Agents | Description tokens, approximate |
|---|---:|---:|
| `replatforming` | 58 | 7700 |
| `dev-standards` | 12 | 1700 |
| `deliberation` | 7 | 1200 |
| `docs-branding` | 4 | 750 |
| `analysis-architecture` | 5 | 500 |
| **all enabled** | **86** | **11900** |

Every description edit moves these figures, so measure rather than trusting the table:

```bash
python3 .github/scripts/validate_registry.py --only capabilities
```

Counts are estimated from character length when `tiktoken` is not installed, and measured
exactly when it is. The report says which.

CI warns above 13000 and fails above 15000. The gap exists so a consumer can still enable
plugins from other marketplaces. This is also the architectural reason plugins are split
by domain rather than shipped as one bundle: enabling `dev-standards` alone costs about
1700 tokens instead of about 11900.

## Flow: contributing a capability

```
author opens a PR touching plugins/**
                 │
                 ▼
   job "Validate marketplace"
        - marketplace.json and every plugin.json: schema, semver,
          source resolution, name agreement, mcpServers/hooks targets
        - every MCP server spec pins a version or a commit SHA
        - claude plugin validate .   (a real gate; a CLI that cannot
          run at all is reported, not enforced)
                 │
                 ▼
   job "Validate catalog"   (needs the job above)
        - every frontmatter under plugins/ survives yaml.safe_load
        - agent frontmatter: name matches filename, no duplicates,
          valid model and effort, description present
        - an agent whose body invokes skills carries the Skill tool
        - skill frontmatter: name matches directory, no model/tools/color,
          description under 1024 characters
        - SKILL.md body under 500 lines
        - reference links resolve; deeper than one level warns
        - ${CLAUDE_PLUGIN_ROOT} paths resolve inside the owning plugin
        - relative markdown links inside plugins resolve
        - a references/ path resolves in its own plugin, or the line
          names the plugin that owns it
        - no retired capability name appears outside the exempt set
        - combined description budget: warn at 13000, fail at 15000
        - hooks/tests/test-pre-tool-safety.sh passes
                 │
                 ▼
   reviewer applies docs/registry/review-checklist.md
                 │
                 ▼
   merge to main  ──►  published; consumers pick it up in the background
                 │
                 ▼
   tag <plugin>@<version> for consumers who pin
```

Both jobs post their findings as a pull-request comment, updating the same comment on
re-runs rather than adding new ones.

The job **names** are load-bearing. The branch protection ruleset requires the status
contexts `Validate marketplace` and `Validate catalog`. Renaming a job in the workflow
silently blocks every pull request, because a required context that never reports stays
pending forever. Change the ruleset first.

Run the same validator locally before pushing:

```bash
python3 .github/scripts/validate_registry.py
claude plugin validate .
```

`--only manifests` and `--only capabilities` run one half, exactly as the two CI jobs do.

## Flow: installing

Two paths, described in full in [Installation](Installation).

```
Path 1, marketplace
  /plugin marketplace add luketherose/claude-registry
  /plugin install <plugin>@claude-registry
        │
        ▼
  Claude Code resolves the plugin, registers agents, skills and MCP servers,
  and updates in the background when the resolved version changes.
  ${CLAUDE_PLUGIN_ROOT} expands natively.

Path 2, scripts/install-local.sh
  agents      → ~/.claude/agents/<name>.md          (flattened)
  skills      → ~/.claude/skills/<name>/            (copied whole)
  references  → ~/.claude/registry-references/<plugin>/
        │
        ▼
  ${CLAUDE_PLUGIN_ROOT}/references is rewritten to the absolute reference
  path while agent files are copied, because the variable does not expand
  outside a plugin. Every installed path is recorded in
  ~/.claude/.registry-install-manifest so --uninstall can reverse it.
```

Path 2 exists because the `strictKnownMarketplaces` setting can forbid adding a
marketplace. It trades background updates and per-project enabling for the ability to
install at all.

## The replatforming pipeline

The flagship workflow is an end-to-end AS-IS to TO-BE migration. Its machine-readable
phase DAG lives in `bmad/workflows.json`; `refactoring-supervisor` is the entrypoint.

```
                     refactoring-supervisor (opus, effort high)
                     human gate between every phase and every Phase 4 step
   ┌──────────┬──────────────┬──────────────┬──────────────┬──────────────────┐
   │          │              │              │              │                  │
Phase 0    Phase 1        Phase 2        Phase 3        Phase 4          Retrospective
   │          │              │              │              │                  │
indexing-  functional-   technical-     baseline-    driven directly    driven directly
supervisor analysis-     analysis-      testing-     by the workflow    by the workflow
           supervisor    supervisor     supervisor   supervisor         supervisor
   │          │              │              │              │                  │
.indexing- docs/analysis/ docs/analysis/ tests/       backend/           docs/refactoring/
kb/        01-functional/ 02-technical/  baseline/    frontend/
                                                      docs/refactoring/
                                                      e2e/
```

Phases 0 to 3 are strictly AS-IS and never modify the legacy source. Phase 4 is the first
phase with target technology.

Each phase writes a state file so the workflow can resume without holding history in the
conversation: `.indexing-kb/_meta/pipeline-state.yaml` for Phase 0, an equivalent
`_meta/pipeline-state.yaml` under each analysis output directory for Phases 1 to 3, and
`.refactoring-kb/pipeline-state.yaml` for Phase 4.

### Phase 0, codebase indexing

`indexing-supervisor` reads the legacy codebase and produces a Markdown knowledge base at
`.indexing-kb/`: structural inventory, dependency graph, per-module API documentation,
data-flow analysis, business-logic extraction, and Streamlit specifics where they apply.
Eight workers plus an auditor. Its output feeds every later phase.

### Phase 1, functional analysis

`functional-analysis-supervisor` turns the knowledge base into a functional understanding
at `docs/analysis/01-functional/`: actors and roles, UI surface, I/O catalogue, use cases
with sequence diagrams, and implicit logic. A challenger and a traceability auditor
review the result. The phase then exports an Accenture-branded PDF and PPTX, and supports
an `exports-only` resume mode that regenerates a missing export without re-running the
analysis.

### Phase 2, technical analysis

`technical-analysis-supervisor` dispatches eight Wave 1 workers in parallel, batched or
sequential mode, chosen adaptively from the knowledge-base size: code quality, state and
runtime, dependency security, data access, integration, performance, resilience,
security. Wave 2 synthesises a unified risk register. Wave 3 is an always-on challenger,
with a separate evidence auditor. Same `exports-only` resume mode as Phase 1.

### Phase 3, baseline testing

`baseline-testing-supervisor` authors the AS-IS regression baseline at `tests/baseline/`:
deterministic fixtures, per-use-case pytest modules, integration tests, benchmarks, and
an optional Postman collection. It then executes the suite and captures the oracle
artefacts. That baseline is what Phase 4 validates against, so its integrity is what the
challenger checks hardest.

### Phase 4, application replatforming

The workflow supervisor drives Phase 4 directly rather than delegating to a single phase
supervisor, because the per-feature gating cannot be delegated. Seven steps, Step 0
through Step 6, with a Step 5.5:

| Step | Name |
|---|---|
| 0 | Bootstrap hard gate |
| 1 | Minimal runnable skeleton |
| 2 | Incremental feature loop |
| 3 | Mandatory validation loop |
| 4 | Progressive system construction |
| 5 | Hardening |
| 5.5 | Test data seeding |
| 6 | Final validation |

The invariant is that the application is **always in a working state**. Every feature
iteration passes a boot smoke test before the next one starts, which catches
default-profile wiring regressions that profile-scoped tests mask.

Step 5.5 exists because the Step 6 gate includes a human visual check, and an empty
database makes an empty grid indistinguishable from a broken one.

Step 6 absorbs what used to be a separate Phase 5. The `tobe-testing` agent cluster from
that design is still in the plugin for backward compatibility, alongside
`refactoring-tobe-supervisor`, the earlier big-bang Phase 4 supervisor. Their own
descriptions still refer to the older shape.

After Phase 4 signs off, the supervisor enters a workflow retrospective that synthesises
findings across phases into `docs/refactoring/` and offers to close, iterate from the
earliest affected phase, or defer.

## Model policy

| Class | Model | Why |
|---|---|---|
| Supervisors, challengers, auditors, deliberation personas | `opus` plus `effort: high` | Cross-cutting reasoning where a missed failure mode is expensive |
| User-facing agents | `inherit` | Match whatever the user is running, and never silently downgrade an Opus session |
| Pipeline workers dispatched in fan-out | `sonnet` | High volume, narrow scope, cost matters |

`inherit` is the platform default. Pinning a model is deliberate and is justified in an
HTML comment in the agent body. It is never justified in a custom frontmatter field,
because an unrecognised multi-line key corrupts the value of the key above it.

Supervisors also carry `experimental.cacheTtl: 1h`, which sets the current Claude Code
version floor of 2.1.248.

## Patterns worth knowing

- **Document as cache.** Pipeline state lives in files under `.indexing-kb/`,
  `docs/analysis/` and `.refactoring-kb/`, never in conversation context. A phase can be
  resumed days later in a fresh session.
- **Workflow registry.** `bmad/workflows.json` holds the phase DAG, so adding a second
  workflow is an entry there plus an agent cluster, not a rewrite of the supervisor.
- **Evaluations before capability.** `evals.json` and `triggers.json` are written first.
  Trigger evaluations are what catch a description edit that quietly breaks routing.

## Related

- [Capability catalog](Capability-catalog): the full agent and skill list
- [Reference](Reference): exact fields, gates, paths and schemas
- [Governance](Governance): review, versioning and release rules
- [Contributing](Contributing): the mechanical workflow
