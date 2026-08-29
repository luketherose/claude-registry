# W7 final audit: post-migration closing gate

Audit target: commit `756f883` (`feat(registry)!: migrate to official Claude Code plugin marketplace`).
Audit date: 2026-08-29. Scope: verification of the claimed pre-migration fixes, plus a hunt for
regressions the migration introduced and gaps against current Anthropic guidance.

Sources fetched for this audit (not worked from memory):
`https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`,
`https://code.claude.com/docs/en/sub-agents`,
`https://code.claude.com/docs/en/plugin-marketplaces`, and the locally installed official skills
under `~/.claude/plugins/cache/claude-plugins-official/plugin-dev/*/skills/` and
`.../skill-creator/*/skills/skill-creator/SKILL.md`.

## Verdict

The migration's *structural* work is sound: manifests conform, skill frontmatter is exactly `name`
plus `description` across all 46 skills, every skill body is under 500 lines, all 21 skill reference
links resolve one level deep, and all 114 `${CLAUDE_PLUGIN_ROOT}` paths resolve inside their owning
plugin. The migration's *behavioural* work did not happen. Two defects make the registry substantially
non functional at runtime and neither is caught by CI: no agent can invoke the `Skill` tool, because
all 86 agents carry a `tools:` allowlist that omits it, which silently disables the entire "skills as
knowledge providers" architecture that `CLAUDE.md` describes; and 70 relative links in agent bodies
and reference files still point at the pre migration `docs/` tree, so every pipeline supervisor's
"Reference docs" table is a list of dangling read instructions. The combined subagent description
budget is 11,798 tokens measured with a real tokenizer against the validator's reported 10,166, a
16 percent undercount that leaves a real margin of 1.7 percent rather than the apparent 18 percent,
and rises to 14,073 of the documented 15,000 ceiling once the official plugins this user already has
enabled are counted. Outside `plugins/`, the retired catalog and marketplace model is still documented
as live in 13 of 14 `wiki/` pages, all 4 `bmad/` files, `docs/quick-start.md`, `templates/new-use-case/`
and the 1,500 line `guida-operativa.tex`, and the user's own global `~/.claude/CLAUDE.md` still
instructs the retired `setup-capabilities.sh --global` update path.

Two caveats on this audit's own reliability, stated rather than glossed. First, `claude plugin validate .`
could not be run: it aborts with `Your organization requires remote managed settings to load`, so the
official CLI's verdict on the manifests is unverified and only the repo validator plus manual schema
comparison back finding 1.4. Second, a concurrent agent is actively rewriting `plugins/*/skills/*/`,
`plugins/*/evals/` and 11 replatforming agent files while this audit ran; all Part 1 verdicts and the
Part 2 counts below were re measured against committed `HEAD` to exclude that churn, and the in flight
work is called out separately in P2-2 because it is introducing a new defect.

## Part 1: verification of the claimed fixes

