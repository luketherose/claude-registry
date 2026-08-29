# Naming conventions

## Agent file names

Format: `{role}.md` or `{role}-{specialization}.md`

- Lowercase only
- Hyphens as separators, no underscores, no spaces
- No version numbers in filenames. Versions live in git tags and in the plugin's
  `plugin.json`
- Descriptive of the **role** the agent plays, not the technology it uses

```
Good:
  software-architect.md
  functional-analyst.md
  developer-java.md
  api-designer.md
  documentation-writer.md

Bad:
  SoftwareArchitect.md        PascalCase
  java_spring_dev.md          underscores
  developer-java-v2.md        version in the name
  spring-boot-helper.md       technology-first, not role-first
```

The file may sit directly under `plugins/<plugin>/agents/` or in a subdirectory grouping a
pipeline phase, for example `plugins/replatforming/agents/indexing/`. The subdirectory is
organisational only. It is not part of the name, and it must not appear when the agent is
referenced from another capability's body.

## Agent `name` frontmatter field

Must match the filename without `.md`. CI fails when it does not. This is what appears in
the Claude Code UI and what you use in `Agent(name)` permission rules.

```yaml
name: developer-java   # in developer-java.md
```

A name may not start with `-` and may not contain `:`. The `plugin:capability` form is how
you reference a capability from another marketplace, for example
`pr-review-toolkit:code-reviewer`, and it is never the value of a `name` field here.

## Skill directory and `name`

A skill lives at `plugins/<plugin>/skills/<name>/SKILL.md`, and its `name` frontmatter
field must equal the directory name. CI additionally requires: at most 64 characters,
lowercase alphanumeric with hyphens, and neither `anthropic` nor `claude` anywhere in it.

Skill names describe the knowledge, not a role: `spring-data-jpa`, `testing-standards`,
`accenture-branding`.

## Git tag format for releases

A release publishes a plugin, so the tag names the plugin.

```
{plugin}@{MAJOR}.{MINOR}.{PATCH}
```

Examples:
```
dev-standards@1.3.0
replatforming@2.0.0
docs-branding@1.1.2
```

For a coordinated release across every plugin, use a registry-wide tag:
```
claude-registry@2026-08-30
```

## Template file names

Format: `{document-type}.md`, in `templates/`.

```
analysis-report.md
api-contract.md
architecture-decision-record.md
```

Scaffolding for a whole workflow gets its own directory instead, as
`templates/new-use-case/` does.

## Policy file names

Format: `{technology-or-domain}-conventions.md`, in `policies/`.

```
python-conventions.md
```

## Evaluation file names

Evaluations are JSON, not Markdown, and their directory carries the capability name:

```
plugins/<plugin>/evals/<capability-name>/evals.json
plugins/<plugin>/evals/<capability-name>/triggers.json
```

`<capability-name>` is the agent filename without `.md`, or the skill directory name.
Agents get both files. Skills get `triggers.json` only. See
`how-to-write-a-capability.md` for the schema of each.

## Version semantics

Semver applies to the **plugin**, in `plugins/<plugin>/.claude-plugin/plugin.json`. There
is no per-capability version and no `beta` or `stable` tier.

| Change type | Version bump |
|---|---|
| Prose, examples, evaluations or reference material only | PATCH |
| A capability gains behaviour without changing its contract | MINOR |
| A new capability is added to the plugin | MINOR |
| A capability's `name` or `description` changes | MAJOR |
| A capability is removed, or moves to another plugin | MAJOR |
| A `tools` list loses a tool | MAJOR |
| An output format a consumer parses changes | MAJOR |

`name` and `description` are routing contract: they decide when Claude delegates to the
capability. Changing either can silently break a consumer, which is why it is a major
bump. See `release-process.md` for the full procedure.
