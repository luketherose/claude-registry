# W7 install verification

Runtime verification of the claude-registry plugin marketplace against a fresh
clone of `https://github.com/luketherose/claude-registry`, not against the local
working tree.

| Field | Value |
|---|---|
| Verified commit | `756f883` (`feat(registry)!: migrate to official Claude Code plugin marketplace`) |
| Verified on | 2026-08-29 |
| Claude Code | 2.1.251 |
| Python | 3.14.6 |
| Scratch root | `/private/tmp/claude-501/-Users-luca-la-rosa-dev/e1925523-d57e-4f1b-b00d-da1cc5cf5b49/scratchpad/w7` |

## Verdict: PASS WITH GAPS

Everything the migration was supposed to fix is fixed and holds up at a second
filesystem location. All 114 `${CLAUDE_PLUGIN_ROOT}` references resolve, both in
the clone and in a simulated plugin cache. All 6 plugins are declared, resolvable
and internally consistent. The repo validator reports 0 errors and 0 warnings.

Three things keep this from a clean PASS:

1. **8 dangling read instructions** in the replatforming plugin, 6 of them the
   same root cause: `replatforming` still points at `deliberation` reference docs
   with relative paths that cannot cross a plugin boundary. Neither the
   `${CLAUDE_PLUGIN_ROOT}` fix nor the repo validator catches these, because they
   are written as bare relative paths in markdown tables rather than as
   `${CLAUDE_PLUGIN_ROOT}` references.
2. **One agent named but never defined**: `code-reviewer`.
3. **The end to end install was never executed.** `claude plugin validate`,
   `claude plugin list` and `claude plugin marketplace list` are all blocked on
   this machine by a managed settings failure. Structural verification is a proxy
   for an install, not a substitute for one. See "What could not be tested".

### Note on commit drift

`main` moved during this verification. At clone time the tip was `756f883`; by the
end of the run `git ls-remote` reported `f58d52d`.

```
git ls-remote origin refs/heads/main
f58d52debc0e407373efa3f5b7593d4c87f10005	refs/heads/main
```

`f58d52d` is `ci: split validation into the two contexts the main ruleset requires`
and touches only `.github/scripts/validate_registry.py` and
`.github/workflows/validate-pr.yml`. Zero paths under `plugins/` or
`.claude-plugin/` changed, so every structural finding below still applies to the
current tip. The newer validator was run as well and also passes.

---

## Step 1: fresh clone

```
mkdir -p <scratch>/w7
cd <scratch>/w7
git clone https://github.com/luketherose/claude-registry.git clone
cd clone
git rev-parse HEAD
```

Output:

```
Cloning into 'clone'...
756f88364155be8dc93730f0f653dac4a861bb86
```

The clone is clean, with no uncommitted state. Top level contains
`.claude-plugin/`, `plugins/`, `.github/`, plus the pre-migration directories
`hooks/`, `settings/`, `policies/`, `templates/`, `scripts/`, `archive/`, `bmad/`,
`wiki/` and a root `.mcp.json`.

---

## Step 2: structural verification

### 2.1 marketplace.json lists 6 plugins with resolvable sources

```
python3 -c "
import json,os
m=json.load(open('.claude-plugin/marketplace.json'))
for p in m['plugins']:
    src=p['source']
    print(p['name'], src, os.path.isdir(src), os.path.isfile(os.path.join(src,'.claude-plugin/plugin.json')))
"
```

Output:

```
replatforming            ./plugins/replatforming              dir=True  plugin.json=True
dev-standards            ./plugins/dev-standards              dir=True  plugin.json=True
deliberation             ./plugins/deliberation               dir=True  plugin.json=True
docs-branding            ./plugins/docs-branding              dir=True  plugin.json=True
analysis-architecture    ./plugins/analysis-architecture      dir=True  plugin.json=True
caveman                  ./plugins/caveman                    dir=True  plugin.json=True
```

All 6 expected plugins present, all 6 source paths resolve to a directory that
contains a plugin manifest. PASS.

### 2.2 Every plugin.json has name, description, version

