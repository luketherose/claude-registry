<!--
audience: end-user
diataxis: how-to
last-verified: 2026-04-28
verified-against: 1e9445a
-->

# Installation

Full installation procedure for end users. If you want to be running in
five minutes, use [Quick start](Quick-start) instead — this page covers
prerequisites, modes, options, and troubleshooting in detail.

## Prerequisites

- **Claude Code** — the CLI, the desktop app, the web app, or any
  supported IDE extension. The capabilities are subagents that Claude
  Code loads from `.claude/agents/`.
- **git** — to clone and pull the registry.
- **bash** — the install script is plain bash. On Windows use Git Bash or
  WSL.

No Python, no Node, no other package managers required by the registry
itself. Individual agents may require their own runtimes (e.g.
`developer-java-spring` only helps if your project actually has Maven and
JDK 21 installed) but the registry itself is build-tool-free.

## Modes

The setup script supports three modes:

| Mode | Command | Use when |
|---|---|---|
| **Project-scoped** | `./setup-capabilities.sh /path/to/project` | You want capabilities in one specific project's `.claude/agents/` |
| **Global** | `./setup-capabilities.sh --global` | You want capabilities in every Claude Code session (`~/.claude/agents/`) |
| **Non-interactive** | `./setup-capabilities.sh /path/to/project all` | Automation / CI; installs every capability without prompting |

## Step by step

### Clone the registry

```bash
git clone https://github.com/luketherose/claude-registry.git
cd claude-registry
```

The registry has two top-level areas you should know about:

- `claude-catalog/` — development source (you only edit this if you
  contribute)
- `claude-marketplace/` — distribution (the install script reads this)

For installation, you only interact with `claude-marketplace/` indirectly,
through the script.

### Run the setup script

Project-scoped, interactive:

```bash
./claude-catalog/scripts/setup-capabilities.sh /path/to/your-project
```

The script:
1. Reads `claude-marketplace/catalog.json` (the manifest of installable
   capabilities).
2. Lists what is available, grouped by tier (`stable` / `beta`).
3. Asks you to choose: `all`, a single tier, or specific names.
4. Resolves dependencies — every agent's `dependencies` field lists the
   skills it needs; those skills are installed automatically.
5. Copies the chosen `.md` files into `<project>/.claude/agents/`
   (creating the directory if needed).

Project-scoped, non-interactive:

```bash
./claude-catalog/scripts/setup-capabilities.sh /path/to/your-project all
```

Global:

```bash
./claude-catalog/scripts/setup-capabilities.sh --global
```

Global mode installs into `~/.claude/agents/` and is the right choice
when you want capabilities available in every Claude Code session
without per-project setup.

### Verify

```bash
ls /path/to/your-project/.claude/agents/ | head -20
```

You should see a mix of agent names (e.g. `software-architect.md`,
`code-reviewer.md`, `developer-java-spring.md`) and skill names
(e.g. `java-spring-standards.md`, `testing-standards.md`).

In Claude Code, run:

```
/agents
```

This lists every agent currently available in the session. Names match
the `name` field in each `.md` file's YAML frontmatter.

## Updating

When the registry changes (new capabilities, fixes, version bumps):

```bash
cd claude-registry
git pull origin main
./claude-catalog/scripts/setup-capabilities.sh /path/to/your-project all
```

The script overwrites previously installed catalog files with their
newer versions. **Project-specific files** (any `.md` whose `name` is
not in `catalog.json`) are not touched — your local overlays survive.

## Selecting a subset

Sometimes you don't want everything. Two patterns:

### By tier

`stable` capabilities have been used in two or more projects without
critical issues for at least 30 days; `beta` are newer and may evolve.
Pick `stable` when you want maximum stability:

```bash
# Interactive — choose 'stable' when prompted
./claude-catalog/scripts/setup-capabilities.sh /path/to/your-project
```

### By name

Pick specific capabilities when you don't want the whole catalog:

```bash
# Interactive — choose 'select' and provide a comma-separated list
./claude-catalog/scripts/setup-capabilities.sh /path/to/your-project
# When prompted, enter:
#   software-architect,developer-java-spring,code-reviewer
```

The dependency resolver still kicks in: if you select an agent that
requires a skill, the skill is installed automatically.

## Uninstalling

The catalog has no install registry on the consumer side — files are
plain `.md` in `.claude/agents/`. To remove everything:

```bash
rm -rf /path/to/your-project/.claude/agents/
```

This deletes both catalog capabilities and any project-specific
overlays. To remove only the catalog files, delete the ones whose
`name` matches `claude-marketplace/catalog.json`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `catalog.json not found` | Run the script with its full path from inside the registry checkout. |
| `permission denied` on the script | `chmod +x ./claude-catalog/scripts/setup-capabilities.sh` |
| Agent not appearing in `/agents` | Restart the Claude Code session. The directory is read at session start. |
| Two agents with the same `name` | Only one wins. Rename your project-specific overlay (e.g. `developer-java-spring-payments.md`). |
| Setup hangs on Windows Git Bash | Make sure paths don't have spaces; if they do, quote them. |
| Capability changed but you still see the old behaviour | Pull the registry, re-run setup, restart Claude Code. |

## Related

- [Quick start](Quick-start) — the 5-minute version
- [Usage](Usage) — what to do once installed
- [Capability catalog](Capability-catalog) — the list of what is installable
- [Reference § Manifest fields](Reference#catalog-manifest) — what each
  field in `catalog.json` means