| # | Finding | Verdict | Evidence |
|---|---|---|---|
| 1.1a | Every `${CLAUDE_PLUGIN_ROOT}` path resolves inside its owning plugin | **CONFIRMED** | Custom checker walked all files under `plugins/`, extracted 114 refs (replatforming 69, deliberation 28, analysis-architecture 7, docs-branding 7, dev-standards 3), verified each resolves and stays within its plugin root. Output: `PROBLEMS: 0`. Reproduce: `python3 .github/scripts/validate_registry.py` (its `validate_plugin_root_refs` covers the same ground and reports no error). |
| 1.1b | No repo relative path to bundled material survives anywhere in `plugins/` | **NOT FIXED** | 70 relative links to bundled material remain, none using `${CLAUDE_PLUGIN_ROOT}`. See P2-2. Also 1 surviving retired path marker: `plugins/deliberation/evals/deliberative-decision-engine-eval.md:273` contains `cp claude-catalog/agents/deliberation/*.md .claude/agents/`. Confirm: `grep -rn "claude-catalog" plugins` |
| 1.2 | Combined subagent description budget under 12000 tokens | **PARTIAL** | Measured with `tiktoken`: **11,798** tokens (`cl100k_base`) / **11,890** (`o200k_base`) across 86 agents and 55,376 description characters. Under 12,000 by 1.7 percent, which is inside tokenizer error. The validator reports **10,166**, a 16.05 percent undercount caused by `WORDS_TO_TOKENS = 1.35` at `.github/scripts/validate_registry.py:24`. With the official plugins this user has enabled the real total is **14,073** of the documented 15,000 ceiling. See P3-1. Confirm: `python3 .github/scripts/validate_registry.py` then compare to a real tokenizer. |
| 1.3a | All skills at `plugins/<plugin>/skills/<name>/SKILL.md` | **CONFIRMED** | All 46 SKILL.md files sit at exactly that depth. Confirm: `find plugins -name SKILL.md | grep -cv '^plugins/[^/]*/skills/[^/]*/SKILL.md$'` returns `0`. |
| 1.3b | Frontmatter contains exactly `name` and `description` | **CONFIRMED** | Key census over committed `HEAD` yields exactly `46 name` and `46 description`, no other key. Confirm: `git ls-tree -r HEAD --name-only \| grep SKILL.md \| while read f; do git show "HEAD:$f" \| awk 'NR==1&&/^---/{fm=1;next} fm&&/^---/{exit} fm&&/^[A-Za-z_][A-Za-z0-9_-]*:/{sub(/:.*/,"");print}'; done \| sort \| uniq -c` |
| 1.3c | SKILL.md bodies under 500 lines | **CONFIRMED** | Largest body is 478 lines (`plugins/docs-branding/skills/frontend-documentation/SKILL.md`); none exceed 500 at `HEAD` or in the working tree. Descriptions are all under the 1,024 character limit. Confirm: `python3 .github/scripts/validate_registry.py` |
| 1.3d | Reference links resolve and stay one level deep | **CONFIRMED** | All 21 relative links inside SKILL.md files resolve to real files and none has more than one `/`. Confirm: `python3 .github/scripts/validate_registry.py` (`validate_skills` enforces both). Note this verdict covers SKILL.md only; links in *agent* bodies are unchecked by CI and are badly broken, see P2-2. |
| 1.4 | `marketplace.json` and every `plugin.json` conform to the documented schema | **CONFIRMED, with one caveat** | Compared field by field against the fetched `plugin-marketplaces` schema. `marketplace.json` has required `name`, `owner.name`, `plugins[]`; all 6 sources use the required `./` prefix and resolve; `metadata.pluginRoot` is valid; `claude-registry` is not a reserved name. All 6 `plugin.json` files carry `name` (matching), `description`, semver `version`, `author.name`; the two `mcpServers` string paths resolve. Caveat: `license: "UNLICENSED"` is not a valid SPDX identifier, see P3-3. **Unverified by the official CLI**: `claude plugin validate .` fails with an org managed settings error, not a schema error. Confirm: `python3 .github/scripts/validate_registry.py` |
| 1.5 | Agent frontmatter uses only documented fields with valid values | **CONFIRMED** | Key census over 86 agents yields only documented fields: `name`, `description`, `tools`, `model`, `color` (86 each), `effort` (24), `experimental` (9), `skills` (4), `background` (1). Values check out: `model` in {`sonnet` 43, `opus` 24, `inherit` 19}; `effort: high`; `background: true`; `experimental.cacheTtl: 1h`; all 4 `skills:` preloads resolve to real in plugin skills. `color` needs a note, see P3-6, but the registry's 6 colour set is safe. Confirm: `for f in $(find plugins -path '*/agents/*.md'); do awk 'NR==1&&/^---/{fm=1;next} fm&&/^---/{exit} fm&&/^[A-Za-z_][A-Za-z0-9_-]*:/{sub(/:.*/,"");print}' "$f"; done \| sort \| uniq -c` |

## Part 2: what the migration broke or missed

Ranked by impact on a user actually running these capabilities.

### P2-1 CRITICAL: no agent can invoke the `Skill` tool, disabling the whole skill architecture

All 86 agents declare an explicit `tools:` allowlist and **not one includes `Skill`**. The
sub agents documentation is unambiguous that `tools` is an allowlist and that omitting `Skill`
is precisely how you prevent an agent from invoking skills. `CLAUDE.md` meanwhile states
"Agents load skills on demand with the `Skill` tool", and 7 agent bodies give explicit
instructions to do so. Those instructions cannot execute.

Runtime consequence: a user invokes `developer-java`, the body says "load `java-spring-standards`,
`spring-expert`, `spring-data-jpa`", the agent cannot, and it silently substitutes its own priors
for the team's standards. This is the failure mode the standards exist to prevent, and it fails
without any error. Only the 4 agents using `skills:` frontmatter preload get skill content at all.

Exact locations of the contradiction (`tools:` is line 4 in every case):

