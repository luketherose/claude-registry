<!--
audience: contributor
diataxis: reference
last-verified: 2026-08-30
verified-against: c6c780a
-->

# Reference

Fields, schemas, paths and gates. Look here when you need an exact answer.

The authoritative authoring document is
[`docs/registry/how-to-write-a-capability.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/how-to-write-a-capability.md).
This page records what CI actually enforces and where things live.

## Directory contract

| Path | Holds |
|---|---|
| `.claude-plugin/marketplace.json` | The marketplace manifest |
| `plugins/<plugin>/.claude-plugin/plugin.json` | The plugin manifest |
| `plugins/<plugin>/agents/**/*.md` | Subagents, optionally nested by domain |
| `plugins/<plugin>/skills/<name>/SKILL.md` | An Agent Skill, one directory per skill |
| `plugins/<plugin>/skills/<name>/references/` | Skill reference material, loaded on demand |
| `plugins/<plugin>/skills/<name>/scripts/` | Executed, never loaded into context |
| `plugins/<plugin>/skills/<name>/assets/` | Used in output, never loaded |
| `plugins/<plugin>/references/` | Shared reference material for that plugin's agents |
| `plugins/<plugin>/evals/<name>/` | `evals.json`, `triggers.json`, and a `fixtures/` directory when a scenario needs input files |
| `plugins/<plugin>/examples/` | Worked examples |
| `plugins/<plugin>/commands/*.md` | Slash commands. Supported by the format, none shipped today |
| `plugins/<plugin>/.mcp.json` | MCP servers, wired through `mcpServers` in `plugin.json` |
| `.github/scripts/validate_registry.py` | The validator both CI jobs run |
| `.github/workflows/validate-pr.yml` | The two CI jobs |
| `docs/registry/` | Governance and authoring documentation |
| `bmad/workflows.json` | The phase DAG for pipeline workflows |
| `bmad/design/workflow-dag-draft.json` | The agent-level DAG, gated against the tree by name |
| `hooks/scripts/`, `hooks/tests/` | Session hooks and their regression matrix |
| `templates/`, `policies/`, `settings/` | Scaffolding and shared configuration |
| `scripts/` | Maintenance tooling |
| `wiki/` | The published GitHub wiki, mirrored in the repository |
| `archive/` | Superseded material kept for provenance |

## Agent frontmatter

Only `name` and `description` are required.

```markdown
---
name: developer-java
description: "Use this agent when writing, reviewing, or refactoring Java code. ..."
tools: Read, Grep, Glob, Edit, Write, Bash, Skill
model: inherit
color: blue
---

## When to invoke
...
```

### Enforced by CI

| Rule | Gate |
|---|---|
| `name` equals the filename without `.md` | error |
| `name` contains no `:` and does not start with `-` | error |
| `name` is unique across the whole registry | error |
| `description` is present | error |
| `model` is one of `sonnet`, `opus`, `haiku`, `fable`, `inherit`, or a full model id starting with `claude-` | error |
| `effort` is one of `low`, `medium`, `high`, `xhigh`, `max` | error |
| Frontmatter parses as YAML and yields a mapping | error |
| A body that mentions the `Skill` tool, or tells itself to invoke a skill, has `Skill` in `tools` | error |
| Body contains a `## When to invoke` section | warning |
| Body is at most 10000 characters | warning |
| `model: opus` carries an HTML comment in the body giving the reason | warning |

The YAML parse gate matters more than it looks. Claude Code loads an agent whose
frontmatter fails to parse by taking the name from the filename and dropping every other
field, with no error anywhere. An unescaped quote in a `description` is enough.

The `Skill` tool gate exists for the same class of failure. An agent told to load a skill
but not granted the tool silently substitutes its own priors for the team standard.

### Optional fields in use

| Field | Used by |
|---|---|
| `skills:` (preload at startup) | `api-designer`, `document-creator`, `presentation-creator`, `test-data-seeder` |
| `effort: high` | 24 agents: supervisors, challengers, auditors, `orchestrator`, `registry-auditor`, the deliberation personas |
| `experimental.cacheTtl: 1h` | 9 agents: the seven phase supervisors, `orchestrator`, `deliberative-decision-engine` |
| `background: true` | `registry-auditor` |

The full field list, including the fields deliberately not adopted, is in the authoring
guide and in
[`docs/registry/version-requirements.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/version-requirements.md).

### Model policy

| Class | Model | Count |
|---|---|---:|
| Supervisors, challengers, auditors, deliberation personas | `opus` plus `effort: high` | 24 |
| User-facing agents | `inherit` | 19 |
| Pipeline workers dispatched in fan-out | `sonnet` | 43 |

`inherit` is the platform default. A pinned model is justified in an HTML comment in the
body, never in a custom frontmatter field. An unrecognised multi-line key corrupts the
value of the key above it.

## Skill frontmatter

Exactly two fields.

```markdown
---
name: spring-data-jpa
description: "This skill should be used when working with JPA/Hibernate inside a Spring project: ... Do not use it for layered architecture (use spring-architecture)."
---
```

| Rule | Gate |
|---|---|
| `name` equals the containing directory name | error |
| `name` is at most 64 characters, lowercase alphanumeric and hyphens | error |
| `name` contains neither `anthropic` nor `claude` | error |
| `name` is unique across the registry | error |
| `description` is present and at most 1024 characters | error |
| `model`, `tools` or `color` present in frontmatter | error |
| Body is at most 500 lines | error |
| Relative links in the body resolve | error |
| A link more than one level deep from `SKILL.md` | warning |
| A body over 400 lines in a skill with no `references/` directory | warning |
| A `when to use` heading inside the body | warning |
| A reference file over 100 lines with no `## Contents` | warning |

The description is written in the **third person**, states both what the skill covers and
when to use it, and names the sibling skill to use instead where confusion is likely. It is
also the only thing routing sees, which is why a `when to use` heading in the body is a
warning: by the time the body loads, the routing decision has already been made.

Most of the warning rows in the two tables above come from `validate_substance()`, added
after an audit found that everything the structural gates covered was clean and everything
they did not had drifted. The missing `## When to invoke` warning is raised by
`validate_agents()` and the more-than-one-level-deep warning by `validate_skills()`. All of
them print in the pull-request comment and none sets a non-zero exit code.

## Bundled paths

Inside a plugin, reference bundled material with `${CLAUDE_PLUGIN_ROOT}`:

```markdown
| Read this | When |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}/references/indexing/grounding-policy.md` | Before emitting any evidence claim |
```

| Rule | Gate |
|---|---|
| Every `${CLAUDE_PLUGIN_ROOT}/<path>` resolves inside the owning plugin | error |
| Every relative markdown link inside `plugins/**` resolves | error |
| A `references/...` path resolves in its own plugin, or the line names the plugin that owns it | error |

A repository-relative path is never correct in a capability body. It resolves against the
consumer's project, finds nothing, and returns silently. That failure mode produced 84
dangling read instructions during the plugin migration, which is why there is a gate for
it.

The cross-plugin rule allows one exception, written in words rather than left implicit.
Four `replatforming` supervisors point at a file owned by the `deliberation` plugin, and
each of those lines says so.

## Manifests

### `.claude-plugin/marketplace.json`

| Field | Required | Notes |
|---|---|---|
| `name` | yes | kebab-case, and not one of the reserved marketplace names |
| `owner.name` | yes | |
| `plugins[]` | yes | One entry per plugin, names unique |
| `plugins[].source` | yes | Relative, starts with `./`, must not contain `..`, must exist |
| `metadata.pluginRoot` | no | `"./plugins"` here. Requires Claude Code 2.1.239 |
| `renames` | no | Maps an old plugin name to a new one, or to `null` for removed |

### `plugins/<plugin>/.claude-plugin/plugin.json`

| Field | Required | Notes |
|---|---|---|
| `name` | yes | Must equal the marketplace entry name |
| `description` | yes | |
| `version` | yes | Semver |
| `author`, `repository`, `license`, `keywords`, `category` | no | Present on every plugin here |
| `mcpServers` | no | A path such as `"./.mcp.json"`; the target must exist |
| `hooks` | no | Same rule as `mcpServers` |

### MCP configuration

Every MCP server spec names an exact version or a commit SHA. `@latest` fails, and a
`git+` URL with no ref fails, in the root `.mcp.json` and in every `plugins/*/.mcp.json`.

| Server | Pin | Declared in |
|---|---|---|
| `browser` (`@playwright/mcp`) | `0.0.79` | `.mcp.json`, `plugins/dev-standards/.mcp.json` |
| `uml` (`antoinebou12/uml-mcp`) | commit `78137bd66bfeb9754d0d5de0be1016f4dc053cc6` | `.mcp.json`, `plugins/docs-branding/.mcp.json` |

The root config and the plugin config for a given server carry the same pin. They drifted
once, and the same server then ran a different build depending on which config won.

## Evaluations

One directory per capability under `plugins/<plugin>/evals/<name>/`.

`evals.json`, a list of scenarios, abridged here from
`plugins/replatforming/evals/refactoring-supervisor/evals.json`:

```json
[
  {
    "agent": "refactoring-supervisor",
    "query": "Start the application replatforming workflow on the current repository",
    "files": [],
    "expected_behavior": [
      "Reads bootstrap-protocol.md before starting",
      "Dispatches indexing-supervisor for Phase 0",
      "Waits for user confirmation between every phase"
    ]
  }
]
```

`agent` equals the eval directory name. `files` lists input fixtures, written relative to
the eval directory, as in `fixtures/npe-stacktrace.txt`, and every one of them has to
exist.

`triggers.json`, a list of routing cases, from
`plugins/analysis-architecture/evals/software-architect/triggers.json`:

```json
[
  { "query": "Write an ADR for the decision to use event sourcing in the order management system",
    "should_trigger": true,
    "description": "ADR for adopting event sourcing" },
  { "query": "Produce a CVE inventory for our third-party dependencies",
    "should_trigger": false,
    "description": "CVE inventory for third-party dependencies" }
]
```

The second case is a negative, and nothing in its `description` says so. That is the rule.

| Rule | Gate |
|---|---|
| Either file is valid JSON | error |
| `triggers.json` is a flat list, not an object | error |
| `evals.json` key set is exactly `agent`, `query`, `files`, `expected_behavior` | error |
| `triggers.json` key set is exactly `query`, `should_trigger`, `description` | error |
| Every `files` entry resolves against the eval directory | error |
| A `description` matching a verdict phrasing | error |
| A `description` naming an agent or skill that its own `query` does not mention | error |

The verdict phrasings are `primary invocation`, `should activate`, `should not activate`,
`route to` in its `route`, `routes` and `routed` spellings, `belongs to`, and
`use <word> instead`, matched case-insensitively.

Both rules on `description` exist because the suite once graded itself. An earlier corpus
named the routing winner in 364 of 365 descriptions, which let a nine-line keyword table
with no semantics score 99.7 percent without reading a capability. A description that
repeats a subject the query already names is fine, because it hands the grader nothing new.

## CI gates

`.github/workflows/validate-pr.yml` runs two jobs on every pull request against `main`.
The second `needs` the first.

**`Validate marketplace`**. Checkout, Python and Node setup come first; these are the steps
that decide the verdict, in the order the workflow runs them:

| # | Step | Covers |
|---:|---|---|
| 1 | `validate_registry.py --only manifests` | Manifest schema, semver, source resolution, name agreement, `mcpServers` and `hooks` targets, MCP version pinning |
| 2 | `claude plugin validate .` | The official CLI's own view of every plugin |
| 3 | Post or update the pull-request comment | |
| 4 | Fail if step 1 or step 2 reported a failure | |

**`Validate catalog`**, which `needs` the job above:

| # | Step | Covers |
|---:|---|---|
| 1 | `validate_registry.py --only capabilities` | Frontmatter YAML parse, eval schemas and verdict leak, workflow DAG, substance warnings, cross-plugin references, agent rules, skill rules, `${CLAUDE_PLUGIN_ROOT}` resolution, relative link resolution, retired names, description budget |
| 2 | `hooks/tests/test-pre-tool-safety.sh` | The 24-case Bash safety hook matrix |
| 3 | `scripts/test-clean-install.sh` | A clean-machine install of every plugin into a throwaway `CLAUDE_CONFIG_DIR` |
| 4 | Post or update the pull-request comment | |
| 5 | Fail if step 1, step 2 or step 3 reported a failure | |

Every checking step in both jobs carries `continue-on-error: true`, and the last step of
each job re-reads their outcomes and exits non-zero. The gating is deferred on purpose:
failing a step where it runs would abort the job before the comment step, so a contributor
would get a red check and no findings. The comment is posted first, then the job fails.

Both jobs update the same comment on re-runs rather than adding a new one. They find it by
the HTML marker `<!-- claude-registry-validation-manifests -->` and
`<!-- claude-registry-validation-capabilities -->`.

`claude plugin validate .` is a real gate. A plugin the CLI rejects fails the build. A CLI
that cannot run at all, because it is unavailable or unauthenticated, is reported and not
enforced.

`scripts/test-clean-install.sh` runs `scripts/install-local.sh --all` against a throwaway
`CLAUDE_CONFIG_DIR`, so it never touches the caller's `~/.claude`. It asserts the things a
repository-local check cannot see: that every installed frontmatter still parses as YAML,
that no `${CLAUDE_PLUGIN_ROOT}` literal survives, that every absolute and every relative
reference path resolves at its installed location, that an agent invoking skills still
carries the `Skill` tool, that the installed agent and skill counts equal the tree's, and
that `--uninstall` leaves nothing behind. It also refuses to pass vacuously: an installer
that copies nothing, or a tree that has fallen below 50 agents and 30 skills, fails rather
than going green on an empty install.

**The job names are load-bearing.** The branch protection ruleset requires the status
contexts `Validate marketplace` and `Validate catalog`. Renaming a job leaves a required
context pending forever and blocks every pull request. Change the ruleset first.

### Running the validator locally

```bash
python3 .github/scripts/validate_registry.py
python3 .github/scripts/validate_registry.py --only manifests
python3 .github/scripts/validate_registry.py --only capabilities
python3 .github/scripts/validate_registry.py --output-file /tmp/report.md
```

Exit code 0 means no errors. Exit code 1 means at least one error. Warnings never fail
the build.

Install `pyyaml` for the frontmatter parse gate, and `tiktoken` for exact token counts.
Without `tiktoken` the budget is estimated from character length at 4.67 characters per
token and the report says so.

### The description budget

| Threshold | Effect |
|---|---|
| 13000 tokens | Warning |
| 15000 tokens | Error, build fails |

The 15000 figure is the documented platform ceiling on combined custom subagent
descriptions. The registry gates 2000 below it so a consumer can still enable plugins from
other marketplaces.

## Retired capability names

CI fails when a retired name appears in `plugins/`, `wiki/`, `docs/`, `bmad/`, `README.md`
or `CLAUDE.md`. The match is on word boundaries, so bare prose fails as readily as a
backticked mention; keying on the decorated spelling alone is how a dispatch instruction
naming a removed agent survived several cleanup passes. A colon immediately before the
name is excluded, so a plugin-qualified reference to the replacement is not flagged as the
thing it replaces. Exempt, because recording a removal necessarily names the thing removed:
`docs/registry/CHANGELOG.md`, `docs/language-agnostic-design.md`, `docs/modernization/`.
`archive/` is not scanned at all.

| What was retired | Use instead |
|---|---|
| The in-house code reviewer, removed 2026-08 | The `pr-review-toolkit` plugin from the official Anthropic marketplace. State the dependency as optional |
| The old Java and Spring developer agent name, renamed 2026-08 | `developer-java` |
| Two separate test-data skills, merged 2026-05 | `test-data-seeding-standards` |

The exact names are the keys of the `RETIRED` dict in the validator. This page describes
them rather than quoting them, because a backticked mention here would fail the same gate.

Add an entry to that dict whenever a capability is removed. It is what turns a stale
reference into a build failure rather than a dangling dispatch instruction at runtime.

## Install paths

| | Marketplace | `scripts/install-local.sh` |
|---|---|---|
| Add | `/plugin marketplace add luketherose/claude-registry` | `git clone`, then run the script |
| Install | `/plugin install <plugin>@claude-registry` | `./scripts/install-local.sh [names...]` |
| Default selection | Explicit | `dev-standards`, `analysis-architecture`, `docs-branding` |
| All plugins | Install each one | `--all` |
| List | Managed by Claude Code | `--list` |
| Remove | Managed by Claude Code | `--uninstall` |
| Agents land in | The plugin sandbox | `~/.claude/agents/<name>.md`, flattened |
| Skills land in | The plugin sandbox | `~/.claude/skills/<name>/` |
| References land in | The plugin sandbox | `~/.claude/registry-references/<plugin>/` |
| `${CLAUDE_PLUGIN_ROOT}` | Expands natively | Rewritten to an absolute path at copy time |
| Updates | Background, on version change | `git pull` and re-run |
| MCP servers | Wired via `plugin.json` | Merge the plugin `.mcp.json` by hand |
| Uninstall record | Managed by Claude Code | `~/.claude/.registry-install-manifest` |

The destination root is `$CLAUDE_CONFIG_DIR` when set, and `~/.claude` otherwise.

## Session hooks

`hooks/scripts/` holds two example hooks, activated by configuring them in a project's
`.claude/settings.json`. Placing a script in that directory does nothing on its own.

| Script | Event | Behaviour |
|---|---|---|
| `pre-tool-safety.sh` | `PreToolUse` on `Bash` | Exits 2, blocking the call, on a high-risk pattern such as a recursive delete or a `DROP TABLE` |
| `post-session-log.sh` | `Stop` | Appends a session-end timestamp to a local audit log. Always exits 0 |

`hooks/tests/test-pre-tool-safety.sh` is a 24-case regression matrix over the safety hook
and runs in the `Validate catalog` job. It asserts both directions: that every flag
spelling of a filesystem wipe is blocked, and that an ordinary scratch-directory cleanup is
not.

`settings/shared-settings-example.json` shows the settings shape, with its hook commands
pointing at `hooks/scripts/`. Its `deny` list is a set of prefix patterns rather than
regexes, so `Bash(rm -rf *)` there does not match `rm -fr` or `rm -r -f`. The file says so
in a comment and points at the hook, which parses the command instead.

## Naming and versioning

- Capability names are `kebab-case` and carry no version. `developer-java`, never
  `developer-java-v2`.
- An agent filename equals its `name`. A skill directory name equals its `name`.
- Branches: `feat/agent-<name>` and `feat/skill-<name>` are what `scripts/new-capability.sh`
  creates.
- Release tags are `<plugin>@<version>`, for example `dev-standards@1.3.0`.

| Change | Bump |
|---|---|
| A capability's `name` or `description` changes | major |
| A capability is removed or moved to another plugin | major |
| An output format a consumer parses changes | major |
| A new capability is added to the plugin | minor |
| A capability gains behaviour without changing its contract | minor |
| Prose, examples, evaluations, reference material | patch |

`name` and `description` are contract rather than documentation. They drive delegation and
skill activation, so changing one can silently break a consumer's routing.

## Pipeline output contracts

Agents in the replatforming pipeline write Markdown with a traceability header:

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

Findings that need a stable identifier carry their own header:

```yaml
id: RISK-NN | VULN-NN | PERF-NN | DEP-NN | INT-NN | SEC-NN
title: <human title>
severity: critical | high | medium | low | info
related: [<other-ids>, <feature-id>, <use-case-id>]
sources: [<.indexing-kb/... or repo/...:line>]
status: draft | needs-review | blocked
```

| Prefix | Domain | Phase | Owner agent |
|---|---|---:|---|
| `A-NN` | Actor | 1 | `actor-feature-mapper` |
| `F-NN` | Feature | 1 | `actor-feature-mapper` |
| `S-NN` | Screen | 1 | `ui-surface-analyst` |
| `UC-NN` | Use case | 1 | `user-flow-analyst` |
| `IN-NN`, `OUT-NN` | Input, output | 1 | `io-catalog-analyst` |
| `TR-NN` | Transformation | 1 | `io-catalog-analyst` |
| `IL-NN` | Implicit-logic finding | 1 | `implicit-logic-analyst` |
| `RISK-NN` | Entry in the unified risk register | 2 | `risk-synthesizer` |
| `RISK-CQ-NN` | Code-quality risk | 2 | `code-quality-analyst` |
| `RISK-DA-NN` | Data-access risk | 2 | `data-access-analyst` |
| `RISK-INT-NN` | Integration risk | 2 | `integration-analyst` |
| `RISK-RES-NN` | Resilience risk | 2 | `resilience-analyst` |
| `VULN-NN` | Library vulnerability | 2 | `dependency-security-analyst` |
| `DEP-NN` | Dependency or deprecation | 2 | `dependency-security-analyst` |
| `INT-NN` | External integration | 2 | `integration-analyst` |
| `PERF-NN` | Performance hotspot | 2 | `performance-analyst` |
| `SEC-NN` | Security or threat-model finding | 2 | `security-analyst` |
| `ST-NN` | State and runtime finding | 2 | `state-runtime-analyst` |
| `BUG-NN` | AS-IS bug found running the baseline | 3 | `baseline-runner` |
| `BC-NN` | Bounded context | 4 | `decomposition-architect` |
| `ADR-NNN` | Architecture decision record | 4 | `decomposition-architect`, `hardening-architect` |
| `TBUG-NN` | TO-BE bug found in equivalence testing | 5 | `tobe-test-runner` |
| `REG-NN` | Blocking regression against the baseline | 5 | `equivalence-synthesizer` |
| `AD-NN` | Accepted difference from the baseline | 5 | `equivalence-synthesizer` |
| `CHL-NN` | Challenger meta-finding | 2, 3, 4, 5 | `technical-analysis-challenger`, `baseline-challenger`, `phase4-challenger`, `tobe-testing-challenger` |

Phase 5 reuses `PERF-NN` and `SEC-NN` for findings of its own. The owner column names the
agent that mints an ID, not every agent that reads one; a downstream agent quotes the ID
verbatim and never renumbers it.

Two conventions sit outside this table. Iteration and retrospective state carries
`ADJ-NN`, `XADJ-NN` and `RETRO-NN` as JSON `adjustment_id` and `issue_id` fields rather
than as document headings, and each Phase 2 worker also emits a JSON `finding_id` of the
form `TECH-<DOMAIN>-NNN`, with `DOMAIN` one of `CATEG`, `DATA`, `DEP`, `INT`, `PERF`,
`QUAL`, `RES`, `SEC`, `STATE`.

Outside the replatforming pipeline, `functional-analyst` in `analysis-architecture` uses
its own three-digit set: `FR-NNN` for a functional requirement, `NFR-NNN` for a
non-functional one, `UC-NNN` for a use case and `BR-NNN` for a business rule. Note that
`UC-NNN` and the pipeline's `UC-NN` are different conventions in different documents.
`technical-analyst` in the same plugin numbers its findings `TA-NNN`.

Each phase also maintains `_meta/manifest.json` and a `_meta/pipeline-state.yaml` under
its output directory, which is what makes a phase resumable in a fresh session.

## Related

- [Architecture](Architecture): how these pieces connect
- [Contributing](Contributing): the workflow for adding a capability
- [Governance](Governance): review, release and deprecation rules
