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

# Bash safety hook regression matrix (24 cases)
./hooks/tests/test-pre-tool-safety.sh

# Clean-machine install check
./scripts/test-clean-install.sh
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
bmad/workflows.json               the phase DAG for the pipeline workflows
templates/ policies/ settings/    scaffolding and shared configuration
hooks/scripts/ hooks/tests/       session hooks and their regression matrix
scripts/                          maintenance tooling
wiki/                             the published GitHub wiki, mirrored here
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

- Combined subagent descriptions stay under **13000 tokens** across all plugins enabled at
  once. The hard platform ceiling is 15000.
- `SKILL.md` bodies stay under **500 lines**. Overflow goes into `references/`.
- Skill `description` stays under 1024 characters and is written in the third person.
- Skill `name` equals its directory name. Agent `name` equals its filename.
- `model`, `tools` and `color` are not SKILL.md frontmatter fields.
- Bundled material uses the form that resolves where the file lives. Agent bodies use
  `${CLAUDE_PLUGIN_ROOT}/references/x.md` (55 of 86), because a repo-relative path there
  resolves against the user's project and silently returns nothing. `SKILL.md` uses a
  plain relative link `](references/x.md)` (all 9 skills that link references), which the
  Agent Skills standard specifies and `validate_skills()` resolves from the SKILL.md
  directory. Do not convert one form into the other.
- Every agent body has a `## When to invoke` section, and the `description` never points
  at it. The ending `See "When to invoke" in the agent body` that
  `plugin-dev:agent-development` prescribes is rejected here, and carried by 0 of 86
  agents: at delegation time the body is not loaded, so the pointer cannot be followed.
- Every frontmatter under `plugins/` survives a real `yaml.safe_load`. An unescaped quote
  in a `description` fails the build. Claude Code would otherwise load the agent with its
  name taken from the filename and drop every other field without an error.
- An agent whose body mentions the `Skill` tool, or tells itself to invoke a skill, has
  `Skill` in its `tools` list. The gate reads the body, not a `## Skills` heading.
- No file outside the exempt set names a retired capability. The `RETIRED` dict in
  `.github/scripts/validate_registry.py` is the source; the scan covers `plugins/`,
  `wiki/`, `docs/`, `README.md` and `CLAUDE.md`. Exempt: `docs/registry/CHANGELOG.md`,
  `docs/language-agnostic-design.md` and `docs/modernization/`, which record past state.
- Every MCP server spec names an exact version or commit SHA. `@latest` and a `git+` URL
  with no ref both fail, in the root `.mcp.json` and in every `plugins/*/.mcp.json`.
- `claude plugin validate .` is a real gate. A plugin the CLI rejects fails the build; a
  CLI that cannot run at all is reported and not enforced.
- `hooks/tests/test-pre-tool-safety.sh` passes. It is a 24-case matrix over the Bash
  safety hook, run by the `Validate catalog` job.
- Every fenced block under `plugins/` closes. Checked as structure, not as a count of
  markers. `scan_fences()` is straight CommonMark: a closing fence is bare and at least
  as long as its opener, so a four-backtick block may quote a three-backtick opener, and
  a fence carrying an info string can never close anything. Blocks do not nest, so a
  three-backtick template holding a three-backtick sample is miswritten and needs a
  four-backtick fence around it. The parity count this replaced passed a file carrying
  one stray closer plus one unclosed opener, and failed a correct four-backtick block.
  Six files carried a stray closing fence from an earlier edit; a lone ``` opens a block
  rather than erroring, so in one `SKILL.md` it swallowed the quality checklist and both
  reference links, and in one agent body 54 lines.
- An output template a capability emits carries **four** backticks, uniformly, not only
  where it happens to hold a nested block today. Encoding "contains a nesting" in the
  fence width means the file breaks silently the day someone adds one, which is how four
  files came to render part of their template as document prose. `codebase-mapper` used
  the selective form and now matches.
- `${CLAUDE_PLUGIN_ROOT}` resolves to a real bundled file, checked in every `.md` under
  `plugins/`. Separately, an agent body never leaves the token bare in prose:
  `scripts/install-local.sh:112` performs the rewrite inside the loop over agents only,
  so a bare mention there reaches the reader as an absolute path dropped into the middle
  of a sentence, naming a directory that exists only when the plugin ships `references/`
  or `examples/`. Skills and bundled references go through `cp -R` and are never
  rewritten, so they are not covered. Neither is a code fence inside an agent body: a
  hooks or MCP snippet writing `"cwd": "${CLAUDE_PLUGIN_ROOT}"` and a shell example
  writing `cd ${CLAUDE_PLUGIN_ROOT}` are both correct Claude Code usage, and stripping
  the braces would break them for anyone who copied them.
- No file under `plugins/`, `bmad/`, `scripts/` or `hooks/` names a retired directory as
  a path, with either separator. The scan follows execution rather than prose, because
  eight files record the migration in the past tense and a record has to name what it
  removed: `docs/registry/CHANGELOG.md`, `wiki/Changelog.md`,
  `docs/registry/release-process.md`, `docs/registry/how-to-write-a-capability.md`,
  `templates/new-use-case/README.md` and the three `docs/modernization/w7-*` audits.
  `archive/` is out for the same reason. A trailing separator is still required, so this
  file can state that neither directory exists without naming a path. Shell scripts are
  in the set: leaving them out is how `scripts/present.sh` kept dispatching an agent to
  read `policies/accenture-branding.md` under a directory deleted in the migration.

No em dash appears in `plugins/**/*.md`, in prose or in an output template, and
`validate_em_dash()` enforces it. Code samples keep theirs, because the character there
is inside a comment being illustrated, not punctuation this registry emits. The
distinction is the fence: untagged and `markdown`-tagged blocks are templates the agents
write into deliverables and are held to the prose rule; a language-tagged block is not.

The gate stops at `.md` deliberately, and the convention claims no more than the gate
holds. `plugins/**/*.json` still carries 32 in eval strings and `docs/registry/CHANGELOG.md`
alone carries over 400, so widening it today would fail the build on a backlog instead of
on a regression. Widen the glob in `validate_em_dash()` as each of those is cleared.

## Model policy

| Class | Model |
|---|---|
| Supervisors, challengers, auditors, deliberation personas | `opus` plus `effort: high` |
| User-facing agents | `inherit` |
| Pipeline workers dispatched in fan-out | `sonnet` |

`inherit` is the platform default. Pinning is deliberate, and justified per class, not per
file: `opus` carries its reason in an HTML comment in its own body, which
`validate_substance()` warns about when missing; the `sonnet` worker default is a class
policy stated once per plugin, not repeated across 43 files. Never justify it in a custom
frontmatter field. A custom multi-line key corrupts the value of the key above it.

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

One schema each, both gated by `validate_evals()`, which fails on a wrong key set, on a
fixture path that does not resolve, and on a `description` that states the verdict:

- `evals.json`: a list of `{agent, query, files, expected_behavior}`. `agent` equals the
  eval directory name; `files` are relative to the eval directory.
- `triggers.json`: a list of `{query, should_trigger, description}`. The `description`
  restates the query and never names the winner. Naming it lets a keyword table score the
  suite without reading a capability, which is how 232 of 232 once passed.

## Adding a new capability

1. Decide the type: agent, skill or command. See `docs/registry/how-to-write-a-capability.md`.
2. Decide the plugin. Prefer the plugin that already owns the skills it needs.
3. Write the evaluations.
4. Write the capability.
5. Run the validator, then `claude plugin validate .`.
6. Update the CHANGELOG and bump the plugin version.
