# Quick Start — Consuming Capabilities from this Catalog

This guide is for developers who want to start using shared capabilities in their project.

---

## Step 1: Find the capability you need

Browse `../claude-marketplace/catalog.json` or the `claude-marketplace/` directory.

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
| `presentation-creator` | Creating Accenture-branded PowerPoint presentations |
| `document-creator` | Creating Accenture-branded PDF or Word documents |
| `indexing-supervisor` | Phase 0: indexing a legacy Python (+ Streamlit) codebase into `.indexing-kb/` |
| `functional-analysis-supervisor` | Phase 1: AS-IS functional analysis from `.indexing-kb/` to `docs/analysis/01-functional/` (+ Accenture-branded PDF/PPTX exports) |
| `technical-analysis-supervisor` | Phase 2: AS-IS technical analysis to `docs/analysis/02-technical/` (+ PDF/PPTX exports) |
| `baseline-testing-supervisor` | Phase 3: AS-IS baseline regression suite at `tests/baseline/` (+ snapshots, benchmarks, optional Postman collection) |
| `refactoring-tobe-supervisor` | Phase 4: TO-BE refactoring (FIRST phase with target tech — Spring Boot 3 + Angular) — produces `backend/`, `frontend/`, OpenAPI contract, ADRs, migration roadmap |
| `refactoring-supervisor` | End-to-end refactoring workflow (Phases 0–4, with HITL + per-step execution timings between phases) |

---

## Step 2: Install with the setup script (recommended)

The easiest way to install capabilities is the interactive setup script:

```bash
./claude-catalog/scripts/setup-capabilities.sh /path/to/your-project
```

The script:
- Shows the full capability list with tiers
- Lets you select by number, or type `all` to install all stable capabilities
- **Automatically installs skill dependencies** — if you select `developer-java-spring`,
  the script also copies `java-spring-standards`, `testing-standards`, and
  `rest-api-standards` into your project's `.claude/agents/`
- Updates your project's `.claude/settings.json` with the `Agent(name)` permission rules

### What are skills?

Skills are shared knowledge providers used by multiple agents. You do not invoke them
directly — agents call them internally to load standards and conventions (e.g. Accenture
branding, Java/Spring patterns, REST design rules). You do not need to think about skills
when installing: the script handles them automatically.

---

## Step 3: Manual copy (alternative)

If you prefer to copy files manually:

```bash
mkdir -p .claude/agents
cp path/to/claude-marketplace/stable/software-architect.md .claude/agents/
```

Check `catalog.json` for any `"dependencies"` listed for the capability you install,
and copy those skill files from `claude-marketplace/skills/` as well.

---

## Step 4: Verify it works

Open Claude Code in your project. Type `/agents` to see the list of available subagents.
Your newly added capabilities should appear there.

Alternatively, start a task that naturally triggers the capability. For example, ask
"Can you review the architecture of this service?" — Claude Code should delegate to
`software-architect` automatically based on its description.

---

## Step 5: Configure settings (optional)

To allow Claude Code to use subagents without prompting for permission each time,
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

The setup script does this automatically. If you copied files manually, add the rules
yourself.

---

## Step 6: Project-specific customization (optional)

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

By default, you get whatever is in the marketplace at the time you install. If your
project needs to stay on a specific version:

1. Check `claude-marketplace/catalog.json` for the version you want
2. Check out the git tag: `git checkout software-architect@1.0.0 -- claude-marketplace/stable/software-architect.md`
3. Copy that version to your project

Document the pinned version in your project's CLAUDE.md so the team knows why
the version is frozen.