```
replatforming            plugin.json=replatforming            match=True desc_match=True version=1.0.0
dev-standards            plugin.json=dev-standards            match=True desc_match=True version=1.0.0
deliberation             plugin.json=deliberation             match=True desc_match=True version=1.0.0
docs-branding            plugin.json=docs-branding            match=True desc_match=True version=1.0.0
analysis-architecture    plugin.json=analysis-architecture    match=True desc_match=True version=1.0.0
caveman                  plugin.json=caveman                  match=True desc_match=True version=1.0.0
```

`match` compares the plugin name in `marketplace.json` against the name in the
plugin's own `plugin.json`; `desc_match` compares the descriptions. Both agree on
all 6, so there is no split-brain between the marketplace entry and the manifest.
Every manifest also carries `author`, `repository`, `license`, `keywords` and
`category`. PASS.

Component inventory in the clone:

| plugin | agents | skills | commands |
|---|---:|---:|---:|
| replatforming | 58 | 4 | 0 |
| dev-standards | 12 | 29 | 0 |
| deliberation | 7 | 0 | 0 |
| docs-branding | 4 | 7 | 0 |
| analysis-architecture | 5 | 3 | 0 |
| caveman | 0 | 3 | 0 |
| **total** | **86** | **46** | **0** |

No duplicate agent names and no duplicate skill names across plugins, so nothing
collides when several plugins are installed together. All 46 `SKILL.md` files
carry both `name` and `description` frontmatter (0 problems).

### 2.3 `${CLAUDE_PLUGIN_ROOT}` resolution (the critical check)

A checker binds `CLAUDE_PLUGIN_ROOT` to each plugin directory in turn, the way
Claude Code does at load time, then resolves every textual reference found
anywhere inside that plugin. Script source is in the runbook at the end.

```
python3 check_plugin_root.py clone/plugins
```

Output:

```
plugins_dir = <scratch>/w7/clone/plugins
total ${CLAUDE_PLUGIN_ROOT} references found : 114
unique (plugin, path) pairs                : 78
unresolved references                      : 0

plugin                     refs  unresolved
analysis-architecture         7           0
deliberation                 28           0
dev-standards                 3           0
docs-branding                 7           0
replatforming                69           0

All references resolve.
EXIT=0
```

**114 references checked, 0 unresolved.** This is the check that was broken before
the migration, and it is now clean.

Two guards on the checker itself, so the zero is not an artefact of a weak regex:

- The literal string `CLAUDE_PLUGIN_ROOT` occurs 114 times under `plugins/` per
  `grep`, and the braced form `${CLAUDE_PLUGIN_ROOT}` also occurs 114 times. The
  counts match the checker's total, so no reference was skipped, and there are 0
  occurrences of the bare `$CLAUDE_PLUGIN_ROOT` form that Claude Code would not
  expand.
- Of the 78 unique targets, 0 needed trailing punctuation stripped to resolve, so
  none of the passes are lenient-parse false positives. 39 resolve to files and 39
  to directories.

### 2.4 The two `.mcp.json` files

`mcpServers` is declared in exactly two manifests, `dev-standards` and
`docs-branding`, both as `"./.mcp.json"`.

```
plugins/dev-standards/.mcp.json   exists=yes   JSON valid
plugins/docs-branding/.mcp.json   exists=yes   JSON valid
```

- `dev-standards` declares a stdio server `browser` running `@playwright/mcp`
  pinned at version 0.0.79 via `npx`.
- `docs-branding` declares a stdio server `uml` running `uml-mcp` via `uvx`, pinned
  to a git commit SHA, with `PLANTUML_SERVER` and `UML_OUTPUT_DIR` overridable
  through the environment.

Both files parse as valid JSON and both are inside their own plugin root, so the
relative `./.mcp.json` resolves correctly wherever the plugin is installed. PASS.

Not verified: whether these servers actually start. That needs `npx` and `uvx` to
fetch packages at runtime, which is an install-time concern, not a manifest one.

### 2.5 Repo validator

```
python3 .github/scripts/validate_registry.py
```

