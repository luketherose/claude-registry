# How to write a capability

A **capability** in this registry is one of four things. Picking the right one is the
first decision, and getting it wrong is the most common authoring mistake.

| Type | What it is | Who invokes it | Lives in |
|---|---|---|---|
| **Agent** (subagent) | An autonomous worker with its own context window, tool set and system prompt | Claude delegates to it, or the user @-mentions it | `plugins/<plugin>/agents/**/*.md` |
| **Skill** | Knowledge and procedure loaded into the current context on demand | Claude loads it with the `Skill` tool, or an agent preloads it via `skills:` | `plugins/<plugin>/skills/<name>/SKILL.md` |
| **Command** | A user-initiated action bound to `/<name>` | The user types the slash command | `plugins/<plugin>/commands/*.md` |
| **Plugin** | The distribution unit that bundles the above | Installed with `/plugin install` | `plugins/<plugin>/` |

**The decision rule.** Does the work need its own context window and its own tools?
That is an agent. Is it knowledge, conventions or a procedure that the current agent
should apply itself? That is a skill. Is it something the user starts by name? That is
a command.

> **Historical note.** Until mid 2026 this registry modelled skills as `haiku` subagents
> with `tools: Read`, invoked through the `Agent` tool. That predates Agent Skills. Do
> not author new capabilities that way. See "Old patterns" at the end of this document.

Anthropic ships two official skills that cover the generic mechanics in more depth than
this document does: `plugin-dev:skill-development` and `plugin-dev:agent-development`.
Read those for the general case. This document is the registry-specific layer on top:
our budgets, our model policy, our directory conventions.

---

## 1. Repository layout

```
claude-registry/
├── .claude-plugin/
│   └── marketplace.json            # the marketplace manifest
├── plugins/
│   └── <plugin>/
│       ├── .claude-plugin/
│       │   └── plugin.json         # name, description, version, author
│       ├── agents/                 # subagents, optionally nested by domain
│       ├── skills/
│       │   └── <skill-name>/
│       │       ├── SKILL.md        # required
│       │       ├── references/     # loaded on demand
│       │       ├── scripts/        # executed, not loaded
│       │       └── assets/         # used in output, never loaded
│       ├── references/             # shared reference material for the plugin's agents
│       ├── evals/
│       ├── examples/
│       └── .mcp.json               # optional, wired via plugin.json mcpServers
├── docs/registry/                  # governance, this document included
├── templates/                      # scaffolding for new capabilities
└── scripts/                        # maintenance tooling
```

There is **one tier**. There is no separate catalog and marketplace, and no per-capability
beta or stable flag. Versioning is semver on the plugin, in `plugin.json`.

### Which plugin does a capability belong to

| Plugin | Scope |
|---|---|
| `replatforming` | The five-phase AS-IS to TO-BE pipeline and everything only useful inside it |
| `dev-standards` | Language and framework standards, developer agents, test authoring, debugging |
| `analysis-architecture` | Architecture design, requirement extraction, technical analysis, orchestration, registry auditing |
| `deliberation` | The multi-agent debate engine and its personas |
| `docs-branding` | Documentation authoring and branded deliverable generation |
| `caveman` | Output-style skills |

**Rule: a capability and the skills it always needs belong to the same plugin.** A skill
in another plugin is only available when the user has that plugin enabled. When a
cross-plugin reference is unavoidable, say so explicitly in the agent body and describe
what the agent should do without it. Never make an agent hard-fail on a skill it does
not own.

---

## 2. Agents

### Frontmatter

Only `name` and `description` are required. Everything else is opt-in.