| Agent | Instruction |
|---|---|
| `plugins/dev-standards/agents/developers/developer-java.md` | `:51` "Before performing any task, load the following skills with the `Skill` tool when the task touches their domain" |
| `plugins/dev-standards/agents/developers/developer-python.md` | `:33` "Before performing any task, load the following skills with the `Skill` tool" |
| `plugins/dev-standards/agents/test-writer.md` | `:32` "Before writing tests, load the following skills with the `Skill` tool" |
| `plugins/analysis-architecture/agents/software-architect.md` | `:39` "load the relevant skills with the `Skill` tool to inform architectural decisions" |
| `plugins/dev-standards/agents/debugger.md` | `:32` "Invoke the relevant skill based on the language/framework being debugged" |
| `plugins/dev-standards/agents/developers/developer-frontend.md` | `:69`, `:71`, `:80`, `:140` an entire "Step 2 / Step 3 invoke the framework skill set" protocol |
| `plugins/replatforming/agents/refactoring-tobe/test-data-seeder.md` | `:81` "Before starting any task, invoke the following skill to load shared" |

Cheapest confirmation:

```bash
grep -rln '^tools:' plugins | wc -l          # 86 agents carry an allowlist
grep -rn  '^tools:.*Skill' plugins | wc -l   # 0 of them permit Skill
```

### P2-2 CRITICAL: 70 dangling read instructions in agent bodies and reference files

The migration renamed `plugins/<plugin>/docs/` to `references/` but did not rewrite the links that
point into it. Of 157 relative markdown links under `plugins/`, **102 fail to resolve**; excluding
three classes of intentional template link (GitHub wiki page names in
`plugins/docs-branding/references/documentation/wiki-writer/page-templates.md`, the generated KB
"Quick links" block in `plugins/replatforming/references/indexing/synthesizer/output-spec.md`, and a
regex inside a table at `plugins/replatforming/references/indexing/dependency-analyzer/detection-patterns.md:89`),
**70 are genuinely broken**. 67 are mechanically repairable by rewriting `docs/` or `agents/` to
`references/`; the remaining 3 point into another plugin entirely.

Every pipeline supervisor is affected. `plugins/replatforming/agents/tobe-testing/tobe-testing-supervisor.md:53-58`,
`plugins/replatforming/agents/refactoring-tobe/refactoring-tobe-supervisor.md:63-71`,
`plugins/replatforming/agents/technical-analysis/technical-analysis-supervisor.md:54-63`,
`plugins/replatforming/agents/functional-analysis/functional-analysis-supervisor.md:52-60` and
`plugins/replatforming/agents/baseline-testing/baseline-testing-supervisor.md:57-67` each open with a
"Reference docs, read on demand" table in which every row is dead. The supervisor is instructed to
read its own protocol, output layout, phase plan and dispatch template before doing anything, and
none of those reads can succeed.

CI cannot see this: `validate_plugin_root_refs` only inspects strings containing
`${CLAUDE_PLUGIN_ROOT}`, and `validate_skills` only checks links inside SKILL.md. Nothing validates
links in agent bodies, even though `CLAUDE.md` states "Bundled material is referenced with
`${CLAUDE_PLUGIN_ROOT}`, never with a repo relative path".

Cheapest confirmation:

```bash
python3 - <<'PY'
import os,re,glob
for p in sorted(glob.glob("plugins/**/*.md",recursive=True)):
    for i,l in enumerate(open(p,errors="replace").read().splitlines(),1):
        for k in re.findall(r'\]\((\.\.[^)\s]*)\)',l):
            if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(p),k))):
                print(f"{p}:{i} -> {k}")
PY
```

**In flight, and regressing.** A concurrent agent is repairing exactly this and is adding a
`validate_relative_links` gate plus a `RETIRED` capability map to the validator. Its rewrite is
sound for the in plugin cases but is **producing malformed markdown for the cross plugin ones**.
The count of the mangled `` `the `<plugin>` plugin's` `` construct rose from **9 at HEAD to 16 in the
working tree**, and 3 of the new ones are broken links with an opening `[` and no closing `](...)`,
in `baseline-testing-supervisor.md:67`, `technical-analysis-supervisor.md:63` and
`functional-analysis-supervisor.md:60`. This needs to be caught before that work is committed.
Confirm: `grep -rn "plugin's \`references/[a-z/-]*\.md\`the \`" plugins`

### P2-3 HIGH: the user's own global config documents the retired install path and two dead agents

