# How to Write a Capability

A **capability** in this catalog is either an **agent** or a **skill** — both are
Claude Code subagents (`.md` files with YAML frontmatter), but they serve different
purposes and have different constraints.

| Type | Purpose | Model | Tools | Location |
|------|---------|-------|-------|---------|
| **Agent** | Performs a role: analyzes, writes code, designs, reviews | `sonnet` | Role-appropriate set | `agents/` |
| **Skill** | Provides knowledge: standards, conventions, brand rules | `haiku` | `Read` only | `skills/` |

Skills are not invoked directly by users. They are called by agents via the `Agent`
tool to load shared knowledge. A skill should contain knowledge that would otherwise
be copy-pasted into two or more agent system prompts.

This document is the authoritative guide for authors.

---

## 0. Skills — when and how to use them

### When to create a skill

Create a skill when:
- The same domain knowledge (coding standards, design rules, brand constants) appears
  in two or more agent system prompts
- The knowledge is declarative: it describes how things should be done, not what to do next
- The knowledge changes independently of any single agent's behavior

Do not create a skill for:
- Logic that is specific to one agent's workflow
- Behavior that needs tool access beyond reading files
- Content that is already short enough to inline without duplication

### Skill file format

```markdown
---
name: my-standards
description: >
  Use to retrieve [domain] standards: [list of topics].
tools: Read
model: haiku
color: cyan
---

## Role

You are a knowledge provider for [domain] standards. When invoked, return the
complete standards relevant to the task at hand.

## Standards

[The actual content — organized by topic, with specific rules and examples]
```

**Constraints for skills:**
- `model: haiku` — skills are knowledge retrieval, not reasoning
- `tools: Read` only — skills do not modify files, run commands, or spawn subagents
- No `## Skills` section — skills are leaf nodes
- No `Agent` tool — skills cannot delegate further

### Progressive disclosure — skill content layout

The Anthropic skill specification defines three loading levels for skill content. The
registry follows the same model so that skills stay cheap to load when only their
abstract is needed and expand on demand when the full content is required.

| Level | What it contains | When loaded |
|---|---|---|
| **1. Frontmatter** | `name`, `description`, `tools`, `model` | Always — at registry boot, with no body |
| **2. SKILL body** | The `## Role` and `## Standards` sections — the rules an agent applies | When an agent invokes the skill via the `Agent` tool |
| **3. `references/`** | Long-form details, full examples, exhaustive tables, code templates | Only when the skill body explicitly links to them |

The frontmatter alone must be enough for Claude to decide whether to invoke the skill.
The body alone must be enough to apply the skill in 90% of invocations. `references/`
is for the remaining 10% — when the agent needs an exhaustive list, a long template, or
a worked example.

**Soft and hard caps on body length**

| Cap | Word count | Action |
|---|---|---|
| Soft | 3 000 words | Body is large. Review whether dense reference material can move to `references/`. Not a blocker. |
| Hard | 5 000 words | Aligned with the Anthropic limit. The body must be split: keep the rules in the body, move long examples / tables / templates to `references/`. |

**`references/` directory layout**

```
claude-catalog/skills/<topic>/<skill-name>/
├── <skill-name>.md            # the skill body (level 2)
└── references/
    ├── <topic>-examples.md    # long worked examples
    ├── <topic>-templates.md   # full templates the skill body links to
    └── <topic>-deep-dive.md   # rare-but-needed deep details
```

When a skill grows from a flat file (`<skill-name>.md`) to a directory layout, both forms
remain supported by the validator. Move only when the body crosses the soft cap or when
a referenced section is long enough to harm scan-readability of the body.

**How the body links to references**

Use plain markdown links from the body to the reference files. The agent does not
auto-load `references/` — the body must point at the specific file when the agent needs
it. Do not paste a `references/` listing in the body; link only the files relevant to
the rule being stated.

```markdown
## Standards

…rules of the skill go here…

For full Java/Spring boilerplate templates, see
[`references/spring-templates.md`](references/spring-templates.md).
```

The link is a signal to the agent: "if you need this level of detail, read this file".

### Deterministic helpers — optional `scripts/` directory

> Claude orchestrates, the code executes.

Anything that is **deterministic, repeatable, or calculable** belongs in an executable
script — not in textual instructions that the model must interpret each time. Putting
deterministic logic in scripts produces results that are cheaper (fewer tokens),
faster, and reproducible across invocations.

A skill may ship a `scripts/` directory alongside its body. The agent that invokes the
skill runs the scripts via the `Bash` tool — the skill itself remains read-only
(`tools: Read`), it just declares the scripts as part of its standards.

| Goes in `scripts/` (deterministic) | Stays in the skill body (judgment) |
|---|---|
| Validating a JSON / YAML / OpenAPI document parses | Deciding whether an API contract is well-modelled |
| Counting cyclomatic complexity, words, sections | Deciding what an excessive complexity means in context |
| Checking naming-convention regex matches | Deciding when a naming convention should be relaxed |
| Generating a Mermaid / PlantUML diagram from a structured input | Deciding which entities deserve a diagram |
| Extracting a frontmatter field from a `.md` file | Deciding what the frontmatter should contain |

