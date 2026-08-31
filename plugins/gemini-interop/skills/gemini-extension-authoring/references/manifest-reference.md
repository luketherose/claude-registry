# `gemini-extension.json` field reference

Verified against `google-gemini/gemini-cli` at tag `v0.57.0`.

## Contents

- [Fields](#fields)
- [Settings entries](#settings-entries)
- [Themes](#themes)
- [Migrating a repository](#migrating-a-repository)
- [Release channels](#release-channels)

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | Lowercase, digits, dashes. Must equal the directory name. Used for command conflict prefixes. |
| `version` | string | yes | SemVer. Keep equal to the GitHub release tag. |
| `description` | string | no | One line, shown at `geminicli.com/extensions`. |
| `contextFileName` | string | no | Defaults to loading a `GEMINI.md` found in the extension root. |
| `mcpServers` | object | no | Same shape as `settings.json`. Every option except `trust`. |
| `excludeTools` | string[] | no | Tool names, optionally with an argument filter: `run_shell_command(rm -rf)`. |
| `settings` | array | no | Declared configuration and secrets, see below. |
| `migratedTo` | string | no | New repository URL. The CLI follows it and re-points the installation. |
| `plan.directory` | string | no | Where planning artefacts go. Falls back to `~/.gemini/tmp/<project>/<session-id>/plans/`. |
| `themes` | array | no | Custom UI themes contributed by the extension. |

Directories are not declared. `commands/`, `skills/`, `agents/`, `hooks/` and `policies/`
are discovered by convention, and adding a key for them to the manifest does nothing.

## Settings entries

```json
"settings": [
  {
    "name": "API Key",
    "description": "Your API key for the service.",
    "envVar": "MY_API_KEY",
    "sensitive": true
  }
]
```

| Field | Purpose |
|---|---|
| `name` | display name in the configuration prompt |
| `description` | shown to the user when they are asked for the value |
| `envVar` | the environment variable the extension and its MCP servers will see |
| `sensitive` | `true` stores the value in the system keychain and obfuscates it in the UI |

Values are persisted in a `.env` inside the extension directory, except sensitive ones,
which go to the keychain. `gemini extensions config <name> [setting] [--scope <scope>]`
edits them after installation, and `--skip-settings` on install defers the prompts.

The allowlist is the point: an extension sees `HOME`, `PATH`, `TMPDIR` and whatever it
declared here. Nothing else from the user's shell reaches it.

## Themes

```json
"themes": [
  {
    "name": "shades-of-green",
    "type": "custom",
    "background": { "primary": "#1a362a" },
    "text": { "primary": "#a6e3a1", "secondary": "#6e8e7a", "link": "#89e689" },
    "status": { "success": "#76c076", "warning": "#d9e689", "error": "#b34e4e" },
    "border": { "default": "#4a6c5a" },
    "ui": { "comment": "#6e8e7a" }
  }
]
```

Selected with `/theme` or `ui.theme`. An extension theme is referred to with the
extension name in parentheses: `shades-of-green (my-green-extension)`.

## Migrating a repository

When an extension moves, the old repository keeps working as a redirect:

```json
{ "name": "my-extension", "version": "1.1.0", "migratedTo": "https://github.com/new-owner/new-repo" }
```

Publish that as a new version in the old repository. On the next update check the CLI
verifies the new source, re-points the installation and carries the settings across.
Users take no action.

## Release channels

Two distribution paths.

**Git repository.** Users run `gemini extensions install <repo-uri>`, optionally with
`--ref=<branch|tag|commit>`. Pushing to the referenced branch prompts installed users to
update. `HEAD` is always treated as latest. The default branch should be the stable
channel; a `dev` branch serves as preview.

**GitHub Releases.** Faster to install, since it ships an archive instead of cloning.
The CLI looks for the release marked **Latest**; `--pre-release` opts into others.

The only hard requirement `docs/extensions/releasing.md` states about archive contents is
that archives must be fully contained extensions, with `gemini-extension.json` at the root
of the archive and the rest of the layout matching a standard extension. Nothing there
forbids shipping extra files.

Trimming the archive is separate advice, and it comes from
`docs/extensions/best-practices.md` under "Clean artifacts": ensure archives only contain
necessary files such as `dist/`, `gemini-extension.json` and `package.json`, and exclude
`node_modules/` and `src/` to minimize download size. Treat that as a size optimisation, not
as something the installer enforces. An archive carrying `src/` still installs.

Note the interaction with enterprise policy: `security.blockGitExtensions` blocks both
Git installs and Git-sourced loading. Where it is set, only local-path installs work, so
an internal registry needs a distribution mechanism that does not depend on a GitHub
URL reaching the workstation.