Full output:

```
<!-- claude-registry-validation -->
## Registry validation

### Subagent description budget

| plugin | agents | description tokens |
|---|---:|---:|
| `replatforming` | 58 | 6681 |
| `dev-standards` | 12 | 1482 |
| `deliberation` | 7 | 982 |
| `docs-branding` | 4 | 646 |
| `analysis-architecture` | 5 | 373 |
| **all enabled** | **86** | **10166** |

**Errors: 0 | Warnings: 0**

EXIT=0
```

The same command against the newer validator at `f58d52d` produces identical
numbers, with the marker changed to `claude-registry-validation-all`, and also
exits 0 with 0 errors and 0 warnings.

Worth knowing for CI: the `f58d52d` validator accepts an `only` option to run
either the manifest half or the capability half on its own.

---

## Step 3: CLI verification

```
cd <scratch>/w7/clone
claude plugin validate .
```

Output, verbatim:

```
Your organization requires remote managed settings to load, but they could not be loaded. Run `claude auth login` to re-authenticate, check your network connection, or contact your administrator.
```

Exit code 1.

As instructed, no authentication was attempted and the command was not retried in
a loop. Two single follow-up probes were made to establish the blast radius of the
block, because it matters for the runbook:

```
claude plugin --help          -> works, exit 0, full subcommand list printed
claude plugin list            -> same managed settings error
claude plugin marketplace list -> same managed settings error
```

So the CLI binary is fine and command parsing works. The block hits every
subcommand that needs to load settings, which is every subcommand that would
actually exercise the marketplace. `claude plugin validate <path>` is confirmed to
exist as a real subcommand in 2.1.251, described as "Validate a plugin or
marketplace manifest, or the skills, agents, and commands in a directory".

**This step is UNTESTED, not failed.** Nothing about the repo caused the error.

---

## Step 4: simulated install at a different path

Claude Code caches a marketplace as a full checkout under
`~/.claude/plugins/marketplaces/<marketplace-name>/`, with plugin roots at
`<marketplace>/plugins/<plugin-name>/`. This was confirmed by inspecting the
already-installed `claude-plugins-official` marketplace and
`~/.claude/plugins/known_marketplaces.json` read-only. Nothing under `~/.claude`
was modified.

The clone was copied into that shape inside the scratch directory:

```
rm -rf install-sim
mkdir -p install-sim/plugins/marketplaces
cp -R clone install-sim/plugins/marketplaces/claude-registry
rm -rf install-sim/plugins/marketplaces/claude-registry/.git
python3 check_plugin_root.py install-sim/plugins/marketplaces/claude-registry/plugins
```

Output:

```
plugins_dir = <scratch>/w7/install-sim/plugins/marketplaces/claude-registry/plugins
total ${CLAUDE_PLUGIN_ROOT} references found : 114
unique (plugin, path) pairs                : 78
unresolved references                      : 0

plugin                     refs  unresolved
analysis-architecture         7           0
deliberation                 28           0
dev-standards                 3           0
docs-branding                 7           0
replatforming                69           0

All references resolve.
EXIT=0
```

Identical to the in-clone run: 114 references, 78 unique targets, 0 unresolved.
Path independence holds.

Two additional path-dependence traps were checked in the copy:

| Check | Result |
|---|---|
| Absolute host paths (`/Users/luca`) anywhere under `plugins/` | 0 occurrences |
| References escaping the plugin root (`${CLAUDE_PLUGIN_ROOT}/..`) | 0 occurrences |
| Both `.mcp.json` files still parse at the new location | valid |

Nothing resolves only because of where the repo sits on disk. PASS.

---

## Step 5: pipeline trace

`/Users/luca.la.rosa/dev/sample-python-refactor` was confirmed to exist (a Python
project with `python/` and `refactor/` subdirectories) but **no migration was run
against it**, per instruction. What follows is a read-only trace of every file the
two supervisors tell a reader to open, checked against the clone.

### 5.1 indexing-supervisor