If the rule reads "given X, the answer is always Y", it belongs in a script. If the
rule reads "given X, consider Y while balancing Z", it stays in prose.

**Layout**

```
claude-catalog/skills/<topic>/<skill-name>/
├── <skill-name>.md            # the skill body
├── references/                # progressive-disclosure attachments (see previous section)
└── scripts/
    ├── README.md              # script index — one line per script
    ├── validate-something.py  # one script, one job, deterministic
    └── count-something.py
```

The `scripts/README.md` is mandatory when the directory exists — it documents each
script's **invocation, inputs, outputs, and exit codes**, so the consuming agent can
call the script correctly without reading the source.

**How a skill declares its scripts**

In the skill body, name the script explicitly and give the agent a Bash recipe.

```markdown
## Standards

For OpenAPI documents, validate that the spec parses with the canonical schema
checker before reviewing semantics. The deterministic check is shipped with this
skill:

    python3 claude-catalog/skills/api/openapi-standards/scripts/validate-openapi.py <path>

Exit code 0 means the spec is well-formed. Non-zero means a parse error — fix the
parse error before applying the rest of the standards.
```

The agent (which has `Bash` in its tools) executes the script when the skill body
points at it.

**When to introduce a `scripts/` directory**

Add scripts only when **at least one** of the following holds:

- The same deterministic check is described in two or more skills (the script
  becomes a single source of truth).
- The textual rule is a regex, a count, or a parse — the prose form is more verbose
  and less reliable than the executable form.
- A consumer agent has been observed reasoning incorrectly about the rule and the
  rule is mechanically verifiable.

Do not add a script just because something *could* be automated. The cost of
maintaining the script (tests, language runtime, documentation) must be lower than
the cost of the rule expressed in prose.

### How agents invoke skills

Add a `## Skills` section to the agent's system prompt:

```markdown
## Skills

Before starting any task, invoke the following skills to load shared standards:

- `java-spring-standards` — authoritative Java/Spring Boot conventions
- `testing-standards` — testing principles, scenario taxonomy, JUnit 5 templates

Apply the loaded standards to all code and recommendations in this session.
```

The agent calls the skill via the `Agent` tool at the start of each session. Skills
return their knowledge content; the agent applies it throughout the task.

### Adding a skill to the marketplace

When adding a skill to `catalog.json`, use `"type": "skill"` and `"tier": "skill"`.
For each agent that depends on the skill, add it to the agent's `"dependencies"` list —
the setup script uses this to auto-install skills alongside their dependent agents.

---

## 1. The subagent file format (official Claude Code standard)

A subagent is a `.md` file in `.claude/agents/` (or in this catalog under `agents/`).
It has two parts:

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
| `name` | string | Unique identifier. Lowercase, hyphens only. Must match filename. |
| `description` | string | Controls when Claude delegates to this subagent. This is the most critical field. |

### Optional frontmatter fields

| Field | Type | Example | Notes |
|---|---|---|---|
| `tools` | string | `Read, Grep, Glob, Bash` | Comma-separated. Omitting inherits all tools. Prefer explicit allowlists. |
| `disallowedTools` | string | `Write, Edit` | Tools to explicitly deny. |
| `model` | string | `sonnet`, `opus`, `haiku` | Default: inherits from parent session. Use `opus` only when reasoning depth justifies it. |
| `maxTurns` | integer | `10` | Limits agentic turns. Useful for bounded tasks. |
| `color` | string | `blue`, `green`, `red` | Visual indicator in the Claude UI. |

Do not add fields that are not in this list. Unrecognized fields are silently ignored
but create confusion.

---

## 2. The `description` field — most important

The `description` tells Claude **when to use** this subagent. It is used both for
automatic delegation (Claude decides to spawn this subagent) and for user-directed
invocation (user types `/agents` and selects it).

### Rules for a good description