| Field | Values | Use it when |
|---|---|---|
| `name` | lowercase, hyphens, no `:`, must match the filename | always |
| `description` | free text, drives delegation | always, see the budget rule below |
| `tools` | comma-separated allowlist, `Agent(type1,type2)`, `mcp__server__*` | always; omitting inherits everything |
| `disallowedTools` | denylist, applied before `tools` | rarely |
| `model` | `sonnet`, `opus`, `haiku`, `fable`, `inherit`, or a full model ID | see the model policy below |
| `effort` | `low`, `medium`, `high`, `xhigh`, `max` | supervisors, challengers, deliberation personas |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` | when the agent must be constrained beyond its tool list |
| `maxTurns` | integer | bounded tasks; output is marked partial and can be resumed |
| `skills` | array of skill names | only for one or two skills the agent needs on **every** run |
| `memory` | `user`, `project`, `local` | agents that must carry state across sessions |
| `mcpServers` | server names or inline definitions | prefer wiring MCP at the plugin level instead |
| `hooks` | lifecycle hooks scoped to this agent | rarely; requires workspace trust |
| `background` | `true` | long-running standalone agents whose result the caller does not block on |
| `isolation` | `worktree` | agents that may safely work on an isolated copy of the repo |
| `color` | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` | always, for transcript legibility |
| `initialPrompt` | string | agents meant to run as a main session via `--agent` |
| `experimental.cacheTtl` | `5m`, `1h` | supervisors driving long pipelines |

Do not invent fields. Unrecognised keys are silently ignored, and a multi-line custom
field will corrupt the value of the key above it. If you need to record why a model was
chosen, put it in an HTML comment in the body.

### The description budget

The combined descriptions of every enabled subagent share a **15000-token ceiling**.
Past it, Claude Code warns at startup and delegation quality degrades because Claude has
to discriminate between too many similar descriptions.

The registry gates at **13000 tokens** in CI (`BUDGET_WARN`), measured across all plugins
enabled at once, under a `BUDGET_FAIL` of 15000. The 2000-token gap is headroom for
subagents the user enables from other marketplaces. Run the check locally before opening a
PR:

```bash
python3 .github/scripts/validate_registry.py
```

Practical consequences for authors:

- The description states the trigger condition and the boundary. It does not restate the
  system prompt.
- Worker agents that are only ever dispatched by a supervisor are never auto-delegated.
  Their description needs the boundary ("not for standalone use, invoked only by X") and
  nothing else. Do not give them trigger enumerations.
- User-facing agents benefit from **quoted user phrasings**, because they match how people
  actually ask. `Typical user phrasings: "review this Spring Boot controller", "add JUnit 5
  tests for the payment module".` Two to four, no more.
- Do not end a description with a pointer to the body. Claude cannot follow it at
  delegation time, because the body is not loaded yet.

### The model policy

| Class | Model | Why |
|---|---|---|
| Supervisors, challengers, auditors, deliberation personas | `opus` plus `effort: high` | Cross-cutting reasoning where a missed failure mode is expensive |
| User-facing agents (developers, architect, documentation, debugger, test-writer) | `inherit` | Match whatever the user is running; do not silently downgrade an Opus session |
| Pipeline workers dispatched in fan-out | `sonnet` | High volume, narrow scope, cost matters |

`inherit` is the default in the Claude Code spec. Pinning a model is a deliberate act:
justify it in an HTML comment in the body.

### Body structure

```markdown
## When to invoke

- **[Scenario].** [What the situation looks like and what the agent does.]
- **[Scenario].** [Same.]

## Role
## What you always do
## What you never do
## Skills
## Output format
## Quality criteria
```

`## When to invoke` is mandatory. It carries the worked scenarios that used to bloat the
description, and CI warns when it is missing.

Writing rules that still hold, unchanged:

1. Be opinionated. Name the frameworks, define the output format exactly, do not leave
   structure to interpretation.
2. State what the agent delegates and to which named sibling.
3. State when the agent escalates to the user rather than guessing.
4. Include a self-check the agent runs before responding.
5. Under `## What you never do`, never join a prohibition to its alternative with a colon
   or a dash. Put the alternative in its own sentence. "Never use Thread.sleep to wait for
   async operations: use CompletableFuture" parses as forbidding `CompletableFuture` too.
   Write "Never use Thread.sleep to wait for async operations. Use CompletableFuture."
6. Name a capability with the flat name the runtime resolves. Skills and agents no longer
   live in category directories, so `angular-expert`, never `frontend/angular-expert`.

### Referencing bundled material

Use `${CLAUDE_PLUGIN_ROOT}` for anything inside the plugin. It resolves to the installed
plugin directory, so it works from any project.