`~/.claude/CLAUDE.md:59` still tells the user to update the registry with
`cd ~/dev/claude-registry && git pull origin main && ./claude-catalog/scripts/setup-capabilities.sh --global`.
That script and directory no longer exist, so the documented update path fails outright. Line 58
still describes the repo as "source at `claude-catalog/`, published at `claude-marketplace/`".
The agent table also lists two capabilities that no longer exist anywhere under `plugins/`:
`developer-java-spring` at `:37` (renamed to `developer-java`) and `code-reviewer` at `:41` (removed).
All skills listed in that file still resolve.

This file is outside the repo and outside this audit's write scope, so it is reported, not changed.

Cheapest confirmation: `grep -n 'developer-java-spring\|code-reviewer\|setup-capabilities' ~/.claude/CLAUDE.md`

### P2-4 HIGH: undeclared cross plugin dependency on `deliberation`, with no graceful degradation note

`CLAUDE.md` requires: "When a cross plugin reference is unavoidable, the agent body says so and
describes what to do without it." No agent body does. Four replatforming supervisors and ten
reference files route contested decisions to the `deliberative-decision-engine` agent, which lives in
the separate `deliberation` plugin. `marketplace.json` declares no dependency between them and the
plugin schema has no dependency field in use here, so a user who installs only `replatforming` gets
supervisors that dispatch to an agent that does not exist, with no fallback described.

The three cross plugin links are also the ones that cannot be expressed relatively at all:
`plugins/replatforming/agents/baseline-testing/baseline-testing-supervisor.md:67`,
`.../functional-analysis/functional-analysis-supervisor.md:60`,
`.../technical-analysis/technical-analysis-supervisor.md:63` all point at
`../deliberation/integration-replatforming.md`, which resolves to a path inside `replatforming`
that does not exist; the real file is `plugins/deliberation/references/deliberation/integration-replatforming.md`.

The dispatch instruction itself is unconditional, for example
`plugins/replatforming/references/baseline-testing/supervisor-protocol.md:122`: "Route the contested
adjustment through `deliberative-decision-engine` BEFORE re dispatching the workers".

Cheapest confirmation: `grep -rn 'deliberative-decision-engine' plugins/replatforming | wc -l`

### P2-5 HIGH: 40 of 46 skill bodies are written as subagent personas that return content to a caller

A skill is injected into the reader's context; it does not run and does not return. 40 of 46 SKILL.md
bodies nonetheless open with a persona line such as "You are an expert software engineer specialising
in Angular" (`plugins/dev-standards/skills/angular-expert/SKILL.md:8`), and eleven lines go further
and describe an explicit return contract to a third party that does not exist at injection time:

- `plugins/analysis-architecture/skills/graphify-code-graph/SKILL.md:8` "When invoked, return the authoritative commands, workflow, and guardrails the calling agent needs... You do not execute commands yourself. You provide the playbook; the caller (which holds `Bash`) runs it."
- `plugins/docs-branding/skills/accenture-branding/SKILL.md:9-10` "When invoked, you return the relevant brand constants, layout rules, and code blocks that the calling agent..." and `:197` "Generate output files, provide the constants and rules for the calling agent to use"
- `plugins/dev-standards/skills/unicredit-design-system/SKILL.md:12`, `:51`, `:155` same pattern
- `plugins/replatforming/skills/test-data-seeding-standards/SKILL.md:21` "you return the rules and templates. The calling agent..."
- `plugins/dev-standards/skills/backend-orchestrator/SKILL.md:8` "You are the decision making brain of the backend. You do not write code directly. You decide which skills to activate..."

When the reader *is* the calling agent, "return X to the calling agent" instructs the model to emit
the reference material as its answer instead of applying it, and "you do not execute commands
yourself, the caller runs it" tells an agent that holds `Bash` that it must not use it. The
`backend-orchestrator` and `frontend-orchestrator` skills are worse: they are written as coordinators
that "decide which skills to activate", a role that requires the `Skill` tool that P2-1 shows no agent
has.

Verified present at committed `HEAD`, so this is not an artefact of the concurrent skill edits.
Cheapest confirmation: `find plugins -name SKILL.md | xargs grep -n 'the calling agent\|you return '`

### P2-6 MEDIUM: `wiki/` and `bmad/` were never migrated and describe the retired model as live

