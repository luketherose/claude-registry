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

CI measures the total across all plugins enabled at once and reports it two ways. Above
`BUDGET_WARN`, which is 13000 tokens, it warns and the build still passes. Above
`BUDGET_FAIL`, which is 15000, it errors and the build fails. The 2000-token gap is
headroom for subagents the user enables from other marketplaces. Counts come from tiktoken
when it is installed and from a 4.67 characters-per-token estimate when it is not, and the
report says which. Run the check locally before opening a PR:

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

There are two forms, and which one is correct depends on the file you are writing in. Do
not convert one into the other.

**An agent body uses `${CLAUDE_PLUGIN_ROOT}`.** It resolves to the installed plugin
directory, so it works from any project.

```markdown
| Read this | When |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}/references/indexing/grounding-policy.md` | Before emitting any evidence claim |
```

**A `SKILL.md` uses a plain relative link.** This is what the Agent Skills standard
specifies, and `validate_skills()` resolves it from the directory the `SKILL.md` lives in.

```markdown
- **Custom exception hierarchy and RFC 7807 handling**: see [references/error-handling.md](references/error-handling.md)
```

Both forms are checked. `validate_plugin_root_refs()` fails on a `${CLAUDE_PLUGIN_ROOT}`
path that does not exist in the owning plugin, `validate_skills()` fails on a `SKILL.md`
link that does not resolve, and `validate_relative_links()` fails on a `../`-style link
anywhere under `plugins/**` that does not resolve. `validate_cross_plugin_references()`
adds one more rule for a bare `references/...` path in an agent body or a `SKILL.md`: it
has to resolve inside its own plugin, or the same line has to name the plugin that owns it
in words, and that plugin has to actually hold the file.

A repository-relative path is never correct in a capability body. It resolves against the
user's project rather than against the registry and silently returns nothing, which is how
84 dangling read instructions survived the plugin migration.

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

- **Under 500 lines.** This is the Anthropic guidance and the CI error threshold. When you
  cross it, move detail into `references/`, do not compress prose. CI also warns at 400
  lines when the skill has no `references/` directory at all, because 500 is a ceiling
  rather than a target.
- **No `when to use` heading in the body.** Routing happens on the description alone, so a
  trigger section in the body is unreachable at the moment it would matter and only
  duplicates what the description already has to say. CI warns on the heading.
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
information. Every reference file links directly from the body. A link that resolves but
goes deeper than one level is a CI warning; a link that does not resolve is an error.

Reference files longer than 100 lines start with a `## Contents` table of contents, so a
partial read still shows the full scope. CI warns on one that does not, across both
`plugins/*/references/` and `plugins/*/skills/*/references/`.

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
`agent` equal to the directory name. Abridged from
`plugins/dev-standards/evals/developer-java/evals.json`:

```json
[
  {
    "agent": "developer-java",
    "query": "Review this Spring Boot controller",
    "files": ["fixtures/OrderController.java"],
    "expected_behavior": [
      "Flags the discount computation inside create, and the @Autowired field injection into the controller, as layering violations, quoting the offending lines",
      "Flags the empty catch (Exception) that returns null and requires an RFC 7807 ProblemDetail response in place of the RuntimeException",
      "Reports the hardcoded STRIPE_KEY constant and the log statement that writes customer email and card number, each with its line"
    ]
  }
]
```

Every path in `files` is resolved against the directory the `evals.json` lives in, and CI
fails on one that does not exist.

`triggers.json` covers the other half: which prompts must activate the capability, and
which near-miss prompts must **not**. It is a flat JSON list of three-key objects. The
`description` says what the query is about and never which capability wins. Two cases from
`plugins/analysis-architecture/evals/software-architect/triggers.json`:

```json
[
  {
    "query": "Write an ADR for the decision to use event sourcing in the order management system",
    "should_trigger": true,
    "description": "ADR for adopting event sourcing"
  },
  {
    "query": "Produce a CVE inventory for our third-party dependencies",
    "should_trigger": false,
    "description": "CVE inventory for third-party dependencies"
  }
]
```

The second case is a negative for `software-architect`, and its description says so
nowhere. That is the rule, and CI enforces it in both directions. `validate_evals()`
rejects a description that matches a verdict phrasing (`primary invocation`,
`should activate`, `should not activate`, `route to` in its `route`, `routes` and `routed`
spellings, `belongs to`, `use <word> instead`), and it separately rejects a description
naming any agent or skill in the registry that the case's own `query` does not mention.
Repeating a subject the query already names is fine, because it tells a grader nothing it
could not read off the query.

Use neutral topic labels, and give the identical query the identical description whether it
appears as a positive in one file or a negative in another. The reason is measured: an
earlier corpus named the winner in 364 of 365 descriptions, which let a nine-line keyword
table with no semantics score 99.7 percent without reading a capability.

Trigger evals are what catch a description edit that quietly breaks routing. Write a
negative case for every sibling a reader could plausibly confuse with this capability. Pick
that sibling when you choose the query, then keep it out of the description. Check the
negative against the capability's own `description` before committing it. A prompt the
description claims the capability handles cannot be a valid negative case, and that error
once listed a security question as a must-not-trigger for an agent whose description names
security among the concerns it assesses.

`validate_evals()` in `.github/scripts/validate_registry.py` gates both files, so a
scenario written to the wrong shape fails CI rather than passing review. It rejects a file
that is not valid JSON, a `triggers.json` that is not a flat list, either file carrying a
key set other than the one documented above, an `evals.json` fixture path that does not
resolve, and a `triggers.json` description that leaks the verdict.

Every agent and every skill carries a `triggers.json`. `evals.json` is for agents, and in
practice for the ones a user invokes directly rather than the fan-out workers a supervisor
dispatches. Count the corpus rather than trusting a figure in this document, because it
moves with every capability added:

```bash
ls plugins/*/evals/*/triggers.json | wc -l
ls plugins/*/evals/*/evals.json | wc -l
```

Test against Haiku, Sonnet and Opus. What reads as sufficient guidance on Opus is often
too terse for Haiku.

---

## 5. What CI enforces

Two jobs run on every pull request against `main`, and both are required status checks.
`Validate marketplace` runs `validate_registry.py --only manifests` and then
`claude plugin validate .`. `Validate catalog` needs `Validate marketplace`, so a broken
manifest stops it before it starts; it runs `validate_registry.py --only capabilities`,
then `hooks/tests/test-pre-tool-safety.sh`, then `scripts/test-clean-install.sh`. Running
the validator with no `--only` flag, as you would locally, covers both halves in one pass.

Every checking step in both jobs carries `continue-on-error: true`, and each job ends with
a step that fails when any of them reported a failure. That ordering is deliberate. Failing
a step outright would abort the job before the comment step, so a contributor would see a
red check and no findings at all. A failure still fails the job, after the findings have
been posted.

The job names are load-bearing. The branch ruleset requires the contexts
"Validate marketplace" and "Validate catalog", and a required context that never reports
stays pending forever. Change the ruleset before renaming a job.

| Gate | What fails | Function |
|---|---|---|
| Manifest schema | A missing or malformed `marketplace.json` or `plugin.json`, a name mismatch, a non-semver version, a source that escapes the root, a reserved marketplace name | `validate_manifests` |
| MCP pinning | An MCP arg ending in `@latest`, or a `git+` URL with no ref after the host, in `.mcp.json` or any `plugins/*/.mcp.json` | `validate_mcp_pins` |
| Frontmatter parses as YAML | Any `plugins/**/*.md` whose frontmatter does not survive `yaml.safe_load`, or does not parse to a mapping | `validate_frontmatter_yaml` |
| Eval schemas | A key set other than `{agent, query, files, expected_behavior}` or `{query, should_trigger, description}`, invalid JSON, a `triggers.json` that is not a flat list, or an `evals.json` fixture that does not resolve | `validate_evals` |
| Eval verdict leak | A `triggers.json` `description` matching a verdict phrasing, or naming an agent or skill the case's own `query` does not mention | `validate_evals` |
| Workflow DAG | `bmad/design/workflow-dag-draft.json` listing an agent not in the tree, or missing one that is. The file being absent also fails | `validate_workflow_dag` |
| Cross-plugin references | A `references/...` path that resolves neither beside the file nor at its plugin root while the line names no owner, or that names an owner the file is not in | `validate_cross_plugin_references` |
| Agent frontmatter | A missing `name` or `description`, a `name` that does not match the filename, a duplicate name, an invalid `model` or `effort` | `validate_agents` |
| Skill tool held | An agent body that mentions the `Skill` tool or tells itself to invoke a skill, while `Skill` is absent from `tools` | `validate_agents` |
| Description budget | Combined agent descriptions over 15000 tokens. Over 13000 is a warning | `validate_agents` plus `report` |
| Skill frontmatter | A `name` that does not match the directory, is over 64 characters, is not kebab-case or contains a reserved word; a `description` over 1024 characters; a `model`, `tools` or `color` key | `validate_skills` |
| SKILL.md body length | Over 500 lines | `validate_skills` |
| Reference links | A link from a `SKILL.md` body that does not resolve. More than one level deep is a warning | `validate_skills` |
| Plugin-root paths | A `${CLAUDE_PLUGIN_ROOT}/...` path that does not exist inside the owning plugin | `validate_plugin_root_refs` |
| Relative links | A `../`-style markdown link inside a plugin that does not resolve | `validate_relative_links` |
| Retired capabilities | Any word-boundary occurrence of a name in the `RETIRED` dict, backticked or in bare prose, anywhere in `plugins/`, `wiki/`, `docs/`, `bmad/`, `README.md` or `CLAUDE.md` | `validate_agent_references` |
| Official CLI | `claude plugin validate .` reporting a validation failure. A CLI that cannot run at all is reported, not enforced | workflow step |
| Safety hook | Any of the 24 cases in `hooks/tests/test-pre-tool-safety.sh` | workflow step |
| Clean-machine install | `scripts/test-clean-install.sh`, which installs every plugin into a throwaway `CLAUDE_CONFIG_DIR` and asserts frontmatter parses, `${CLAUDE_PLUGIN_ROOT}` is gone, reference paths resolve, counts match the tree, and uninstall is clean | workflow step |

Five more rules are checked and reported as **warnings**, which never fail the build:
a `SKILL.md` body over 400 lines with no `references/` directory, a `when to use` heading
inside a `SKILL.md` body, a reference file over 100 lines with no `## Contents`, an agent
body over 10 000 characters, and `model: opus` with no HTML comment in the body. All five
live in `validate_substance`. Two further warnings sit elsewhere: a missing
`## When to invoke` in an agent body, and a `SKILL.md` reference link more than one level
deep. Treat all of them as review comments the machine wrote for you, not as optional.

Three of the errors deserve a note, because they change how you work rather than what you
type.

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
`.github/scripts/validate_registry.py` with what to use instead, then fix every reference
in `plugins/`, `wiki/`, `docs/`, `bmad/`, `README.md` and `CLAUDE.md` in the same pull
request. The match is on word boundaries, not on backticks, so a mention in ordinary prose
fails the build too. That is deliberate: keying on the decorated spelling once let a
dispatch instruction naming a removed agent survive every cleanup pass. The lookbehind
excludes a colon, so a plugin-qualified name such as `pr-review-toolkit:code-reviewer` is
not flagged as the thing it replaces. `docs/registry/CHANGELOG.md`,
`docs/language-agnostic-design.md` and `docs/modernization/` are exempt, because recording
a removal necessarily names the thing removed. `archive/` is not scanned.

---

## 6. Before opening a PR

```bash
python3 .github/scripts/validate_registry.py
claude plugin validate .
bash hooks/tests/test-pre-tool-safety.sh
bash scripts/test-clean-install.sh
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