File: `plugins/replatforming/agents/indexing/indexing-supervisor.md` (54 lines).
Its reference table declares the base
`${CLAUDE_PLUGIN_ROOT}/references/indexing/` and lists 9 documents.

| Doc named in the table | Exists |
|---|---|
| `supervisor-protocol.md` | yes |
| `phase-plan.md` | yes |
| `dispatch-prompt-template.md` | yes |
| `manifest-spec.md` | yes |
| `sub-agents-catalog.md` | yes |
| `grounding-policy.md` | yes |
| `evidence-ledger-schema.md` | yes |
| `large-file-policy.md` | yes |
| `context-graph-schema.md` | yes |

**9 of 9 resolve. No dangling instruction.**

Sub-agents named in the prose also all exist as real agents:
`codebase-mapper`, `streamlit-analyzer`, `synthesizer`, `indexing-auditor`,
`functional-analysis-supervisor`, `technical-analysis-supervisor`,
`refactoring-supervisor`.

A second-level pass over those 9 documents found 10 sibling document tokens, of
which 3 do not resolve: `codebase-map.md` and `language-stats.md` in
`phase-plan.md:109`, and `graph-quality-report.md` in
`context-graph-schema.md:23`. All three are names of files the pipeline **writes**
into `.indexing-kb/` in the target repo, not files a reader is told to open. Not
defects.

### 5.2 refactoring-supervisor

File: `plugins/replatforming/agents/refactoring-supervisor.md` (97 lines). Base
declared as `${CLAUDE_PLUGIN_ROOT}/references/refactoring-workflow/`, table has 19
rows.

18 of 19 resolve: `bootstrap-protocol.md`, `schematics.md`,
`per-phase-protocol.md`, `iteration-loop.md`, `phase-verification-report.md`,
`decision-rules.md`, `deliberation-integration.md`, `deliberative-integration.md`,
`constraints.md`, `workflow-manifest-spec.md`, `phase-4-replatforming.md`,
`phase-4-step-5-5-test-data-seeding.md`, `phase-4-step-6-ui-smoke-gate.md`,
`ui-smoke-gate.md`, `retrospective.md`, `cross-phase-iteration.md`,
`activation-examples.md`, `supervisor-protocol.md`.

**1 of 19 is dangling.** See D1 below.

### 5.3 Dangling instructions found

All 8 are in the `replatforming` plugin. Line numbers are against `756f883`.

| ID | Location | Instruction | Why it dangles |
|---|---|---|---|
| D1 | `plugins/replatforming/agents/refactoring-supervisor.md:96` | read `../deliberation/integration-replatforming.md` | Resolves to `plugins/replatforming/references/deliberation/integration-replatforming.md`, which does not exist. The file exists only at `plugins/deliberation/references/deliberation/integration-replatforming.md`. |
| D2 | `references/refactoring-workflow/deliberation-integration.md:25` | read `../deliberation/trigger-lexicon.md` | Same cross-plugin boundary. Target lives in the `deliberation` plugin. |
| D3 | `references/refactoring-workflow/deliberation-integration.md:43` | read `../deliberation/schemas.md` | Same. |
| D4 | `references/refactoring-workflow/deliberation-integration.md:88` | read `../deliberation/integration-replatforming.md` | Same. |
| D5 | `references/refactoring-workflow/cross-phase-iteration.md:173` | route "per `integration-replatforming.md`" | Bare filename, no sibling of that name exists in `references/refactoring-workflow/`. Same target as D1. |
| D6 | `references/refactoring-workflow/iteration-loop.md:22` | "governed by `integration-replatforming.md`" | Same as D5. |
| D7 | `references/refactoring-workflow/per-phase-protocol.md:405` | see `refactoring-supervisor.md` section "Decision rules" | Two problems. The file is not a sibling of the reference directory, it is at `agents/refactoring-supervisor.md`. And that file has no "Decision rules" section; its only sections are Role, When to invoke, Reference docs. The decision table actually lives in `decision-rules.md`. |
| D8 | `references/refactoring-workflow/ui-smoke-gate.md:5` | `INFOSYNC-REFACTORING-AGENT-GAP-REPORT.md` "in the registry root" | The file exists, but at `archive/INFOSYNC-REFACTORING-AGENT-GAP-REPORT.md`, not the registry root, and it is outside every plugin root so an installed plugin has no supported way to reach it. |

