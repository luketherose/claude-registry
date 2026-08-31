---
name: gemini-extension-authoring
description: "This skill should be used when building, packaging or releasing a Gemini CLI extension: writing `gemini-extension.json`, laying out `commands/`, `skills/`, `agents/`, `hooks/` and `policies/`, using `${extensionPath}`, declaring settings and secrets, and publishing through a Git repository, a GitHub Release or the extension gallery. Trigger phrases: \"gemini extension\", \"gemini-extension.json\", \"publish a gemini extension\", \"gemini extensions install\", \"extension gallery\". Covers producing the distribution unit. It does not cover driving the CLI itself (that is `gemini-cli-expert`) or converting an existing Claude Code plugin (that is `cross-host-parity`)."
---

# Authoring a Gemini CLI extension

An extension is Gemini CLI's distribution unit, the counterpart of a Claude Code plugin.
It bundles MCP servers, custom commands, skills, sub-agents, hooks, policies, themes and
a context file behind one manifest.

Verified against `google-gemini/gemini-cli` at tag `v0.57.0`.

## Layout

```
my-extension/
  gemini-extension.json        required, at the extension root
  GEMINI.md                    context, loaded when the extension is active
  commands/                    TOML custom commands
    deploy.toml                becomes /deploy
    gcs/sync.toml              becomes /gcs:sync
  skills/
    security-audit/SKILL.md    becomes the security-audit skill
  agents/
    security-auditor.md        sub-agent, preview feature
  hooks/hooks.json             hooks, never declared in the manifest
  policies/rules.toml          Policy Engine rules, tier 2
```

Only `gemini-extension.json` is required. Every other directory is discovered by
convention, and none of them is declared in the manifest.

## The manifest

```json
{
  "name": "my-extension",
  "version": "1.0.0",
  "description": "One line, shown in the gallery.",
  "contextFileName": "GEMINI.md",
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${extensionPath}${/}server.js"],
      "cwd": "${extensionPath}"
    }
  },
  "excludeTools": ["run_shell_command(rm -rf)"],
  "settings": [
    {
      "name": "API Key",
      "description": "Key for the upstream service.",
      "envVar": "MY_API_KEY",
      "sensitive": true
    }
  ]
}
```

Rules the CLI enforces or silently depends on:

- `name` must equal the extension's directory name. A mismatch makes the extension fail
  to load with no error at the point of the mistake.
- `name` is lowercase letters, digits and dashes. Not underscores, not spaces.
- The manifest must sit at the **root** of the repository or release archive for the
  gallery crawler to see it.
- `contextFileName` is optional: a `GEMINI.md` present in the extension root is loaded
  even without it.
- MCP server config supports every option except `trust`.
- Separate the executable from its arguments. `"command": "node server.js"` is wrong;
  use `command` plus `args`.

The full field list, including `migratedTo`, `plan` and `themes`, is in
[references/manifest-reference.md](references/manifest-reference.md).

## Variables

| Variable | Expands to |
|---|---|
| `${extensionPath}` | absolute path to the extension directory |
| `${workspacePath}` | absolute path to the current workspace |
| `${/}` | platform path separator |

They are substituted in `gemini-extension.json` and in `hooks/hooks.json`. They are
**not** substituted in `SKILL.md`, in command TOML files or in `GEMINI.md`. A skill that
needs to name a bundled file uses a plain relative path from its own directory, which is
what the Agent Skills standard specifies and what the skill's granted directory access
makes readable.

## Settings and secrets

An extension does **not** inherit the user's shell environment. It sees standard safe
variables such as `HOME`, `PATH` and `TMPDIR`, plus exactly those declared in the
`settings` array via `envVar`. Anything else is filtered out.

Mark credentials `"sensitive": true`: the value goes to the system keychain and is
obfuscated in the UI. Users reconfigure with `gemini extensions config <name>`.

An extension that reads an undeclared environment variable will find it empty at runtime
and produce a confusing downstream failure. Declare every one.

## Commands, hooks and policies

Commands are TOML, arguments are `{{args}}`, shell output is injected with `!{...}` and
file content with `@{...}`. Hooks are JSON in `hooks/hooks.json`, with millisecond
timeouts. Policies are TOML in `policies/`, contributed at tier 2, and any `allow` or
`yolo` in them is ignored by design.

Details and worked examples are in
[references/commands-and-hooks.md](references/commands-and-hooks.md).

## Conflict resolution

Extension commands have the **lowest** precedence. When an extension command collides
with a user or project command, the extension's version is reachable only under a dotted
prefix, `/my-extension.deploy`. Skills follow the opposite ordering: workspace beats
user beats extension beats built-in.

Neither collision produces a warning. Check `/help` and `/skills list` after installing.

## Develop, install, release

```bash
gemini extensions new ./my-extension mcp-server   # scaffold from a template
gemini extensions link .                          # symlink for local development
gemini extensions validate ./my-extension         # structural check, before publishing
gemini extensions install <github-url|path> [--ref <ref>] [--auto-update]
gemini extensions update --all
gemini extensions disable <name> --scope workspace
```

`gemini extensions new <path> [template]` accepts **seven** templates, not the three the
`mcp-server` example suggests: `custom-commands`, `exclude-tools`, `hooks`, `mcp-server`,
`policies`, `skills`, `themes-example`. That list comes from `gemini extensions new --help`
on the installed 0.57.0 binary; `docs/cli/cli-reference.md` documents the command only as
`gemini extensions new <path>` and names no template at all. Scaffold from the template
closest to what you are building rather than starting from `mcp-server` by habit.

`gemini extensions validate <path>` is the counterpart of `claude plugin validate`. It is
documented at `docs/cli/cli-reference.md` and present in the binary. Run it before every
release: it is the only structural check that does not require starting a session.

`link` symlinks; `install` copies, so an installed extension needs `update` to pick up
upstream changes. All of these are terminal commands, not slash commands, and every one
of them takes effect only after the session restarts.

To have the gallery index a public extension, add the GitHub topic
`gemini-cli-extension` to the repository and keep the manifest at the root. The crawler
runs daily. There is no submission step.

Keep the manifest `version` equal to the GitHub release tag. The CLI detects updates from
tags but displays the manifest version, so a drift between them shows users a version
they do not have.

## Verifying before release

1. `gemini extensions validate ./my-extension`. Structural check, no session needed, and
   the cheapest gate to fail on.
2. `gemini extensions link .` then restart the session.
3. `/extensions list` shows the extension by name.
4. `/help` lists the commands, under the dotted prefix if a collision exists.
5. `/skills list` shows the bundled skills.
6. F12 opens the debug console; confirm the MCP server started and tools are registered.
7. Run once with `-e my-extension` only, so nothing else can mask a missing dependency.

If the extension ships hooks, check one more thing: renaming a hook or editing its
`command` between releases re-triggers Gemini's trust prompt for every existing user,
because project hooks are fingerprinted on `name` plus `command`. Freeze both and let the
script they point at absorb the changes.
