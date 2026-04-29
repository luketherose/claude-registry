# How to Consume Capabilities

This guide explains how to use published capabilities from this marketplace in your project.

---

## The mechanism: Claude Code subagents

Published capabilities are **Claude Code subagents** — Markdown files with YAML frontmatter
that you place in your project's `.claude/agents/` directory. This is the official
Claude Code mechanism for custom specialized agents.

When a subagent file is present in `.claude/agents/`, Claude Code can:
- Automatically delegate tasks to it when the task matches its `description` field
- Allow you to invoke it explicitly via the `/agents` command
- Use it when the `Agent(name)` tool is called from another subagent

---

## Step 1: Choose a capability

Browse `../catalog.json` for a description of each available capability.
Choose based on the task you need to accomplish.

**Stable tier** capabilities are production-ready. Use them in any project.
**Beta tier** capabilities work but may have gaps in their system prompts. Suitable
for pilots and non-critical work.

---

## Step 2: Copy the subagent file to your project

```bash
# From your project root
mkdir -p .claude/agents

# Copy a stable capability
cp path/to/claude-marketplace/stable/software-architect.md .claude/agents/

# Copy a beta capability
cp path/to/claude-marketplace/beta/technical-analyst.md .claude/agents/
```

Commit `.claude/agents/` to your project's git repository so the whole team
gets the same capabilities.

---

## Step 3: Add permission rules (recommended)

To avoid being prompted for Agent permission on every delegation, add explicit rules
to `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Agent(software-architect)",
      "Agent(functional-analyst)",
      "Agent(developer-java)"
    ]
  }
}
```

Only add `Agent(name)` entries for capabilities your team has reviewed and trusts.

---

## Step 4: Use the capability

**Automatic delegation**: Claude Code reads each subagent's `description` field and
decides when to delegate automatically. If you ask "Can you review the architecture
of this service?", Claude should delegate to `software-architect` without explicit
instruction.

**Explicit invocation**: Type `/agents` in Claude Code to see the available subagents
and select one manually.

---

## Adding project context to a capability

If a capability needs project-specific knowledge (your naming conventions, your
internal libraries, your domain vocabulary), create a local specialization:

1. Copy the capability with a new name:
   ```bash
   cp .claude/agents/developer-java.md .claude/agents/developer-java-{project}.md
   ```
2. Change the `name` field in the frontmatter to match the new filename
3. Append a "Project context" section at the end of the system prompt:
   ```markdown
   ## Project context
   - Package root: com.acme.{service}
   - Uses internal library X for Y
   - Domain rule: ...
   ```

Do not rewrite the core prompt — only add project-specific context.
The project-local file overrides nothing globally; it is a new, separate subagent.

---

## Staying up to date

There is no automatic update mechanism. To get the latest version of a capability:

```bash
# Check current version in catalog.json
cat claude-marketplace/catalog.json | grep -A5 '"name": "software-architect"'

# Copy the updated file
cp claude-marketplace/stable/software-architect.md .claude/agents/software-architect.md

# Review the diff before committing
git diff .claude/agents/software-architect.md
```

Always review diffs before updating a capability that your team has been relying on.
A MINOR version update may change output format; a MAJOR update may require you to
update project-local specializations.