```markdown
| Read this | When |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}/references/indexing/grounding-policy.md` | Before emitting any evidence claim |
```

Never use a repository-relative path. It resolves against the user's project, not against
the registry, and silently returns nothing. CI fails on a `${CLAUDE_PLUGIN_ROOT}` path that
does not exist in the owning plugin.

---

## 3. Skills

### SKILL.md frontmatter

Exactly two fields.

```markdown
---
name: spring-data-jpa
description: "This skill should be used when working with JPA/Hibernate inside a Spring project: entity design, fetch strategies, N+1 resolution, transaction boundaries, JPQL. Do not use it for layered architecture (use spring-architecture) or database design (use postgresql-expert)."
---
```

- `name`: max 64 characters, lowercase alphanumeric and hyphens, must equal the directory
  name, must not contain `anthropic` or `claude`.
- `description`: max 1024 characters, non-empty, **third person**, states both what the
  skill does and when to use it, and names the sibling skill to use instead when there is
  a likely confusion.

`model`, `tools` and `color` are **not** SKILL.md fields. CI rejects them.

### Body

- **Under 500 lines.** This is the Anthropic guidance and the CI gate. When you cross it,
  move detail into `references/`, do not compress prose.
- Assume Claude is already smart. Do not explain what a PDF is, what JPA is, or what a
  design token is. Only add context Claude does not already have.
- Use consistent terminology. Pick one word per concept and keep it.
- No time-sensitive statements. Put superseded guidance in an `## Old patterns` section
  inside `<details>` rather than writing "before August 2026, do X".
- Do not offer four options. Give a default and one escape hatch.

### Progressive disclosure

| Level | Content | Loaded |
|---|---|---|
| 1 | `name` and `description` | Always, at startup, for every installed skill |
| 2 | The SKILL.md body | When Claude decides the skill is relevant |
| 3 | `references/*.md` | Only when the body links to the specific file |

`scripts/` is executed, never loaded. `assets/` is used in output, never loaded.

**References must be one level deep from SKILL.md.** Claude partially reads files reached
through a chain of references, using `head` style previews, and ends up with incomplete
information. Every reference file links directly from the body.

Reference files longer than 100 lines start with a `## Contents` table of contents, so a
partial read still shows the full scope.

Link them explicitly, one line per file, saying what is in it:

```markdown
## Detailed references

- **Full code templates for the controller, service and mapper layers**: see [references/layer-templates.md](references/layer-templates.md)
- **Custom exception hierarchy and RFC 7807 global exception handling**: see [references/error-handling.md](references/error-handling.md)
```

### Deterministic work belongs in scripts

If the rule reads "given X, the answer is always Y", write a script. If it reads "given X,
weigh Y against Z", write prose. A `scripts/README.md` is mandatory when the directory
exists: one entry per script with its invocation, inputs, outputs and exit codes, so the
consuming agent can call it without reading the source.

Handle errors inside the script rather than deferring to Claude, and justify every
constant in a comment. A timeout of 47 with no explanation is a bug waiting to happen.

### How an agent uses a skill

Two mechanisms, and the choice matters.

**On demand, through the `Skill` tool.** This is the default. The agent loads the skill
only when the task touches its domain. Use this whenever the agent references more than
two skills, or when the relevant skill depends on what the agent detects at runtime.

```markdown
## Skills

Load the following skills with the `Skill` tool when the task touches their domain:

- `java-spring-standards` for package structure, layering, error handling and observability
- `spring-data-jpa` when the change touches entities, repositories or transactions
```

**Preloaded, through the `skills:` frontmatter field.** The full skill content is injected
at startup, before the agent sees the task. Only use this for one or two skills the agent
needs on **every single run**, such as `accenture-branding` for `presentation-creator`.
Preloading five skills defeats progressive disclosure and costs the agent its context.

---

## 4. Evaluations come first

Write the evaluations **before** the capability, not after. Otherwise you document an
imagined problem.

1. Run Claude on a representative task with no capability. Record what it gets wrong.
2. Write three scenarios that cover those gaps.
3. Measure the baseline.
4. Write the smallest capability that passes.
5. Iterate against the evaluations, not against your intuition.

Both files live in `plugins/<plugin>/evals/<capability-name>/`, where the directory name is
the agent filename without `.md`, or the skill directory name. Agents get both files.
Skills get `triggers.json` only, because a skill has no behaviour of its own to score: it
is judged on whether the right prompt activates it.

