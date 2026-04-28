<!--
audience: end-user
diataxis: how-to
last-verified: 2026-04-28
verified-against: 1e9445a
-->

# Usage

Common patterns once the capabilities are installed. This page assumes you
have already followed [Installation](Installation).

## How Claude picks a capability

Each capability is a `.md` file with a `description` field. Claude Code
reads those descriptions and decides automatically which subagent to
delegate to based on what you ask. You can also invoke an agent
explicitly.

**Automatic delegation:**

> "Review this PR for security issues"

Claude reads the descriptions of installed agents, sees that
`code-reviewer` matches "review … PR" and `security-analyst` matches
"security issues", and dispatches both (in parallel where independent).

**Explicit invocation:**

```
@developer-java-spring add a controller for the /orders endpoint
```

The `@<name>` form invokes a specific agent regardless of what
description Claude thought matched.

**Listing what's available:**

```
/agents
```

Lists every agent currently loaded in the session.

## Patterns

### One specialist for one task

```
@code-reviewer review the changes on this branch
```

```
@api-designer propose an OpenAPI spec for /products with pagination
```

```
@debugger here is a stack trace, find the root cause: <paste>
```

Use this when the task is clearly within one specialist's domain.

### Multi-domain tasks via the orchestrator

When a task spans multiple specialists ("design a feature", "review the
whole architecture"), invoke `orchestrator`:

```
@orchestrator I want to add OAuth2 to our Spring Boot service.
Recommend an architecture, design the API, and produce a code skeleton.
```

The orchestrator agent (model `opus`) discovers which specialists are
installed, decomposes the task into subtasks, dispatches them in parallel
where independent, and synthesises the result.

### Multi-phase refactoring pipelines

For end-to-end legacy modernisation (Python → Java/Spring + Angular)
the registry ships a six-phase pipeline. The single entrypoint is
`refactoring-supervisor`:

```
@refactoring-supervisor migrate the code at ~/dev/legacy-streamlit-app
```

It runs phases sequentially with explicit human-in-the-loop checkpoints
between each:

| Phase | Supervisor | Output | Read more |
|---|---|---|---|
| 0 — Indexing | `indexing-supervisor` | `.indexing-kb/` | [Architecture](Architecture#phase-0-indexing) |
| 1 — Functional analysis | `functional-analysis-supervisor` | `docs/analysis/01-functional/` | [Architecture](Architecture#phase-1-functional-analysis) |
| 2 — Technical analysis | `technical-analysis-supervisor` | `docs/analysis/02-technical/` | [Architecture](Architecture#phase-2-technical-analysis) |
| 3 — Baseline testing | `baseline-testing-supervisor` | `tests/baseline/` + report | [Architecture](Architecture#phase-3-baseline-testing) |
| 4 — TO-BE refactoring | `refactoring-tobe-supervisor` | `backend/`, `frontend/`, ADRs | [Architecture](Architecture#phase-4-to-be-refactoring) |
| 5 — TO-BE testing & equivalence | `tobe-testing-supervisor` | `01-equivalence-report.md` (PO sign-off) | [Architecture](Architecture#phase-5-to-be-testing) |

You can also run a single phase directly by invoking its supervisor.

### Document and presentation generation

Two agents produce Accenture-branded deliverables from project files:

```
@document-creator generate a PDF from docs/analysis/02-technical/ at /tmp/report.pdf
```

```
@presentation-creator generate an executive deck from docs/analysis/02-technical/
at /tmp/deck.pptx
```

Both are read-only on the source files; they only write the export.

## Project-specific overlays

Sometimes a global capability needs project-specific knowledge — your
internal logging library, an in-house naming convention, a domain glossary.
Put a thin overlay in your project:

```
your-project/.claude/agents/developer-java-spring-payments.md
```

Patterns:

- **Rename**, don't shadow. Use a distinct `name` so both files coexist
  in the directory.
- **Add, don't rewrite.** Reference the catalog capability by behaviour:
  "Follow `developer-java-spring` conventions but additionally use our
  internal `com.acme.logging` library and never persist a `User` record
  without the `tenantId` field."
- **Promote when stable.** When your overlay proves widely useful, open
  a PR to promote the addition to the catalog. See
  [Contributing](Contributing).

## Updating capabilities

Pull and re-run setup:

```bash
cd /path/to/claude-registry
git pull origin main
./claude-catalog/scripts/setup-capabilities.sh /path/to/your-project all
```

The script overwrites previously installed catalog files but leaves
project overlays untouched. Restart Claude Code to pick up the new
versions.

## Listing dependencies

If you want to know what skills an agent depends on, look at its entry
in `claude-marketplace/catalog.json`:

```bash
jq '.capabilities[] | select(.name == "developer-java-spring") | .dependencies' \
  claude-marketplace/catalog.json
```

The setup script uses this same field to auto-install skill
dependencies.

## When something goes wrong

- **Wrong agent picked.** Be more specific in your prompt, or invoke
  explicitly with `@name`.
- **Agent says it can't find a file.** Either the path is wrong, or you
  installed globally and are running in a project with a different
  directory layout. Provide the path explicitly.
- **An agent's behaviour changed unexpectedly.** Check
  [Changelog](Changelog) — the registry releases minor versions for
  behaviour changes and major versions for breaking ones.
- **Generated file with weird syntax in the repo root.** This was a
  past incident (Mermaid shell-injection in Phase 2, fixed 2026-04-28).
  Pull the registry to get the hardening; see [Changelog](Changelog).

## Related

- [Capability catalog](Capability-catalog) — the full list of what is
  installable, with descriptions
- [Reference](Reference) — fields, schemas, and conventions
- [FAQ](FAQ) — common questions
