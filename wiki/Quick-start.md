<!--
audience: end-user
diataxis: tutorial
last-verified: 2026-04-28
verified-against: 1e9445a
-->

# Quick start

Install the registry's capabilities into your project and verify Claude
delegates to one of them. Five minutes, four commands.

## Prerequisites

- **Claude Code** installed and working in a project (Mac, Linux, Windows
  with WSL/Git Bash). If `claude` doesn't run yet, follow the official
  Claude Code install guide first.
- **git** and **bash** (the install script is plain bash; no other build
  tooling is needed).
- **Read access** to this repository.

You don't need Python, Node, or any package manager. The registry has no
build step.

## 1. Clone the registry

```bash
git clone https://github.com/luketherose/claude-registry.git
cd claude-registry
```

Pull updates the same way you would for any other repo:

```bash
git pull origin main
```

## 2. Install the capabilities

Two common modes — pick one.

### Project-scoped (recommended for most projects)

```bash
./claude-catalog/scripts/setup-capabilities.sh /path/to/your-project
```

The script:
- reads `claude-marketplace/catalog.json` (the source of truth for what is
  installable)
- prompts you to choose `all`, a tier (`stable` / `beta`), or specific
  capabilities by name
- copies the selected `.md` files into `<project>/.claude/agents/`
- auto-installs every skill listed in the chosen agents'
  `dependencies`
- creates `<project>/.claude/agents/` if it doesn't exist

To install everything non-interactively:

```bash
./claude-catalog/scripts/setup-capabilities.sh /path/to/your-project all
```

### Global (every Claude Code session)

```bash
./claude-catalog/scripts/setup-capabilities.sh --global
```

This installs into `~/.claude/agents/`. Use this when you want the
catalog available in any Claude Code session, not just inside a specific
project.

## 3. Verify the install

```bash
ls /path/to/your-project/.claude/agents/ | head
```

You should see files like `software-architect.md`, `developer-frontend.md`,
`code-reviewer.md`, plus skills.

Open Claude Code in the project and run:

```
/agents
```

You should see the installed agents listed.

## 4. Use one

Ask Claude something that matches an agent's `description`. For example:

> "Review the authentication flow in `src/auth/` for security issues."

Claude will delegate to `security-analyst` (or `code-reviewer` plus the
`security-analyst` if you ask broadly). You can also invoke an agent
directly:

```
@code-reviewer please review the changes on this branch
```

## 5. Update later

The registry evolves; pull updates when you want them:

```bash
cd claude-registry
git pull origin main
./claude-catalog/scripts/setup-capabilities.sh /path/to/your-project all
```

The setup script overwrites previously installed `.md` files with the
newer versions from `claude-marketplace/`. Project-specific overlays you
created (any agent with a name not in the catalog) are left untouched.

## Common pitfalls

- **You ran `setup-capabilities.sh` from outside the registry root.** The
  script resolves paths relative to its own location, so running it from
  the registry root is safest. If you got "catalog.json not found", check
  your `pwd`.
- **Capability not appearing in `/agents`.** The agent's `name` in the
  frontmatter must be unique across the project's `.claude/agents/`
  directory. If two files declare the same `name`, only one wins.
- **You see "Agent not found" when invoking by `@name`.** The agent file
  exists but Claude hasn't loaded it yet — restart the Claude Code
  session.
- **You're on Windows and saw a long list of garbage files appear.** This
  was a known incident with one specific agent (Phase 2
  state-runtime-analyst, fixed in 2026-04-28). Update the registry to
  pull in the fix; see [Changelog](Changelog) for the entry.

## Next steps

- Read [Usage](Usage) for the day-to-day patterns (delegation, direct
  invocation, the orchestrator agent for multi-domain tasks).
- Read [Capability catalog](Capability-catalog) for what each agent does.
- If you want to write your own capability, jump to
  [Contributing](Contributing).