- Start with "Use when" or "Use for"
- Be specific about the **trigger condition**, not just the domain
- List the key tasks it handles
- Mention what it does NOT handle (if there's a likely confusion)

```yaml
# Bad — too vague
description: Helps with software architecture.

# Bad — technology first, not role first
description: Works with Spring Boot applications.

# Good — specific trigger + task list
description: >
  Use when analyzing or designing system architecture, evaluating technology
  choices, writing Architecture Decision Records (ADRs), or reasoning about
  trade-offs across security, performance, scalability, cost, and maintainability.
  Does not write implementation code — delegates to developer subagents for that.
```

---

## 3. The system prompt — writing guidelines

The body of the `.md` file is the system prompt. It replaces the default Claude Code
system prompt when the subagent runs.

### Structure (recommended)

```markdown
## Role

One paragraph defining who this subagent is and what it is authoritative for.

## What you always do

Bullet list of mandatory behaviors. Things that happen in every interaction.

## What you never do

Explicit prohibitions. Include the reason when non-obvious.

## Output format

Define the exact format the subagent should produce. Consistency matters for
consumers who parse or post-process outputs.

## Quality criteria

How the subagent evaluates its own output before responding.
```

### Writing rules

1. **Be opinionated.** A generic prompt produces generic outputs. A capability should
   have strong opinions: specific output formats, named frameworks, explicit standards.
   A vague subagent is not useful.

2. **Define output formats explicitly.** If the subagent should produce an ADR, define
   the exact ADR structure. If it should produce a risk table, define the columns.
   Don't leave format to interpretation.

3. **Include completeness checks.** Tell the subagent what to verify before it responds.
   Example: "Before responding, check that you have addressed security, performance, and
   operational considerations. If the source code is needed and not provided, ask for it."

4. **Name the frameworks it follows.** "Use the C4 model for system diagrams" is better
   than "describe the system structure". Named frameworks produce consistent, recognizable
   output.

5. **Specify what it delegates.** If this subagent analyzes but does not implement,
   say so explicitly. "Do not write implementation code. If code changes are needed,
   describe them precisely and note which developer subagent should implement them."

6. **Define escalation.** Tell the subagent when to ask for more context before
   proceeding rather than guessing.

---

## 4. Tool permissions

Use the minimum set of tools needed. This reduces the blast radius of errors and makes
the capability's scope clear.

### Standard profiles

| Profile | Tools | Use for |
|---|---|---|
| Read-only analyst | `Read, Grep, Glob` | Analysis-only roles |
| Read + report | `Read, Grep, Glob, Write` | Analysis with written output |
| Full developer | `Read, Edit, Write, Bash, Grep, Glob` | Code writing and execution |
| Research | `Read, Grep, Glob, WebFetch` | Architecture / design with web lookup |

### Tool reference

| Tool | Purpose | Grant when |
|---|---|---|
| `Read` | Read files | Always grant to analysis roles |
| `Grep` | Search code and content | Always grant to analysis roles |
| `Glob` | Find files by pattern | Always grant to analysis roles |
| `Write` | Create new files | When producing deliverables (reports, specs) |
| `Edit` | Modify existing files | Developer roles only |
| `Bash` | Run shell commands | Developer and debugger roles; scope carefully |
| `WebFetch` | Fetch external URLs | Architecture research; risks for sensitive projects |
| `Agent` | Spawn other subagents | Orchestrator roles only |

---

## 5. Model selection

| Model | Use when |
|---|---|
| `sonnet` (default) | Standard analysis, code writing, documentation — use for most capabilities |
| `opus` | Deep reasoning tasks where answer quality justifies higher cost (rare) |
| `haiku` | Fast, high-volume, low-complexity tasks |

Default to `sonnet`. Only use `opus` if you can articulate why the task needs deeper
reasoning and cannot be handled by `sonnet`. Document the reason in a comment in the PR.

---

## 6. Quality criteria before submitting

Before opening a PR, verify:

- [ ] The `name` matches the filename exactly (without `.md`)
- [ ] The `description` starts with "Use when" or "Use for" and is specific
- [ ] The system prompt defines a clear role, not a vague helper
- [ ] Output formats are explicitly defined
- [ ] The tools list is minimal (not `*` unless genuinely necessary)
- [ ] No credentials, tokens, or secrets anywhere in the file
- [ ] At least one example exists in `examples/`
- [ ] At least two eval scenarios exist in `evals/`
- [ ] You have tested the subagent locally in at least one real scenario

---

## 7. When to create a new capability vs. modify existing

**Modify existing** when:
- The capability covers the right domain but is missing a behavior or output format
- A prompt bug causes consistently wrong output
- The model should change (e.g. upgrading to a newer Claude version)

**Create new** when:
- The role is genuinely different (different actor, different output, different tools)
- The specialization is deep enough that it would fragment an existing capability
- A project-specific override has proven broadly useful and deserves promotion

**Do not** create a new capability just to add technology-specific details that could
be provided as context at invocation time. For example, do not create
`developer-java-microservices.md` if `developer-java.md` can handle
microservices with the right context in the user message.

---

## 8. Global capability vs. project override

**Global capability** (this catalog):
- Applies across projects and domains
- Technology-aware but not domain-aware
- Contains no project-specific business rules, data models, or team conventions

**Project override** (project's `.claude/agents/`):
- A copy of a global capability with project-specific additions
- Adds domain context (e.g. "this service uses CQRS with Axon Framework")
- Adds team conventions (e.g. "always use our internal logging library X")
- Should be as thin as possible — add, don't rewrite

When a project override grows large, it's a signal that the global capability needs
to be more flexible, or that a new specialized capability should be created in this catalog.
