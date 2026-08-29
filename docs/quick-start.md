# Quick start: using capabilities from this registry

For developers who want the team's agents and skills in their own project. Authoring a new
capability is a different job: see
[registry/how-to-write-a-capability.md](registry/how-to-write-a-capability.md).

The registry is a Claude Code plugin marketplace. You add the marketplace once, enable the
plugins you need, and updates arrive in the background. There is no file to copy and no
installer to run.

---

## Step 1: add the marketplace

```bash
/plugin marketplace add luketherose/claude-registry
```

To develop against a local clone instead:

```bash
claude plugin marketplace add .
```

---

## Step 2: enable the plugins you need

```bash
/plugin install dev-standards@claude-registry
```

Enable only what the project needs. Every enabled subagent description competes for the
same 15000-token delegation budget, and a smaller enabled set produces sharper routing.

| Situation | Enable |
|---|---|
| Day-to-day development | `dev-standards` |
| Architecture and analysis work | `analysis-architecture` |
| A legacy migration project | `replatforming`, plus `analysis-architecture` |
| Producing client deliverables | `docs-branding` |
| A hard, irreversible decision | `deliberation` |
| Terse output for prose, commits and reviews | `caveman` |

---

## Step 3: find the capability you need

Agents are delegated to by name. Skills are loaded by the agent that needs them, so you
never invoke a skill directly.

Commonly used agents, with the plugin that ships each one:

| Agent | Plugin | Use when |
|---|---|---|
| `software-architect` | `analysis-architecture` | Designing or reviewing architecture, writing ADRs |
| `functional-analyst` | `analysis-architecture` | Extracting requirements, writing use cases, mapping processes |
| `technical-analyst` | `analysis-architecture` | Auditing technical debt, security posture, dependency vulnerabilities |
| `orchestrator` | `analysis-architecture` | A task that spans several domains or is ambiguous in scope |
| `registry-auditor` | `analysis-architecture` | Auditing a Claude Code agent or skill registry against Anthropic's rubrics, read-only |
| `developer-java` | `dev-standards` | Writing or reviewing Java and Spring Boot code |
| `developer-python` | `dev-standards` | Writing or reviewing Python code |
| `developer-frontend` | `dev-standards` | Angular, React, Vue, Qwik or Vanilla JS/TS work |
| `test-writer` | `dev-standards` | Writing tests for existing code |
| `debugger` | `dev-standards` | Diagnosing a bug from an error message plus code |
| `api-designer` | `dev-standards` | Designing or reviewing REST API contracts |
| `documentation-writer` | `docs-branding` | Writing READMEs, runbooks, API guides |
| `wiki-writer` | `docs-branding` | Authoring or restructuring a GitHub wiki |
| `presentation-creator` | `docs-branding` | Accenture-branded PowerPoint |
| `document-creator` | `docs-branding` | Accenture-branded PDF or Word documents |
| `deliberative-decision-engine` | `deliberation` | Structured multi-agent debate on a high-stakes decision |

`dev-standards` also ships `developer-csharp`, `developer-go`, `developer-kotlin`,
`developer-php`, `developer-ruby` and `developer-rust`.

Code review lives in Anthropic's own `pr-review-toolkit` plugin, not in this registry.
Install it from the official marketplace and call `pr-review-toolkit:code-reviewer`.

### The replatforming pipeline

`replatforming` ships one entry point plus the phase supervisors it dispatches. Call
`refactoring-supervisor` for the whole workflow, or a phase supervisor to run one phase
standalone.

| Agent | Runs |
|---|---|
| `refactoring-supervisor` | The end-to-end workflow, Phases 0 to 4, with a checkpoint between every phase and every Phase 4 step |
| `indexing-supervisor` | Phase 0: indexing a legacy codebase into `.indexing-kb/` |
| `functional-analysis-supervisor` | Phase 1: AS-IS functional analysis into `docs/analysis/01-functional/` |
| `technical-analysis-supervisor` | Phase 2: AS-IS technical analysis into `docs/analysis/02-technical/` |
| `baseline-testing-supervisor` | Phase 3: AS-IS baseline regression suite at `tests/baseline/` |

Two further supervisors are deprecated in v3 of the workflow and retained only for the
legacy flow. `refactoring-tobe-supervisor` was the big-bang Phase 4, superseded by the
7-step incremental Phase 4 loop in `refactoring-supervisor`. `tobe-testing-supervisor` was
a separate Phase 5, now absorbed into Phase 4 Step 6. Neither appears in the workflow DAG
in `bmad/workflows.json`. Do not start new work on either.

The full roster, with one line per capability, is in the
[README](../README.md#available-capabilities).

---

## Step 4: verify it works

Open Claude Code in your project and run `/plugin` to see the enabled plugins, or
`/agents` to see the subagents they contribute.

Then start a task that should trigger the capability. Ask "review the architecture of this
service" and Claude Code should delegate to `software-architect` on its description alone.
If it does not, the description is the thing to fix, not the prompt.

---

## Step 5: pin the marketplace for the whole team

Commit this into the project's `.claude/settings.json` so every teammate gets the same
marketplace and the same enabled set when they trust the project:

```json
{
  "extraKnownMarketplaces": {
    "claude-registry": {
      "source": { "source": "github", "repo": "luketherose/claude-registry" }
    }
  },
  "enabledPlugins": {
    "dev-standards@claude-registry": true,
    "analysis-architecture@claude-registry": true
  }
}
```

To freeze a version, add a `ref` to the source pointing at a release tag, and say in the
project's `CLAUDE.md` why it is frozen. Without a `ref` you track `main` and pick up
changes in the background when the resolved version changes.

---

## Step 6: project-specific context (optional)

When a capability needs project-specific context (naming conventions, domain vocabulary,
an internal library), do not fork the agent. Put the context in the project's `CLAUDE.md`,
where it applies to every capability at once:

```markdown
## Project context (Payments Service)

- Package root: com.acme.payments
- Audit logging goes through com.acme.commons.audit.AuditLogger
- Monetary amounts are BigDecimal, never double or float
```

A fork is a copy that stops receiving updates and drifts from the registry within a
release or two. If the context is genuinely capability-specific and genuinely reusable,
propose it back here as a change to the capability instead.
