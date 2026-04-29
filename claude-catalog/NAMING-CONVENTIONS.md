# Naming Conventions

## Subagent file names

Format: `{role}.md` or `{role}-{specialization}.md`

- Lowercase only
- Hyphens as separators, no underscores, no spaces
- No version numbers in filenames (versions live in git tags and catalog.json)
- Descriptive of the **role** the subagent plays, not the technology it uses

```
Good:
  software-architect.md
  functional-analyst.md
  developer-java.md
  code-reviewer.md
  api-designer.md

Bad:
  SoftwareArchitect.md       ← PascalCase
  java_spring_dev.md         ← underscores
  developer-java-v2.md ← version in name
  spring-boot-helper.md      ← technology-first, not role-first
```

## Subagent `name` frontmatter field

Must match the filename (without `.md`). This is what appears in the Claude UI and
what you use in `Agent(name)` permission rules.

```yaml
name: developer-java   ← matches developer-java.md
```

## Git tag format for releases

```
{name}@{MAJOR}.{MINOR}.{PATCH}
```

Examples:
```
software-architect@1.0.0
developer-java@2.1.0
functional-analyst@1.3.1
```

To tag all capabilities at once for a coordinated release, use a catalog-wide tag:
```
catalog@2026-04-19
```

## Template file names

Format: `{document-type}.md`

Examples:
```
architecture-decision-record.md
analysis-report.md
api-contract.md
functional-spec.md
```

## Policy file names

Format: `{technology-or-domain}-conventions.md`

Examples:
```
java-spring-conventions.md
python-conventions.md
rest-api-conventions.md
```

## Eval file names

Format: `{capability-name}-eval.md`

Examples:
```
software-architect-eval.md
functional-analyst-eval.md
```

## Version semantics (SemVer for capabilities)

| Change type | Version bump | Examples |
|---|---|---|
| Bug fix in prompt, no behavior change | PATCH | 1.0.0 → 1.0.1 |
| New behavior, backward compatible | MINOR | 1.0.0 → 1.1.0 |
| `name` or `description` change | MAJOR | 1.0.0 → 2.0.0 |
| Tools list change that removes a tool | MAJOR | 1.0.0 → 2.0.0 |
| Model change (e.g. sonnet → opus) | MINOR | 1.0.0 → 1.1.0 |