`wiki/` is 13 of 14 files stale (only `_Sidebar.md` is clean, because it has no prose). It documents
the two area `claude-catalog/` plus `claude-marketplace/` split, `catalog.json`, the `stable`/`beta`
tier system, `publish.sh`, and `setup-capabilities.sh` as the current install mechanism. Highest
signal instances: `wiki/Installation.md:34-36,61,77,83,86` (the entire install procedure, including
`--global` writing into `~/.claude/agents/`), `wiki/Architecture.md:20,50,57-63,115` (the repo layout
diagram), `wiki/Contributing.md:39` (`cp claude-catalog/agents/your-new-thing.md /path/to/test-project/.claude/agents/`),
`wiki/Quick-start.md:45,67,70`, `wiki/Reference.md:76,98-132`, `wiki/Governance.md:45-49,80-89`,
`wiki/FAQ.md:45,110-122`, `wiki/Capability-catalog.md:11,151,156`, `wiki/_Footer.md:3-5` (three dead
links), `wiki/Home.md:25-29,58-59`, `wiki/Changelog.md:11,50,92,99`, `wiki/Usage.md:145,155,159`,
`wiki/What-is-Claude-Registry.md:21,42,64-95`.

`bmad/` is 4 of 4 stale: `bmad/workflows.json:2` and `:113` reference `claude-catalog/`;
`bmad/design/mapping.md` has 16 stale lines; `bmad/design/workflow-dag-draft.json:569,641` name dead
agents. `bmad/workflows.json` is cited by `CLAUDE.md` as the authoritative phase DAG and lists two
names that resolve to nothing under `plugins/`: `developer-java-spring` at `:92` and `code-reviewer`
at `:97`.

Also stale outside those two trees: `docs/quick-start.md` (whole file, notably `:71`
`cp path/to/claude-marketplace/stable/architecture/software-architect.md .claude/agents/`),
`docs/pitch-claude-registry.md`, `docs/supervisor-extraction-template.md`,
`docs/language-agnostic-design.md`, `templates/new-use-case/README.md` (18 stale lines),
`templates/new-use-case/catalog-entry-template.json` (the entire file models the retired
`catalog.json` entry schema and has no counterpart in the plugin model),
`templates/new-use-case/supervisor-template.md:37`, and `guida-operativa.tex` (42 hits across a
1,500 line Italian operations guide, including whole sections at `:1412` and `:1424` documenting the
retired scripts) together with its built artefact `guida-operativa.pdf`.

Correctly scoped as historical and **not** to be "fixed": `docs/registry/CHANGELOG.md`,
`docs/registry/how-to-write-a-capability.md:343,363-366` and `docs/registry/release-process.md:88`,
all of which sit inside dated "Old patterns, superseded 2026-08" blocks.

Cheapest confirmation: `grep -rln 'claude-catalog\|claude-marketplace\|setup-capabilities' wiki bmad docs templates settings scripts`

### P2-7 MEDIUM: a dead path is baked into a runtime prompt in `scripts/present.sh`

`scripts/present.sh:125` emits, as part of the prompt it hands to Claude:
`Follow the Accenture brand standard (colors, fonts, layouts) as defined in claude-catalog/policies/accenture-branding.md.`
`policies/` now contains only `python-conventions.md`; the branding content lives at
`plugins/docs-branding/skills/accenture-branding/SKILL.md`. Every deck this script produces is
generated against an instruction to read a file that does not exist, so the branding is unenforced
at exactly the point the script exists to enforce it.

Cheapest confirmation: `sed -n '125p' scripts/present.sh && ls policies/`

### P2-8 MEDIUM: the shared settings example wires hooks to dead paths

`settings/shared-settings-example.json:74` and `:87` point at
`claude-catalog/hooks/scripts/pre-tool-safety.sh` and `claude-catalog/hooks/scripts/post-session-log.sh`.
Both scripts exist, at `hooks/scripts/`, but the `claude-catalog/` prefix is dead. Anyone copying this
example gets two hooks that silently never fire, one of which is a safety hook.

Cheapest confirmation: `grep -n 'claude-catalog' settings/shared-settings-example.json && ls hooks/scripts/`

### P2-9 MEDIUM: `bmad/scripts/backfill-dag.py` is non functional

`bmad/scripts/backfill-dag.py:12` hard codes `CATALOG = ROOT / "claude-marketplace" / "catalog.json"`.
That directory does not exist, so the script cannot run at all.

Cheapest confirmation: `sed -n '12p' bmad/scripts/backfill-dag.py && ls claude-marketplace`

### P2-10 LOW: four orphaned reference files, roughly 25 KB, shipped to every user

