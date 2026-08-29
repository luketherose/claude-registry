# Claude Code version requirements

Frontmatter fields and marketplace features used by this registry, with the Claude Code
version that introduced them. Check this table after any Claude Code update.

**Current floor for everything in use: 2.1.248.**

| Feature | Minimum version | Used by |
|---|---|---|
| `experimental.cacheTtl` | 2.1.248 | The nine supervisors, set to `1h` |
| `maxTurns` partial marking and resume | 2.1.246 | Available, not yet used |
| `metadata.pluginRoot` in marketplace.json | 2.1.239 | `.claude-plugin/marketplace.json` |
| `headersHelper` for authenticated archives | 2.1.238 | Not used; needed only for a private artifact registry |
| Inline MCP servers require workspace trust | 2.1.238 | Plugin-level `.mcp.json` is unaffected |
| `source: archive` (zip) | 2.1.224 | Not used |
| Working-directory guard for `isolation: worktree` | 2.1.203 | Not used, see the note below |
| `manual` as an alias for `default` permission mode | 2.1.200 | Not used |
| `skills:` frontmatter preload | in use | `document-creator`, `presentation-creator`, `api-designer`, `test-data-seeder` |
| `effort` | in use | Supervisors, challengers, auditors, deliberation personas |
| `model: inherit` | in use | User-facing agents |
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

## After an update

```bash
claude --version
```

Compare against the table. If Claude Code required re-authentication against managed org
settings, run `claude auth login` before `claude plugin validate .`.
