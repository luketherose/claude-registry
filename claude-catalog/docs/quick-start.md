# Quick Start — Consuming Capabilities from this Catalog

This guide is for developers who want to start using shared capabilities in their project.

---

## Step 1: Find the capability you need

Browse `../claude-marketplace/catalog.json` or the `claude-marketplace/stable/` directory.

Common capabilities and when to use them:

| Capability | Use when |
|------------|---------|
| `software-architect` | Designing or reviewing architecture, writing ADRs |
| `functional-analyst` | Extracting requirements, writing use cases, mapping processes |
| `developer-java-spring` | Writing or reviewing Spring Boot code |
| `technical-analyst` | Auditing technical debt, security posture, code quality |
| `developer-python` | Writing or reviewing Python code |
| `code-reviewer` | Reviewing a PR or set of changed files |
| `test-writer` | Writing tests for existing code |
| `debugger` | Diagnosing a bug from error message + code |
| `api-designer` | Designing or reviewing REST API contracts |
| `documentation-writer` | Writing READMEs, runbooks, API guides |

---

## Step 2: Copy the subagent file to your project

```bash
mkdir -p .claude/agents
cp path/to/claude-marketplace/stable/software-architect.md .claude/agents/
```

The `.claude/agents/` directory is the official Claude Code location for project-scoped
subagents. Any `.md` file there with valid frontmatter is automatically available to
Claude Code when you work in that project.

---

## Step 3: Verify it works

Open Claude Code in your project. Type `/agents` to see the list of available subagents.
Your newly added capability should appear there.

Alternatively, start a task that naturally triggers the capability. For example, ask
"Can you review the architecture of this service?" — Claude Code should delegate to
`software-architect` automatically based on its description.

---

## Step 4: Configure settings (optional)

To allow Claude Code to use these subagents without prompting for permission each time,
add explicit `Agent(name)` rules to your `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Agent(software-architect)",
      "Agent(functional-analyst)",
      "Agent(developer-java-spring)"
    ]
  }
}
```

See `../settings/shared-settings-example.json` for a more complete example.

---

## Step 5: Project-specific customization (optional)

If a capability needs project-specific context (your company's naming conventions,
your specific frameworks, domain vocabulary), create a project-local override:

1. Copy the capability: `cp .claude/agents/developer-java-spring.md .claude/agents/developer-java-spring-payments.md`
2. Change the `name` field: `name: developer-java-spring-payments`
3. Add project-specific context at the end of the system prompt:
   ```
   ## Project context (Payments Service)
   - Package root: com.acme.payments
   - Uses our internal audit library: com.acme.commons.audit.AuditLogger
   - All monetary amounts use BigDecimal, never double or float
   ```

Keep overrides thin. The purpose is to add project context, not rewrite the capability.

---

## Pinning to a specific version

By default, you get whatever is in the stable tier of the marketplace at the time you
copy the file. If your project needs to stay on a specific version:

1. Check `claude-marketplace/catalog.json` for the version you want
2. Check out the git tag: `git checkout software-architect@1.0.0 -- claude-marketplace/stable/software-architect.md`
3. Copy that version to your project

Document the pinned version in your project's CLAUDE.md so the team knows why
the version is frozen.