Each of these was superseded by a per agent subdirectory during the restructure, but the flat file
was left behind and nothing links to it. The corresponding agent points at the sibling directory
instead, for example `plugins/replatforming/agents/refactoring-tobe/backend-scaffolder.md:44` reads
`${CLAUDE_PLUGIN_ROOT}/references/refactoring-tobe/backend-scaffolder/`, one level below the orphan.

- `plugins/replatforming/references/refactoring-tobe/backend-scaffolder-method.md` (4,397 bytes)
- `plugins/replatforming/references/refactoring-tobe/frontend-scaffolder-method.md` (5,581 bytes)
- `plugins/replatforming/references/refactoring-tobe/phase4-challenger-checks.md` (8,053 bytes)
- `plugins/replatforming/references/tobe-testing/tobe-testing-challenger-checks.md` (6,638 bytes)

Cheapest confirmation: `grep -rn 'backend-scaffolder-method\|frontend-scaffolder-method\|phase4-challenger-checks\|tobe-testing-challenger-checks' plugins | wc -l` returns `0`.

### P2-11 LOW: per capability `beta` and `roadmap` flags survive, contradicting `CLAUDE.md`

`CLAUDE.md` states "There is no `claude-catalog` and no `claude-marketplace`, and no per capability
beta or stable flag. Versioning is semver on the plugin." Sixteen lines still carry the retired flag,
in `plugins/analysis-architecture/agents/technical-analyst.md:120`,
`plugins/docs-branding/agents/documentation/documentation-writer.md:241`,
`plugins/dev-standards/agents/debugger.md:95`,
`plugins/dev-standards/agents/developers/developer-python.md:101`, and pairs at `:39`/`:224`,
`:37`/`:205`, `:38`/`:271`, `:38`/`:276`, `:45`/`:231`, `:38`/`:230` in `developer-ruby`,
`developer-rust`, `developer-csharp`, `developer-php`, `developer-kotlin` and `developer-go`
respectively. These are user visible: they tell the user the capability is unfinished.

Cheapest confirmation: `grep -rn 'Status.*beta\|status: roadmap' plugins`

### P2-12 LOW: root `.mcp.json` duplicates the plugin MCP configs and is unpinned

The two plugin level MCP configs are correctly pinned: `plugins/dev-standards/.mcp.json` pins
`@playwright/mcp@0.0.79`, `plugins/docs-branding/.mcp.json` pins `uml-mcp` to commit
`78137bd66bfeb9754d0d5de0be1016f4dc053cc6`. The root `.mcp.json` declares the same two servers with
`@playwright/mcp@latest` and no commit pin. It is a leftover of the pre plugin model and now applies
only to work done inside this repo, where it silently overrides the pinning discipline the plugins
establish.

Cheapest confirmation: `cat .mcp.json plugins/dev-standards/.mcp.json`

### P2-13 LOW: duplication against the official plugins this user has enabled

`ls ~/.claude/plugins/cache/claude-plugins-official/` returns 14 plugins: `agent-sdk-dev`,
`chrome-devtools-mcp`, `claude-code-setup`, `claude-md-management`, `code-review`, `code-simplifier`,
`commit-commands`, `feature-dev`, `hookify`, `plugin-dev`, `pr-review-toolkit`, `session-report`,
`skill-creator`, `swift-lsp`. Genuine overlaps:

| Registry capability | Overlapping official capability | Note |
|---|---|---|
| `dev-standards/skills/browser-automation` | `chrome-devtools-mcp` (6 skills) | Both drive a real browser; the registry routes through `@playwright/mcp`, the official plugin through Chrome DevTools MCP. Two MCP servers for one job. |
| `analysis-architecture/agents/registry-auditor` | `plugin-dev::plugin-validator`, `plugin-dev::skill-reviewer`, `skill-creator` | The registry agent explicitly shells out to read those official skills (`registry-auditor.md:74-76`), so it is a wrapper around capabilities the user already has natively. |
| `dev-standards/skills/refactoring-expert` | `code-simplifier` agent, `pr-review-toolkit::code-simplifier` | Overlapping remit. |
| `caveman/skills/caveman-commit` | `commit-commands::commit` | Overlapping remit. |
| (none, `code-reviewer` was removed) | `pr-review-toolkit::code-reviewer`, `feature-dev::code-reviewer`, `code-review` | Three official code reviewers now exist while `~/.claude/CLAUDE.md:41` and `bmad/workflows.json:97` still point at a registry `code-reviewer` that does not. Reinforces P2-3. |