`evals.json` is a flat JSON list. One object per scenario, exactly these four keys, with
`agent` equal to the directory name:

```json
[
  {
    "agent": "developer-java",
    "query": "This repository method triggers an N+1 on order lines. Fix it.",
    "files": ["fixtures/OrderRepository.java"],
    "expected_behavior": [
      "Identifies the lazy association responsible for the N+1",
      "Applies a fetch join or an entity graph rather than switching to EAGER",
      "Keeps the existing method signature and adds a regression test"
    ]
  }
]
```

`triggers.json` covers the other half: which prompts must activate the capability, and
which near-miss prompts must **not**. It is a flat JSON list of three-key objects. A
negative case carries the sibling it should route to instead, in the `description`:

```json
[
  {
    "query": "Write an ADR for the decision to use event sourcing in the order service",
    "should_trigger": true,
    "description": "Primary invocation"
  },
  {
    "query": "Produce a CVE inventory for our third-party dependencies",
    "should_trigger": false,
    "description": "Dependency vulnerability audit, should route to `technical-analyst`"
  }
]
```

Trigger evals are what catch a description edit that quietly breaks routing. Write a
negative case for every sibling a reader could plausibly confuse with this capability, and
make sure the negative case is genuinely out of scope: a prompt the capability's own
description claims is a prompt it must handle.

Nothing in CI checks either schema, so a scenario written to the wrong shape passes review
and then fails silently when the suite is run. Both shapes above are the ones in use across
all 27 `evals.json` and all 73 `triggers.json` files in the repository.

Test against Haiku, Sonnet and Opus. What reads as sufficient guidance on Opus is often
too terse for Haiku.

---

## 5. What CI enforces

Two jobs run on every pull request against `main`, and both are required status checks.
`Validate marketplace` runs `validate_registry.py --only manifests` and then
`claude plugin validate .`. `Validate catalog` needs `Validate marketplace`, so a broken
manifest stops it before it starts; it runs `validate_registry.py --only capabilities` and
then the safety-hook regression matrix. Running the validator with no `--only` flag, as you
would locally, covers both halves in one pass.

The job names are load-bearing. The branch ruleset requires the contexts
"Validate marketplace" and "Validate catalog", and a required context that never reports
stays pending forever. Change the ruleset before renaming a job.

| Gate | What fails | Function |
|---|---|---|
| Manifest schema | A missing or malformed `marketplace.json` or `plugin.json`, a name mismatch, a non-semver version, a source that escapes the root, a reserved marketplace name | `validate_manifests` |
| MCP pinning | An MCP arg ending in `@latest`, or a `git+` URL with no ref after the host, in `.mcp.json` or any `plugins/*/.mcp.json` | `validate_mcp_pins` |
| Frontmatter parses as YAML | Any `plugins/**/*.md` whose frontmatter does not survive `yaml.safe_load`, or does not parse to a mapping | `validate_frontmatter_yaml` |
| Agent frontmatter | A missing `name` or `description`, a `name` that does not match the filename, a duplicate name, an invalid `model` or `effort` | `validate_agents` |
| Skill tool held | An agent body that mentions the `Skill` tool or tells itself to invoke a skill, while `Skill` is absent from `tools` | `validate_agents` |
| Description budget | Combined agent descriptions over 15000 tokens. Over 13000 is a warning | `validate_agents` plus `report` |
| Skill frontmatter | A `name` that does not match the directory, is over 64 characters, is not kebab-case or contains a reserved word; a `description` over 1024 characters; a `model`, `tools` or `color` key | `validate_skills` |
| SKILL.md body length | Over 500 lines | `validate_skills` |
| Reference links | A link from a `SKILL.md` body that does not resolve. More than one level deep is a warning | `validate_skills` |
| Plugin-root paths | A `${CLAUDE_PLUGIN_ROOT}/...` path that does not exist inside the owning plugin | `validate_plugin_root_refs` |
| Relative links | A `../`-style markdown link inside a plugin that does not resolve | `validate_relative_links` |
| Retired capabilities | A backticked reference to a name in the `RETIRED` dict, anywhere in `plugins/`, `wiki/`, `docs/`, `README.md` or `CLAUDE.md` | `validate_agent_references` |
| Official CLI | `claude plugin validate .` reporting a validation failure. A CLI that cannot run at all is reported, not enforced | workflow step |
| Safety hook | Any of the 24 cases in `hooks/tests/test-pre-tool-safety.sh` | workflow step |

