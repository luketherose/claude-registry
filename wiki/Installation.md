<!--
audience: operator
diataxis: how-to
last-verified: 2026-08-30
verified-against: c6c780a
-->

# Installation

Two supported install paths, in full. If you want to be running in five minutes and the
marketplace path works for you, use [Quick start](Quick-start) instead.

## Which path applies to you

| Path | Mechanism | Use when |
|---|---|---|
| [Path 1](#path-1-plugin-marketplace) | `/plugin marketplace add` plus `/plugin install` | Your Claude Code configuration allows adding this marketplace |
| [Path 2](#path-2-local-install-without-the-marketplace) | `./scripts/install-local.sh` | Enterprise policy restricts marketplace sources and this one is not among the authorised ones |

Path 2 exists because the `strictKnownMarketplaces` setting limits which marketplaces a
session may add. Where that setting is enforced by policy, Path 1 is refused and the
script is the way in. Which sources are authorised is decided by whoever manages that
policy, not by this repository.

Both paths deliver the same agents, skills and reference material.

## Prerequisites

- **Claude Code 2.1.248 or later.** That floor comes from `experimental.cacheTtl`, used
  by the supervisor agents. Confirm with `claude --version` and compare against
  [`docs/registry/version-requirements.md`](https://github.com/luketherose/claude-registry/blob/main/docs/registry/version-requirements.md),
  which lists the version that introduced every frontmatter field and marketplace feature
  in use.
- **Read access** to `github.com/luketherose/claude-registry`.
- For Path 2 only: **git**, **bash** and **python3**. The installer shells out to
  `python3` to rewrite bundled paths.

The registry itself has no build step. Individual agents need their own toolchains, so
`developer-java` is only useful in a project that already has Maven and a JDK.

---

## Path 1: plugin marketplace

### Add the marketplace

```
/plugin marketplace add luketherose/claude-registry
```

Once per machine.

### Install the plugins you need

```
/plugin install dev-standards@claude-registry
```

```
/plugin install analysis-architecture@claude-registry
```

Available plugin names: `replatforming`, `dev-standards`, `deliberation`,
`docs-branding`, `analysis-architecture`, `caveman`. See
[Capability catalog](Capability-catalog) for what each one contains.

### Enable a fixed set for a whole team

Commit this into the project's `.claude/settings.json`:

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

The marketplace is added automatically when a teammate trusts the project, and the listed
plugins are enabled by default.

### Choosing what to enable

Every enabled subagent description is loaded at session start and competes for the same
15000-token delegation budget. Enabling all six plugins puts roughly 11900 tokens of
descriptions into that budget and leaves little room for plugins from other marketplaces.
Enable per project.

| Situation | Enable |
|---|---|
| Day-to-day development | `dev-standards` |
| Architecture and analysis work | `analysis-architecture` |
| A legacy migration project | `replatforming`, plus `analysis-architecture` |
| Producing client deliverables | `docs-branding` |
| A hard, irreversible decision | `deliberation` |
| Terser output | `caveman` |

### Updating

Plugins update in the background when the resolved version changes. There is nothing to
run.

To pin instead of tracking `main`, add a `ref` to the marketplace source pointing at a
release tag. Tags are named `<plugin>@<version>`, for example `dev-standards@1.0.0`.

### Installing from a local checkout, for development

```bash
claude plugin marketplace add .
```

Run this from the repository root when you are testing a capability you are writing. See
[Contributing](Contributing).

---

## Path 2: local install without the marketplace

`scripts/install-local.sh` copies the registry into your Claude Code configuration
directory, in the layout each component type is loaded from.

### What it installs, and where

| Source | Destination | Notes |
|---|---|---|
| `plugins/<p>/agents/**/*.md` | `~/.claude/agents/<name>.md` | Flattened; nested directories collapse. Agent names are unique registry-wide, so nothing collides. |
| `plugins/<p>/skills/<name>/` | `~/.claude/skills/<name>/` | Copied whole, so `references/`, `scripts/` and `assets/` come along. This is where the `Skill` tool looks. |
| `plugins/<p>/references/` | `~/.claude/registry-references/<p>/` | Shared reference material for that plugin's agents. |

The destination root is `$CLAUDE_CONFIG_DIR` when that variable is set, and `~/.claude`
otherwise.

While copying agent files the script rewrites bundled paths:

- `${CLAUDE_PLUGIN_ROOT}/references` becomes `~/.claude/registry-references/<plugin>`
- a bare `${CLAUDE_PLUGIN_ROOT}` becomes `~/.claude/registry-references`

That rewrite is the whole point of the script. `${CLAUDE_PLUGIN_ROOT}` only expands
inside an installed plugin; outside one it stays a literal string and every bundled
reference silently fails to open. Skill directories need no rewrite, because their links
are relative and travel with the copied directory.

### Commands

```bash
./scripts/install-local.sh --list
```

Prints every plugin with its agent count, skill count and truncated description.

```bash
./scripts/install-local.sh
```

Installs the default set: `dev-standards`, `analysis-architecture`, `docs-branding`.
The default is the day-to-day set, chosen so the combined description budget stays well
clear of the ceiling.

```bash
./scripts/install-local.sh dev-standards docs-branding
```

Installs exactly the named plugins. An unknown name aborts the run before anything is
copied.

```bash
./scripts/install-local.sh --all
```

Installs all six. The script warns that combined subagent descriptions will sit near the
15000-token ceiling and that routing gets weaker.

```bash
./scripts/install-local.sh --uninstall
```

Removes every path recorded in the install manifest, then deletes the manifest.

```bash
./scripts/install-local.sh --help
```

### The install manifest

Each run writes `~/.claude/.registry-install-manifest`, one absolute path per line
covering every file and directory the script owns. `--uninstall` reads it back. Files you
put in `~/.claude/agents/` yourself are not listed and are never touched.

The script is idempotent. Re-running it replaces what it owns and leaves everything else
alone, so the update procedure is:

```bash
cd /path/to/claude-registry
git pull origin main
./scripts/install-local.sh dev-standards analysis-architecture
```

Restart Claude Code afterwards.

### MCP servers are not wired for you

`dev-standards` ships `plugins/dev-standards/.mcp.json` (Playwright, consumed by the
`browser-automation` skill) and `docs-branding` ships `plugins/docs-branding/.mcp.json`
(the UML server, consumed by `uml-diagram-generator`). Under Path 1 these are wired
through each `plugin.json`. Under Path 2 they are not. The script prints a note when it
installs a plugin that carries one, and you merge the `mcpServers` block into your
project's `.mcp.json` by hand.

### Limitations of Path 2 to be aware of

- No background updates. You pull and re-run the script.
- No per-project enable and disable. Everything installed is global to your user.
- MCP servers are a manual step.
- Agent files in `~/.claude/agents/` carry absolute rewritten paths, so moving or
  renaming `~/.claude/registry-references/` breaks them. Re-run the script after any such
  move.

---

## Verifying either path

```
/agents
```

lists the subagents available in the session. For a Path 2 install you can also check the
filesystem directly:

```bash
ls ~/.claude/agents | head
ls ~/.claude/skills | head
ls ~/.claude/registry-references
```

Restart the session before concluding that something failed to load. Components are
resolved at session start.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `/plugin marketplace add` is refused | Marketplace sources are restricted by policy. Use Path 2. |
| Agents do not appear in `/agents` | The session predates the install. Restart Claude Code. |
| An agent reports a missing reference file | The agent file was copied by hand rather than installed, so `${CLAUDE_PLUGIN_ROOT}` never expanded. Install the plugin, or run `scripts/install-local.sh`. |
| Routing picks the wrong specialist | Too many plugins enabled at once. Reduce the enabled set. |
| `unknown plugin '<name>'` from the installer | Typo in the plugin name. Run `./scripts/install-local.sh --list`. |
| Nothing to remove on `--uninstall` | No manifest at `~/.claude/.registry-install-manifest`, so the script has not run for this user. |
| The browser or UML MCP server is missing under Path 2 | Expected. Merge the plugin's `.mcp.json` into your project config by hand. |

## Related

- [Quick start](Quick-start): the five-minute version
- [Usage](Usage): what to do once installed
- [Capability catalog](Capability-catalog): what each plugin contains
- [Reference](Reference#install-paths): exact paths, flags and manifest format