The official plugins also contribute 16 agents and roughly 2,275 description tokens to the same
budget measured in 1.2. Cheapest confirmation:
`find ~/.claude/plugins/cache/claude-plugins-official -path '*/agents/*.md' | sed -E 's|.*official/([^/]+)/[^/]+/agents/(.*)\.md|\1 :: \2|' | sort -u`

## Part 3: gaps against current guidance that nobody has noticed

### P3-1 CRITICAL: the description budget gate is measuring the wrong thing and the real margin is 1.7 percent

`.github/scripts/validate_registry.py:24` estimates tokens as `words * 1.35`. Measured against
`tiktoken`, the registry's 86 descriptions are 55,376 characters and **11,798 tokens** (`cl100k_base`)
or **11,890** (`o200k_base`); the validator reports **10,166**. That is a 16.05 percent undercount,
and it implies 5.45 characters per token where the real figure is 4.69. The gate therefore shows
18 percent headroom under its own 12,000 soft limit when the true headroom is 202 tokens, or
1.7 percent. Claude's tokenizer is not `cl100k`, and on this kind of text, dense with hyphenated
capability names and technical nouns, it typically produces equal or higher counts, so 11,798 should
be read as a floor rather than a point estimate.

Two structural problems compound this. First, the documented ceiling is per user, not per marketplace:
the sub agents documentation says the warning fires "when the combined descriptions of your subagents,
except the built in ones, exceed 15,000 tokens". Counting the 16 official plugin agents this user
already has enabled brings the real total to **14,073 of 15,000**, at 94 percent of the ceiling,
before any project level `.claude/agents/` are added. Second, `replatforming` alone contributes 7,672
tokens across 58 agents, so it is that single plugin that consumes the budget.

Note also that the task framing for this audit cited a 12,000 token platform limit; the authoritative
figure in the fetched documentation is **15,000**, with 12,000 being this repo's own self imposed soft
gate as documented at `.github/scripts/validate_registry.py:22-23`.

Cheapest confirmation:

```bash
python3 .github/scripts/validate_registry.py | grep 'all enabled'
pip install tiktoken && python3 - <<'PY'
import re,glob,tiktoken
e=tiktoken.get_encoding("cl100k_base"); t=0
for p in glob.glob("plugins/*/agents/**/*.md",recursive=True):
    s=open(p).read(); fm=s[3:s.find("\n---",3)]
    m=re.search(r'^description:\s*(.*)$',fm,re.M)
    if m: t+=len(e.encode(m.group(1).strip().strip('"')))
print(t)
PY
```

### P3-2 HIGH: CI does not enforce the one convention `CLAUDE.md` calls out as silently failing

`CLAUDE.md` states that bundled material must use `${CLAUDE_PLUGIN_ROOT}` because "a repo relative
path resolves against the user's project and silently returns nothing". That is exactly the failure
mode of P2-2, and the validator has no check for it: `validate_plugin_root_refs` only inspects
strings that already contain the variable, so a link that omits it is invisible by construction.
The concurrent work is adding a `validate_relative_links` gate that closes this, which is the right
fix; it should land together with the P2-2 correction described above.

Cheapest confirmation: `grep -n 'def validate_' .github/scripts/validate_registry.py`

### P3-3 MEDIUM: `license: "UNLICENSED"` is not a valid SPDX identifier

All 6 `plugin.json` files declare `"license": "UNLICENSED"`. The plugin schema documents this field as
"SPDX identifier like MIT, Apache-2.0". `UNLICENSED` is an npm convention, not SPDX; the SPDX
equivalents are `NONE`, `NOASSERTION`, or a `LicenseRef-` prefixed custom identifier. Cosmetic today,
but it will fail any future strict manifest validation.

Cheapest confirmation: `grep -h '"license"' plugins/*/.claude-plugin/plugin.json | sort -u`

### P3-4 MEDIUM: the validator's reserved marketplace name list is missing 11 documented names

`.github/scripts/validate_registry.py:17-18` lists 5 reserved names. The plugin marketplaces
documentation reserves at least 16, including `claude-plugins-official`, `claude-plugins-community`,
`claude-community`, `agent-skills`, `anthropic-agent-skills`, `knowledge-work-plugins`,
`life-sciences`, `claude-for-legal`, `claude-for-financial-services`, `financial-services-plugins`
and `healthcare`. Not a live problem, since `claude-registry` is not reserved, but the gate would pass
a rename that the platform then rejects at install time.

