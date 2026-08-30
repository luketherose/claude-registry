<!--
audience: end-user
diataxis: how-to
last-verified: 2026-08-30
verified-against: c6c780a
-->

# Usage

Day-to-day patterns once a plugin is installed. This page assumes you have followed
[Installation](Installation).

## How Claude picks a capability

**Agents** are chosen by their `description`. Claude reads the description of every
enabled subagent at session start and delegates on what you ask.

> Review the authentication flow in `src/auth/` and tell me what an attacker gets.

You can also name the agent, which bypasses the routing decision:

```
@developer-java add a controller for the /orders endpoint
```

```
/agents
```

lists the subagents available in the session.

**Skills** are loaded by whoever is already working, using the `Skill` tool, when the task
touches their domain. They do not appear in `/agents` and you rarely invoke one by hand.
An agent that needs a skill on every run preloads it through the `skills:` frontmatter
field instead. Four agents do this today: `api-designer` preloads `rest-api-standards`,
`document-creator` and `presentation-creator` preload `accenture-branding`, and
`test-data-seeder` preloads `test-data-seeding-standards`.

## Patterns

### One specialist for one task

```
@api-designer propose an OpenAPI 3.1 spec for /products with cursor pagination
```

```
@debugger here is a stack trace, find the root cause: <paste>
```

```
@test-writer add JUnit 5 tests for the payment service
```

Use this when the task sits inside one specialist's domain.

### Multi-domain tasks

When a task spans several specialists, or its scope is unclear, use the orchestrator from
`analysis-architecture`:

```
@orchestrator I want to add OAuth2 to our Spring Boot service. Recommend an
architecture, design the API, and produce a code skeleton.
```

It discovers which agents are available, decomposes the task, dispatches independent
subtasks in parallel and synthesises the result.

### A hard, irreversible decision

`deliberation` runs a structured debate instead of a single opinion:

```
@deliberative-decision-engine should we replace our Kafka consumer group with
a pull-based scheduler? Constraints: 40 services, 6-month window.
```

The engine dispatches independent personas (`debate-proposer`, `debate-critic`,
`debate-risk-reviewer`, `debate-operations-reviewer`,
`debate-replatforming-specialist`), runs challenge and rebuttal rounds, and has
`debate-judge` produce an auditable decision record. Reserve it for decisions that are
expensive to reverse; a full debate is not cheap.

### The replatforming pipeline

`replatforming` implements an end-to-end AS-IS to TO-BE migration in five phases. The
single entrypoint is `refactoring-supervisor`:

```
@refactoring-supervisor migrate the code at ~/dev/legacy-streamlit-app
```

It runs phases in order with a human-in-the-loop gate between each one.

| Phase | Supervisor | Writes | Read more |
|---|---|---|---|
| 0, Codebase indexing | `indexing-supervisor` | `.indexing-kb/` | [Architecture](Architecture#phase-0-codebase-indexing) |
| 1, Functional analysis | `functional-analysis-supervisor` | `docs/analysis/01-functional/` | [Architecture](Architecture#phase-1-functional-analysis) |
| 2, Technical analysis | `technical-analysis-supervisor` | `docs/analysis/02-technical/` | [Architecture](Architecture#phase-2-technical-analysis) |
| 3, Baseline testing | `baseline-testing-supervisor` | `tests/baseline/` | [Architecture](Architecture#phase-3-baseline-testing) |
| 4, Application replatforming | `refactoring-supervisor` drives it directly | `backend/`, `frontend/`, `docs/refactoring/`, `e2e/` | [Architecture](Architecture#phase-4-application-replatforming) |

Phases 0 to 3 are strictly AS-IS and never modify the legacy source. Phase 4 introduces
the target stack and runs as a seven-step loop (Step 0 through Step 6, with a Step 5.5 for
test-data seeding) where every feature iteration must leave the application in a working
state.

Each of Phases 0 to 3 also runs standalone:

```
@indexing-supervisor index this codebase
```

```
@technical-analysis-supervisor run Phase 2
```

Phase 4 does not run standalone; it requires Phases 0 to 3 complete.

On invocation the supervisor detects existing outputs per phase and asks what to do with
each: skip, re-run, revise, or regenerate exports only. The `exports-only` mode covers
the case where the analysis is complete but the Accenture-branded PDF or PPTX is missing.

### Documents and presentations

From inside a session:

```
@document-creator generate a PDF from docs/analysis/02-technical/ at /tmp/report.pdf
```

```
@presentation-creator generate an executive deck from docs/analysis/02-technical/
```

Both read the source material and write only the export.

From a shell, `scripts/present.sh` wraps the same agents through `claude -p`:

```bash
./scripts/present.sh ./estimation/
./scripts/present.sh --type pdf --audience tech ./docs/
./scripts/present.sh --type pptx --audience biz --project "Portal Modernization" \
  --output ~/Desktop/deck.pptx ./docs/
```

`--type` accepts `pptx`, `pdf` or `docx`; `--audience` accepts `biz` or `tech`. The
default output path is `./output/<project>.<type>`.

### Documentation

```
@documentation-writer write a runbook for the deployment procedure
```

```
@wiki-writer refresh the wiki after the new endpoint landed
```

`wiki-writer` writes Markdown into `wiki/` for review and never pushes to a wiki remote
on its own.

## Project-specific overlays

When a shared agent needs project knowledge such as an internal logging library or a
domain glossary, add an overlay in the project's own `.claude/agents/`:

```
your-project/.claude/agents/developer-java-payments.md
```

- **Give it a distinct name.** Two files declaring the same `name` collide and only one
  wins.
- **Add, do not restate.** Reference the shared agent's behaviour and state only the
  delta.
- **Promote what generalises.** When an overlay proves useful beyond one project, open a
  PR. See [Contributing](Contributing).

## Updating

Under the marketplace path, plugins update in the background when the resolved version
changes. Nothing to run.

Under the local install path:

```bash
cd /path/to/claude-registry
git pull origin main
./scripts/install-local.sh dev-standards analysis-architecture
```

Then restart Claude Code.

## When something goes wrong

- **The wrong agent was picked.** Be more specific, or name the agent with `@`. If it
  keeps happening, you probably have too many plugins enabled and the descriptions are
  competing.
- **An agent says a reference file is missing.** Its bundled paths did not resolve. See
  [Installation](Installation#troubleshooting).
- **An agent's behaviour changed unexpectedly.** Check [Changelog](Changelog). A change
  to a `name` or a `description` is a major bump precisely because it changes routing.
- **A phase supervisor asks about outputs you do not recognise.** It found artefacts from
  an earlier run. Read the state file it names before choosing re-run over skip.

## Related

- [Capability catalog](Capability-catalog): every agent and skill, with what it does
- [Reference](Reference): frontmatter fields, CI gates, paths
- [FAQ](FAQ): common questions