Three of these deserve a note, because they change how you work rather than what you type.

**Frontmatter is parsed, not scanned.** `split_frontmatter()` returns raw text and
`field()` reads it line by line, so an unescaped quote in a `description` still yields a
plausible-looking value to the rest of the validator. Claude Code, meanwhile, loads such an
agent with its name taken from the filename and silently drops every other field: the
description, the model, the colour and the whole `tools` list. Nothing surfaces an error.
`validate_frontmatter_yaml()` runs a real `yaml.safe_load` over every `plugins/**/*.md` so
that failure is loud. If your description contains a quote, escape it.

**The Skill-tool gate reads the body, not a heading.** It used to key on a literal
`## Skills` heading, which missed an agent whose body said "Invoke the framework skill set"
while its `tools` list had no `Skill` entry. The instruction was inert and the agent
substituted its own priors for the team standard. The gate now matches `` `Skill` ``,
"Skill tool", and "invoke the ... skill". Writing any of those without granting the tool
fails the build.

**Retiring a capability is a repository-wide edit.** Add the name to the `RETIRED` dict in
`.github/scripts/validate_registry.py` with what to use instead, then fix every backticked
reference in `plugins/`, `wiki/`, `docs/`, `README.md` and `CLAUDE.md` in the same pull
request. `docs/registry/CHANGELOG.md`, `docs/language-agnostic-design.md` and
`docs/modernization/` are exempt, because recording a removal necessarily names the thing
removed. `archive/` is not scanned.

---

## 6. Before opening a PR

```bash
python3 .github/scripts/validate_registry.py
claude plugin validate .
bash hooks/tests/test-pre-tool-safety.sh
```

- [ ] `name` matches the filename (agents) or the directory (skills)
- [ ] Description is third person, specific, and names the sibling to use instead
- [ ] Agent body has `## When to invoke`
- [ ] SKILL.md body is under 500 lines
- [ ] Reference links resolve and are one level deep
- [ ] Bundled paths use `${CLAUDE_PLUGIN_ROOT}`
- [ ] `tools` is a minimal allowlist
- [ ] Model choice follows the policy, or is justified in an HTML comment
- [ ] Cross-plugin skill dependencies are declared and degrade gracefully
- [ ] Three evaluation scenarios plus `triggers.json`, in the schemas above
- [ ] One example in the plugin's `examples/`
- [ ] Combined description budget still under 13000 tokens
- [ ] Any capability this change retires is in `RETIRED`, and every reference to it is gone
- [ ] Any MCP server this change adds names an exact version or commit SHA
- [ ] No credentials, tokens or secrets anywhere

---

## Old patterns

<details>
<summary>Skills as haiku subagents (superseded 2026-08)</summary>

Skills used to be flat `.md` files under `claude-catalog/skills/<topic>/<name>.md` with
this frontmatter:

```yaml
---
name: java-expert
description: Use to load Java 17+ core standards.
tools: Read
model: haiku
---
```

An agent invoked them through the `Agent` tool and consumed the returned text. This
predates Agent Skills. It cost a full subagent round trip per invocation, it put skill
descriptions inside the subagent delegation budget, and the skills were invisible to the
`Skill` tool, so Claude never activated them on its own.

</details>

<details>
<summary>catalog.json plus setup-capabilities.sh (superseded 2026-08)</summary>

Distribution used a hand-maintained `claude-marketplace/catalog.json`, a bash installer
that copied agent files into `~/.claude/agents/`, and a `SessionStart` hook that compared
`main` against `origin/main` and printed a reminder to re-run the installer.

It is replaced by the official marketplace mechanism: `extraKnownMarketplaces` plus
`enabledPlugins` in `settings.json`, with background updates when the resolved version
changes. The per-capability `beta` and `stable` tiers are replaced by semver on the plugin.

</details>