Cheapest confirmation: `sed -n '17,18p' .github/scripts/validate_registry.py`

### P3-5 MEDIUM: two latent gaps in the validator's own parsing

Both are dormant today and will bite on the next structural change.

- `.github/scripts/validate_registry.py:141` globs skills as `plugins/*/skills/*/SKILL.md`, non recursive, while line 105 globs agents recursively with `**`. A skill nested one level deeper is silently unvalidated. Agents are already nested this way, so the asymmetry is a question of when, not if.
- `.github/scripts/validate_registry.py:48-50`: `field()` matches `^<name>:` under `re.M | re.S` and terminates at the next line starting `[a-zA-Z_-]+:`. A description whose body contains a line beginning with a word plus colon, for example `Examples:`, will be silently truncated at that point, and the budget in 1.2 will under report further. `validate_skills` also bans only `model`, `tools` and `color` rather than rejecting any key outside `name` and `description`, so the "exactly two fields" rule verified in 1.3b is convention, not an enforced gate.

Cheapest confirmation: `sed -n '48,50p;105p;141p;163,165p' .github/scripts/validate_registry.py`

### P3-6 MEDIUM: the two authoritative sources conflict on `color`, and a future auditor will misflag this

Worth recording so the next audit does not raise a false positive. `code.claude.com/docs/en/sub-agents`
lists the allowed colours as `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`,
which excludes `magenta`. The bundled official
`plugin-dev/*/skills/agent-development/SKILL.md:111` lists `blue`, `cyan`, `green`, `yellow`,
`magenta`, `red`, which excludes `purple`, `orange` and `pink`. Fourteen registry agents use
`color: magenta`.

Empirically the installed CLI (v2.1.251) favours the bundled list: the strings `"magenta"` and
`"cyan"` appear 8 and 6 times in the bundle, while `"purple"` and `"pink"` appear zero times. The
registry's colour set is exactly `blue`, `cyan`, `green`, `yellow`, `magenta`, `red`, an exact match
for the bundled guidance, so **this is not a defect** and should not be "fixed" toward the web doc's
list without testing. Flagged only because the conflict is real and undocumented in the repo.

Cheapest confirmation:

```bash
grep -n 'Options:.*blue' ~/.claude/plugins/cache/claude-plugins-official/plugin-dev/*/skills/agent-development/SKILL.md
for c in magenta purple pink cyan; do echo -n "$c: "; grep -ao "\"$c\"" /opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe | wc -l; done
```

### P3-7 LOW: could not verify the manifests with the official CLI

`claude plugin validate .` exits without validating, printing `Your organization requires remote
managed settings to load, but they could not be loaded. Run 'claude auth login' to re authenticate...`.
Finding 1.4 therefore rests on the repo validator plus a manual field by field comparison against the
fetched schema, not on the official tool. `CLAUDE.md` lists this command as a required step in
"Adding a new capability" step 5, so the documented authoring workflow is currently unrunnable on this
machine.

Cheapest confirmation: `claude plugin validate .`

### P3-8 LOW: skill description and naming conventions are compliant, recorded for completeness

Checked and found clean, so no action: 42 of 46 skill descriptions use the recommended third person
`This skill should be used when...` opening and the other 4 are also third person; zero use first or
second person, which the best practices guide flags as a discovery problem. All 86 agents carry the
`## When to invoke` section the validator warns on. Skill names use noun phrase form rather than the
recommended gerund, which the guide explicitly lists as an acceptable alternative.

Cheapest confirmation: `for f in $(find plugins -path '*/agents/*.md'); do grep -q '## When to invoke' "$f" || echo "$f"; done | wc -l`

## Recommended order of work

1. P2-1, add `Skill` to the `tools` allowlist of the 7 agents that instruct skill loading, and decide deliberately for the other 79 whether the omission is intended.
2. P2-2, land the in flight link repair, but fix the malformed cross plugin substitution first, and add the `validate_relative_links` gate from P3-2 so it cannot regress.
3. P3-1, replace `WORDS_TO_TOKENS` with a real tokenizer and re baseline the gate against the 15,000 per user ceiling, counting other enabled marketplaces.
4. P2-3, correct `~/.claude/CLAUDE.md` lines 37, 41, 58 and 59.
5. P2-4, add the graceful degradation note `CLAUDE.md` already mandates to the 4 replatforming supervisors.
6. P2-5, rewrite the 11 return contract lines; the 40 persona openings are lower priority and can follow.
7. Everything else in the order listed.