D1 through D6 are one root cause: **the `replatforming` plugin references the
`deliberation` plugin's documents using relative paths that were valid when both
lived in one tree, and there is no cross-plugin path variable that can replace
them.** Splitting the monolith into 6 plugins severed these links. The
`${CLAUDE_PLUGIN_ROOT}` migration did not touch them because they were never
written as `${CLAUDE_PLUGIN_ROOT}` references.

Severity is uneven. D2 through D4 sit in `deliberation-integration.md`, which the
supervisor's own table labels "legacy doc", and a live replacement
(`deliberative-integration.md`) exists and resolves. D1, D5 and D6 are in
non-legacy paths and affect Phase 4 decision routing.

Not a defect but worth recording: the `deliberation` plugin's own
`deliberative-decision-engine.md` reaches the same documents correctly through
`${CLAUDE_PLUGIN_ROOT}/references/deliberation/...`, which resolves cleanly inside
its own plugin.

### 5.4 Undefined agent

`plugins/replatforming/agents/refactoring-supervisor.md:37` lists the fine-grained
Phase 4 sub-agents the supervisor orchestrates directly:

```
(`developer-java`, `developer-frontend`, `test-writer`, `debugger`,
`code-reviewer`, `api-designer`, `software-architect`)
```

Six of the seven resolve to agents in this registry. **`code-reviewer` is not
defined anywhere in the repository**, in any plugin or outside one. Searching for
`^name: code-reviewer` across every markdown file returns nothing.

This may still work by accident on a machine that has the official
`code-review` or `pr-review-toolkit` plugins installed, both of which ship an
agent by that name. That is an unstated external dependency, not a guarantee.

### 5.5 Other stale references inside plugins

Two survivors of the old layout, both low severity, neither breaking a read:

- `plugins/deliberation/evals/deliberative-decision-engine-eval.md:273` still
  instructs `cp claude-catalog/agents/deliberation/*.md .claude/agents/`. The
  `claude-catalog/` directory no longer exists.
- `plugins/analysis-architecture/agents/orchestrator.md:59` describes
  `~/.claude/agents/*.md` as the place where user-global agents live. This is
  still true for hand-installed agents, but it no longer describes where this
  registry's agents end up after a plugin install.

---

## What could not be tested, and why

| Not tested | Why | What the owner must do |
|---|---|---|
| `claude plugin validate .` | Blocked by the managed settings error quoted in Step 3. Organisation policy requires remote managed settings that failed to load. | Run `claude auth login` on a machine with working network access to the managed settings endpoint, then re-run the command in a clone. |
| `claude plugin marketplace add` and `claude plugin install` | Same block, and both mutate `~/.claude`, which this verification was forbidden from touching. | Run them yourself. This is the one check that proves the marketplace is installable rather than merely well-formed. |
| Agents and skills actually loading into a session | Requires a real install plus a Claude Code restart. | After installing, restart and confirm the agent and skill lists show the expected 86 agents and 46 skills. |
| MCP servers starting | `@playwright/mcp` needs `npx` plus a package fetch; `uml-mcp` needs `uvx` on PATH plus a git fetch. Neither was executed. | Install `dev-standards` and `docs-branding`, then confirm both MCP servers reach connected state. |
| An actual pipeline run against `sample-python-refactor` | Explicitly out of scope, and it mutates a real project. | Copy the project to a scratch directory first, then invoke `indexing-supervisor` there. |
| Behaviour of D1 through D6 at runtime | Requires an installed plugin and a Phase 4 decision point. Static tracing shows the read targets do not exist; it cannot show how the agent degrades when a read fails. | Trigger a Phase 4 decision point after installing and watch whether the supervisor errors, silently skips, or hallucinates the missing content. |

---

## Unpublished repo assets

