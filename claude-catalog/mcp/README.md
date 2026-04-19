# MCP (Model Context Protocol) Configuration

This directory contains reference examples for MCP server configuration.

---

## What is MCP?

MCP (Model Context Protocol) is an official Claude Code standard that allows external
tools and data sources to be exposed to Claude as callable tools. MCP servers run as
separate processes and communicate with Claude Code via a defined protocol.

MCP is configured in `.mcp.json` at the project root. This is an officially documented
Claude Code feature.

---

## When to use MCP — and when not to

### Use MCP when:
- You need Claude to access a data source that is **outside the project directory**
  and cannot be accessed with standard `Read`/`Grep`/`Glob` (e.g. a database,
  an external API, a wiki, a JIRA instance)
- The integration is **reused across multiple sessions** — the setup cost is worth it
- The tool needs to **return structured data** that Claude would otherwise have to
  extract from unstructured text

### Do NOT use MCP when:
- Files are in the project directory — use `Read`, `Grep`, `Glob` instead
- You need to run a shell command — use `Bash` instead
- You need a one-off web lookup — tell Claude to use `WebFetch` instead
- The MCP server setup is more complex than the benefit it provides

**The rule of thumb**: If you can solve the problem with the tools Claude Code already
has (`Read`, `Bash`, `WebFetch`), do not introduce an MCP server. MCP adds operational
complexity (another process to run, maintain, and secure).

---

## File format

`.mcp.json` is placed at the **project root** (not inside `.claude/`).
It is safe to commit to git **as long as it contains no secrets**.

```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-name"],
      "env": {
        "API_KEY": "${API_KEY_ENV_VAR}"
      }
    }
  }
}
```

Environment variable references (`${VAR}`) are expanded from the shell environment
at runtime. This is the correct way to provide secrets — never hardcode them.

---

## Transport types (official)

| Type | Use case |
|------|----------|
| `stdio` | Local process (most common for development tools) |
| `http` | Remote MCP server over HTTP/SSE |
| `ws` | Remote MCP server over WebSocket |

---

## Common MCP servers

These are community-maintained servers from the official MCP ecosystem.
Availability and quality vary — evaluate before adopting in production workflows.

| Server | Package | Provides |
|--------|---------|---------|
| Filesystem | `@modelcontextprotocol/server-filesystem` | Read/write to specified directories |
| PostgreSQL | `@modelcontextprotocol/server-postgres` | DB schema and query access |
| GitHub | `@modelcontextprotocol/server-github` | Issues, PRs, code search |
| Brave Search | `@modelcontextprotocol/server-brave-search` | Web search |

For the full list, see the official MCP documentation.

---

## Security considerations

- Grant MCP servers the minimum permissions needed
- Database MCP servers should use read-only credentials in all non-production contexts
- Never use a shared production database credential in development MCP configs
- Review what tools each MCP server exposes — some expose write operations by default
- `.mcp.json` with environment variable references is safe to commit; actual secret
  values must never be in the file
