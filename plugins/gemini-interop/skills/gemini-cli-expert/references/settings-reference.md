# Gemini CLI settings reference

Verified against `google-gemini/gemini-cli` at tag `v0.57.0`.

## Contents

- [Where settings live](#where-settings-live)
- [Keys that matter for a capability registry](#keys-that-matter-for-a-capability-registry)
- [Sub-agent overrides](#sub-agent-overrides)
- [Hooks](#hooks)
- [MCP servers](#mcp-servers)
- [Ignoring files](#ignoring-files)

## Where settings live

Seven configuration layers, each overriding the ones above it:

| # | Layer | Path |
|---|---|---|
| 1 | Default values | hardcoded in the application |
| 2 | System defaults file | `/etc/gemini-cli/system-defaults.json` (Linux), `/Library/Application Support/GeminiCli/system-defaults.json` (macOS), `C:\ProgramData\gemini-cli\system-defaults.json` (Windows), or `GEMINI_CLI_SYSTEM_DEFAULTS_PATH` |
| 3 | User settings file | `~/.gemini/settings.json` |
| 4 | Project settings file | `<project>/.gemini/settings.json` |
| 5 | System settings file | `/etc/gemini-cli/settings.json` (Linux), `/Library/Application Support/GeminiCli/settings.json` (macOS), `C:\ProgramData\gemini-cli\settings.json` (Windows), or `GEMINI_CLI_SYSTEM_SETTINGS_PATH` |
| 6 | Environment variables | including values loaded from `.env` |
| 7 | Command-line arguments | flags passed at launch |

Four of those are settings files: layers 2, 3, 4 and 5.

**Layer 5 is the one to know about on a managed workstation.** It is a second system-wide
JSON file, distinct from the system defaults at layer 2, and it overrides **all other
settings files**, including the user's own and the project's. The upstream doc states its
purpose plainly: it lets system administrators at enterprises keep control over their
users' Gemini CLI setups. When a setting appears not to take, check layer 5 before
suspecting a bug, and check whether `GEMINI_CLI_SYSTEM_SETTINGS_PATH` is repointing it.

There is **no "Admin" settings layer**, and `adminPolicyPaths` does not create one. It is a
top-level key set inside a system settings file, and its documented description is
"Additional admin policy files or directories to load". It feeds the Policy Engine's Admin
tier and has no effect at all on how `settings.json` files merge. The layer that gives an
administrator override authority over settings is layer 5 above, not this key. See
`references/tools-and-policy.md` for where `adminPolicyPaths` actually applies.

Extensions merge in at load time and lose to `settings.json` on any key they both set.

The `.gemini/` directory in a project is the workspace equivalent of `.claude/`: it holds
`settings.json`, `commands/`, `skills/`, `agents/` and `GEMINI.md`.

## Keys that matter for a capability registry

### `skills`

```json
{ "skills": { "enabled": true, "disabled": ["noisy-skill"] } }
```

Both require a restart. `disabled` is the escape hatch when a ported skill triggers too
eagerly, and is preferable to deleting it while the trigger is being tuned.

### `context`

```json
{ "context": { "fileName": ["AGENTS.md", "GEMINI.md"] } }
```

An array makes one repository legible to more than one agent CLI. Order is the order in
which files are searched for.

### `security`

| Key | Default | Effect |
|---|---|---|
| `security.disableYoloMode` | `false` | blocks `-y/--yolo` even when passed on the command line |
| `security.disableAlwaysAllow` | `false` | removes "Always allow" from confirmation dialogs |
| `security.enablePermanentToolApproval` | `false` | adds "Allow for all future sessions" |
| `security.autoAddToPolicyByDefault` | `false` | makes permanent approval the default for low-risk tools |
| `security.blockGitExtensions` | `false` | blocks installing and loading extensions from Git |
| `security.toolSandboxing` | `false` | isolates individual tools rather than the whole process |

`blockGitExtensions` is the one to check first in an enterprise environment: with it set,
`gemini extensions install <github-url>` fails and only local-path installs work.

### `tools`

| Key | Default | Effect |
|---|---|---|
| `tools.sandbox` | unset | boolean, a profile path, or `docker`/`podman`/`lxc`/`windows-native` |
| `tools.sandboxAllowedPaths` | `[]` | extra paths readable from inside the sandbox |
| `tools.sandboxNetworkAccess` | `false` | network from inside the sandbox |
| `tools.shell.enableInteractiveShell` | `true` | node-pty backed shell |
| `tools.shell.backgroundCompletionBehavior` | `"silent"` | `silent`, `inject` or `notify` when a background command ends |

## Sub-agent overrides

Built-in sub-agents are reconfigured under `agents.overrides`, keyed by agent name:

```json
{
  "agents": {
    "overrides": {
      "codebase_investigator": {
        "modelConfig": { "model": "gemini-3-flash-preview" },
        "runConfig": { "maxTurns": 50 }
      },
      "browser_agent": { "enabled": true }
    }
  }
}
```

`browser_agent` is the only built-in disabled by default. Note the shape difference from
a custom agent's frontmatter: here the model sits under `modelConfig.model` and turns
under `runConfig.maxTurns`, whereas a custom agent file spells them `model` and
`max_turns` at the top level.

## Hooks

Hooks are configured under a `hooks` object in `settings.json`, keyed by event name. An
extension ships them in `hooks/hooks.json` instead, never in the extension manifest.

```json
{
  "hooks": {
    "BeforeTool": [
      {
        "matcher": "run_shell_command",
        "sequential": true,
        "hooks": [
          {
            "type": "command",
            "name": "shell-safety",
            "command": "${extensionPath}/hooks/scripts/pre-tool-safety.sh",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

`timeout` is **milliseconds** here, default 60000. Claude Code's hook `timeout` is in
seconds. Copying a hook block between the two without converting gives a 5000 second
timeout or a 5 millisecond one, and neither errors.

## MCP servers

Declared under `mcpServers` in `settings.json`, or in an extension manifest. Every
option is supported in an extension except `trust`.

```json
{
  "mcpServers": {
    "uml": { "command": "npx", "args": ["-y", "uml-mcp-server@1.4.2"] }
  }
}
```

Pin an exact version or commit SHA. `@latest` makes the capability's behaviour a
function of the day it was installed.

## Ignoring files

`.geminiignore` works like `.gitignore` and applies to context gathering and to the
`@{...}` file injection used by custom commands. `respect_git_ignore` and
`respect_gemini_ignore` are per-call arguments on the file system tools.
