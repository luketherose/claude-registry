<!--
audience: end-user
diataxis: tutorial
last-verified: 2026-08-30
verified-against: 8670a63
-->

# Quick start

Install one plugin, confirm Claude loaded it, and use it. Five minutes.

If your Claude Code configuration blocks adding marketplaces, skip to
[Installation](Installation#path-2-local-install-without-the-marketplace); the rest of
this page assumes the marketplace path works for you.

## Prerequisites

- **Claude Code**, recent enough for the frontmatter fields this registry uses. The
  current floor is **2.1.248**, set by `experimental.cacheTtl` on the supervisors. Check
  with `claude --version` and compare against
  [`docs/registry/version-requirements.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/version-requirements.md).
- **Read access** to `github.com/luketherose/claude-registry`.

Nothing else. The registry has no build step. Individual agents need their own runtimes
(`developer-java` is only useful where Maven and a JDK exist), but installing costs
nothing beyond Claude Code itself.

## 1. Add the marketplace

In Claude Code:

```
/plugin marketplace add luketherose/claude-registry
```

You add the marketplace once per machine.

## 2. Install a plugin

Start with the day-to-day one:

```
/plugin install dev-standards@claude-registry
```

That gives you 12 developer, test and API agents plus 29 standards skills. See
[Capability catalog](Capability-catalog#dev-standards) for the full list.

Install more only as a project needs them. Every enabled subagent description competes
for the same 15000-token delegation budget, and a smaller enabled set routes better.

| Situation | Install |
|---|---|
| Day-to-day development | `dev-standards` |
| Architecture and analysis work | `analysis-architecture` |
| A legacy migration project | `replatforming` plus `analysis-architecture` |
| Producing client deliverables | `docs-branding` |
| A hard, irreversible decision | `deliberation` |
| Terser output | `caveman` |

## 3. Confirm it loaded

Restart the session, then run:

```
/agents
```

You should see `developer-java`, `developer-python`, `developer-frontend`, `test-writer`,
`debugger` and `api-designer` among the listed agents.

## 4. Use one

Ask something that matches an agent's `description` and let Claude route:

> Add a REST controller for the `/orders` endpoint following our Spring conventions.

Claude delegates to `developer-java`, which loads the `java-spring-standards` and
`spring-architecture` skills with the `Skill` tool as the task touches their domains.

To pick the agent yourself, name it:

```
@debugger here is a stack trace, find the root cause: <paste>
```

## 5. Keep it current

Plugins update in the background when the resolved version changes. There is no sync
command and no script to re-run.

To pin a version instead of tracking `main`, use a `ref` in the marketplace source in
your `settings.json`. Release tags follow `<plugin>@<version>`, for example
`dev-standards@1.0.0`. See [Governance](Governance#releases).

## Common pitfalls

- **Nothing appears in `/agents`.** Restart the session. Plugin components are resolved
  at session start.
- **Adding the marketplace is refused.** Your configuration restricts marketplace sources
  (`strictKnownMarketplaces`). Use
  [the local install path](Installation#path-2-local-install-without-the-marketplace).
- **Routing feels vague and picks the wrong specialist.** You probably enabled every
  plugin. Disable what the project does not need; the combined description budget is the
  constraint that degrades first.
- **An agent reports it cannot read a bundled reference.** That path is written as
  `${CLAUDE_PLUGIN_ROOT}/references/...` and only expands inside an installed plugin. If
  you copied a single agent file by hand instead of installing the plugin, the reference
  cannot resolve. Install the plugin, or use `scripts/install-local.sh`, which rewrites
  those paths to absolute ones.

## Next steps

- [Usage](Usage) for the day-to-day patterns: delegation, direct invocation, the
  orchestrator, and the replatforming pipeline.
- [Capability catalog](Capability-catalog) for what each agent and skill does.
- [Contributing](Contributing) to write your own.
