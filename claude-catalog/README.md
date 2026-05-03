# claude-catalog

Source repository for Claude Code shared capabilities.

This directory is the **authoritative source** for all team-owned Claude Code subagents,
prompt templates, policies, hooks, and MCP configuration patterns.

## Structure

| Directory / File | Purpose |
|---|---|
| `agents/` | Subagent definitions — official Claude Code `.md` format with YAML frontmatter |
| `templates/` | Reusable output templates: ADRs, analysis reports, API contracts |
| `policies/` | Coding conventions and style guides that subagents enforce |
| `examples/` | Sample invocations and expected outputs per capability |
| `evals/` | Evaluation scenarios for validating subagent behavior |
| `hooks/` | Hook scripts and settings.json examples for session automation |
| `settings/` | Reference settings.json examples (not deployed directly to projects) |
| `mcp/` | MCP server configuration examples with credential documentation |
| `docs/` | Internal documentation for contributors |
| `how-to-write-a-capability.md` | Step-by-step guide for new capability authors |
| `review-checklist.md` | PR review checklist for capability changes |
| `release-process.md` | Steps to release and publish a capability |
| `GOVERNANCE.md` | Decision-making process, roles, lifecycle |
| `NAMING-CONVENTIONS.md` | File and capability naming rules |
| `CONTRIBUTING.md` | How to contribute to this catalog |
| `CHANGELOG.md` | Record of all capability changes |
| `ANTI-PATTERNS.md` | Negative-knowledge log: capabilities and approaches that failed, why, what replaced them |

## Key concepts

**Subagent** is the official Claude Code term for a `.md` file placed in `.claude/agents/`.
When Claude Code encounters a relevant task, it can delegate to a subagent defined there.

**Capability** is this team's term for the full package: subagent + documentation +
examples + evals. A capability lives in this catalog; once approved and released, its
subagent file is published to `../claude-marketplace/`.

## Relationship to claude-marketplace

This directory is **source**. The `../claude-marketplace/` directory is **distribution**.
Only capabilities that pass review and are tagged with a git release are promoted to
the marketplace. Teams consume from the marketplace, not directly from this catalog.

## Quick start for contributors

1. Read `how-to-write-a-capability.md`
2. Create your subagent in `agents/your-capability-name.md`
3. Add examples in `examples/` and evals in `evals/`
4. Open a PR and apply `review-checklist.md`
5. After merge, follow `release-process.md` to tag and publish
