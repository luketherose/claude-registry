# Claude Registry

Governance infrastructure for shared Claude Code capabilities across the team.

The registry lets you define, review, version, and distribute specialised subagents —
exactly like a shared code library, but for Claude's behaviour.

---

## Read the operational guide first

Everything you need to use or contribute to the registry is in the guide:

```
guida-operativa.pdf   (in the root of this repository)
```

The guide covers:
- **Part 1 — Using capabilities**: prerequisites, installation via script, verification, updates
- **Part 2 — Contributing**: creating a new capability, writing the system prompt, testing, opening a PR, handling review, publishing

If you just want to install capabilities in your project without reading everything:

```bash
./claude-catalog/scripts/setup-capabilities.sh /path/to/your-project
```

---

## Repository structure

```
claude-registry/
  claude-catalog/          ← source (development and review)
    agents/                  subagent .md files with YAML frontmatter
    skills/                  reusable knowledge providers (shared across agents)
    examples/                example invocations for capabilities
    evals/                   validation scenarios
    hooks/                   scripts and configurations for Claude Code hooks
    settings/                reference settings.json for projects
    mcp/                     MCP server configuration examples
    policies/                remaining conventions (not yet migrated to skills)
    templates/               output templates (ADR, report, API contract)
    docs/                    internal documentation for contributors
    scripts/
      setup-capabilities.sh  installs capabilities into a project (resolves dependencies)
      new-capability.sh      scaffolds a new capability or skill
    how-to-write-a-capability.md
    CONTRIBUTING.md
    GOVERNANCE.md
    CHANGELOG.md

  claude-marketplace/      ← distribution (approved capabilities only)
    stable/                  production-ready capabilities
    beta/                    new or experimental capabilities
    skills/                  shared skills (installed automatically as dependencies)
    catalog.json             manifest with versions, metadata, and dependencies

  guida-operativa.pdf      ← read this first
  pitch-claude-registry.pptx
```

---

## Available capabilities

### Agents (13)

| Name | Tier | Description |
|------|------|-------------|
| `software-architect` | stable | Architectural analysis, ADRs, trade-off evaluation |
| `functional-analyst` | stable | Requirements, use cases, business processes |
| `developer-java-spring` | stable | Java/Spring Boot enterprise development |
| `technical-analyst` | beta | Technical debt, security, vulnerable dependencies |
| `developer-python` | beta | Python/FastAPI development |
| `developer-frontend` | beta | Multi-framework frontend development (Angular, React, Vue, Qwik, Vanilla) |
| `code-reviewer` | beta | Structured code review on PRs or changed files |
| `test-writer` | beta | JUnit 5, Mockito, Testcontainers, pytest tests |
| `debugger` | beta | Bug diagnosis from stack traces, logs, and code |
| `api-designer` | beta | REST API design and review, OpenAPI specs |
| `documentation-writer` | beta | READMEs, runbooks, architectural guides |
| `presentation-creator` | beta | Accenture-branded slides (.pptx) from project documents |
| `document-creator` | beta | Accenture-branded documents (PDF/DOCX) from project documents |

### Skills

Skills are atomic knowledge providers shared across multiple agents. They are not
autonomous agents: they are invoked by agents to retrieve standards and conventions.
The `setup-capabilities.sh` script installs them automatically as dependencies.

| Name | Used by | Contents |
|------|---------|----------|
| `java-spring-standards` | developer-java-spring, code-reviewer, test-writer | Package structure, layering, testing, error handling, logging, security, Micrometer |
| `testing-standards` | developer-java-spring, test-writer, code-reviewer, developer-python | Principles, scenario taxonomy, naming, JUnit 5 / pytest / Jest templates |
| `rest-api-standards` | developer-java-spring, api-designer, code-reviewer | Resource modelling, HTTP methods, status codes, RFC 7807, OpenAPI 3.1 |
| `accenture-branding` | presentation-creator, document-creator | Colour palette, python-pptx constants, CSS PDF template, typography |
| `functional-analyst` | developer-frontend, functional-analyst | Functional behaviour reconstruction, feature lists, user flows, business rules |
| `uml-diagram-generator` | software-architect, functional-analyst, documentation-writer, doc-expert, backend-documentation, frontend-documentation, functional-document-generator | UML diagram rendering (class, sequence, component, activity, use-case, ER) via the `uml` MCP server (antoinebou12/uml-mcp) |
| + 36 frontend and backend skills | developer-frontend | Angular, React, Vue, Qwik, Vanilla, Python, Java, database, refactoring, orchestrators |

---

## Governance

- The `main` branch is protected: every change goes through a Pull Request with review
- GitHub Actions validates structure and completeness of every capability (catalog check first, then marketplace)
- SemVer versioning: PATCH = fix, MINOR = new behaviours, MAJOR = breaking change
- Promotion from `beta` to `stable` requires use in at least two projects and 30 days without critical issues

Details in [`claude-catalog/GOVERNANCE.md`](claude-catalog/GOVERNANCE.md).

---

## Useful links

| Resource | Path |
|----------|------|
| Operational guide (PDF) | [`guida-operativa.pdf`](guida-operativa.pdf) |
| How to write a capability | [`claude-catalog/how-to-write-a-capability.md`](claude-catalog/how-to-write-a-capability.md) |
| PR review checklist | [`claude-catalog/review-checklist.md`](claude-catalog/review-checklist.md) |
| Release process | [`claude-catalog/release-process.md`](claude-catalog/release-process.md) |
| Changelog | [`claude-catalog/CHANGELOG.md`](claude-catalog/CHANGELOG.md) |
| Team pitch (PPTX) | [`pitch-claude-registry.pptx`](pitch-claude-registry.pptx) |
