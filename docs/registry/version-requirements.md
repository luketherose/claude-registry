# Claude Code version requirements

Frontmatter fields and marketplace features used by this registry, with the Claude Code
version that introduced them. Check this table after any Claude Code update.

**Current floor for everything in use: 2.1.248.**

| Feature | Minimum version | Used by |
|---|---|---|
| `experimental.cacheTtl` | 2.1.248 | 9 agents, all at `1h`: the 7 supervisors in `replatforming`, plus `orchestrator` and `deliberative-decision-engine` |
| `maxTurns` partial marking and resume | 2.1.246 | Available, not yet used |
| `metadata.pluginRoot` in marketplace.json | 2.1.239 | `.claude-plugin/marketplace.json` |
| `headersHelper` for authenticated archives | 2.1.238 | Not used; needed only for a private artifact registry |
| Inline MCP servers require workspace trust | 2.1.238 | Plugin-level `.mcp.json` is unaffected. `dev-standards` and `docs-branding` each wire one through `mcpServers` in their `plugin.json` |
| `source: archive` (zip) | 2.1.224 | Not used |
| Working-directory guard for `isolation: worktree` | 2.1.203 | Not used, see the note below |
| `manual` as an alias for `default` permission mode | 2.1.200 | Not used |
| `skills:` frontmatter preload | in use | `document-creator`, `presentation-creator`, `api-designer`, `test-data-seeder` |
| `effort` | in use | 24 agents at `high`: supervisors, challengers, auditors, `orchestrator`, `registry-auditor` and the deliberation personas |
| `model: inherit` | in use | 19 user-facing agents. The other 67 pin a model: 24 `opus`, 43 `sonnet` |
| `background` | in use | `registry-auditor` |

## Deliberately not adopted

**`isolation: worktree` on the code-generating pipeline workers.** It looked like an obvious
fit for `backend-scaffolder`, `frontend-scaffolder`, `data-mapper`, `logic-translator` and
`test-data-seeder`. It is not. A worktree is branched from the default branch and is
discarded when unchanged, but those workers write into `backend/` and `frontend/` in the
main tree and later phases read what they wrote. Isolating them would hide their output
from the supervisor and break the pipeline.

**`background: true` on the challengers.** Challengers produce reports that a supervisor
reads and gates on. `background: true` forces background execution even when the caller
wants the result inline, which would break the gate. Only `registry-auditor`, which runs
standalone, uses it.

**`permissionMode: plan` on the analyst workers.** They all hold `Write` because they emit
their findings to the knowledge base. Plan mode is read-only and would break them.

## Pinned versions outside the frontmatter

Not a Claude Code version requirement, but checked by the same CI run and equally prone to
silent drift. Every MCP server spec names an exact version or commit SHA, and
`validate_mcp_pins()` fails the build on `@latest` or on a `git+` URL with no ref.

| Server | Pin | Declared in |
|---|---|---|
| `browser` (`@playwright/mcp`) | `0.0.79` | `.mcp.json`, `plugins/dev-standards/.mcp.json` |
| `uml` (`antoinebou12/uml-mcp`) | `78137bd66bfeb9754d0d5de0be1016f4dc053cc6` | `.mcp.json`, `plugins/docs-branding/.mcp.json` |

The root config and the plugin config for a given server must carry the same pin. They
drifted once, when the root ran `@latest` while both plugin configs were pinned, so the
same server ran a different build depending on which config won.

## After an update

```bash
claude --version
```

Compare against the table. If Claude Code required re-authentication against managed org
settings, run `claude auth login` before `claude plugin validate .`.