Everything at the repo root outside `plugins/` and `.claude-plugin/` is cloned into
the marketplace cache but is not reachable through any plugin, because no
`plugin.json` declares it: `hooks/`, `settings/`, `policies/`, `templates/`,
`scripts/`, the root `.mcp.json`, and `.claude/`. No manifest declares a `hooks`
key. If any of that was expected to ship with the plugins, it does not.

---

## Runbook

Run in order, from a directory outside the working tree.

**1. Fresh clone**

```
git clone https://github.com/luketherose/claude-registry.git
cd claude-registry
git rev-parse HEAD
```

**2. Repo validator**

```
python3 .github/scripts/validate_registry.py
```

Expect `Errors: 0 | Warnings: 0`.

**3. Plugin root resolution**

Save this as `check_plugin_root.py` outside the repo, then run
`python3 check_plugin_root.py <path-to-clone>/plugins`. Expect 114 references and
0 unresolved.

```python
import glob as g, os, re, sys
REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}(/[^\s`\"'()<>|\]]*)?")
EXT = {".md", ".json", ".yaml", ".yml", ".sh", ".py", ".txt", ".toml"}
root_dir = os.path.abspath(sys.argv[1])
total, fails = 0, []
for plugin in sorted(os.listdir(root_dir)):
    root = os.path.join(root_dir, plugin)
    if not os.path.isdir(root):
        continue
    for dp, dn, fns in os.walk(root):
        dn[:] = [d for d in dn if d != ".git"]
        for fn in fns:
            if os.path.splitext(fn)[1] not in EXT:
                continue
            p = os.path.join(dp, fn)
            for ln, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
                for m in REF.finditer(line):
                    raw = (m.group(1) or "").lstrip("/")
                    total += 1
                    ok = False
                    for c in {raw, raw.rstrip(".,;:")}:
                        t = os.path.join(root, c) if c else root
                        ok = ok or (bool(g.glob(t)) if "*" in c else os.path.exists(t))
                    if not ok:
                        fails.append(f"{p}:{ln} -> {raw}")
print(f"references: {total}  unresolved: {len(fails)}")
for f in fails:
    print("  " + f)
```

**4. Path independence**

Copy the clone somewhere else and repeat step 3 against the copy. The two runs
must produce identical numbers.

```
cp -R claude-registry /tmp/registry-copy
python3 check_plugin_root.py /tmp/registry-copy/plugins
```

**5. CLI validation** (this is the step that failed here)

```
claude plugin validate .
```

If it reports the managed settings error, run `claude auth login` first, then
retry once.

**6. Real install** (this is the step that was never reached)

```
claude plugin marketplace add luketherose/claude-registry
claude plugin install replatforming@claude-registry
claude plugin install dev-standards@claude-registry
claude plugin install analysis-architecture@claude-registry
claude plugin install deliberation@claude-registry
claude plugin install docs-branding@claude-registry
claude plugin install caveman@claude-registry
```

Restart Claude Code, then confirm the agents and skills are listed and that the
`browser` and `uml` MCP servers connect.

**7. One real pipeline**

```
cp -R ~/dev/sample-python-refactor /tmp/sample-verify
cd /tmp/sample-verify
```

Ask for the indexing phase and confirm `.indexing-kb/` is produced. Then push
through to a Phase 4 decision point to see how D1 through D6 behave when the
supervisor tries to read a document that is not there.

**8. Fix the gaps before shipping**

- D1 to D6: decide how `replatforming` should reach `deliberation` documents. The
  options are to duplicate the documents into the `replatforming` plugin, to
  declare `deliberation` a dependency and reference it by an installed-plugin
  path, or to drop the cross-references and inline the rules.
- D7: repoint `per-phase-protocol.md:405` at `decision-rules.md`.
- D8: repoint `ui-smoke-gate.md:5` at `archive/`, or inline the finding.
- `code-reviewer`: define it in `dev-standards`, or remove it from the Phase 4
  sub-agent list, or document it as an external dependency.
- Add a check for bare relative document references to
  `.github/scripts/validate_registry.py`, since the current validator passes a repo
  that contains all 8 of these.
