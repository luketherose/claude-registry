# Twin registry on Gemini CLI: implementation plan

**Status**: Proposed. Nothing is built until the open decisions in section 11 are settled.
**Date**: 2026-08-31
**Scope**: a second capability registry running this repository's material on Google's Gemini CLI,
kept in step by a procedure and a gate rather than by goodwill.

Every Gemini CLI fact below is checked against `google-gemini/gemini-cli` at `v0.57.0`, and where the docs are silent,
against the 0.57.0 binary installed here. Anything neither settles is marked UNVERIFIED with the command that would.

## Contents

[1 Gate zero](#1-gate-zero-the-cli-on-this-machine) · [2 Scope](#2-what-is-actually-in-scope) · [3 Topology](#3-repository-topology) ·
[4 Source of truth, naming, ledger](#4-source-of-truth-naming-and-the-ledger) · [5 Port buckets](#5-port-buckets) ·
[6 Drift gate](#6-the-drift-gate) · [7 Evals](#7-evals-one-corpus-two-harnesses) · [8 Phasing](#8-phasing) ·
[9 Non-functional impact](#9-non-functional-impact) · [10 Risks](#10-risks) · [11 Open decisions](#11-open-decisions-for-the-user)

## 1. Gate zero: the CLI on this machine

The authoring machine is now on `0.57.0`, upgraded during this pass and confirmed with `gemini --version`. It was
`0.1.18`, roughly a year old, and that gap is why the gate stays wave 0 for every other machine: skills, sub-agents,
hooks, the Policy Engine and `gemini extensions install` all postdate that build, and the failure is silent, because
`gemini extensions --help` prints the top-level help instead of erroring. Nothing here can be tested, let alone
shipped, on a machine that has not had the upgrade. It is a hard prerequisite, not a preparatory task.

```bash
gemini --version && npm install -g @google/gemini-cli@latest
gemini extensions list && gemini skills list --all
```

## 2. What is actually in scope

Six plugins, 86 agents, 46 skills. A seventh, `gemini-interop`, holds the fact base itself (1 agent, 4 skills) and
mirrors as a matter of course, because a Gemini-side author needs `gemini-extension-authoring` more than a Claude-side
one does. It is **in scope for the waves**, not outside them: its 4 skills ride wave 2 and its agent `gemini-porter`
rides wave 4, so the totals the waves count against are **87 agents and 50 skills**.

| Plugin | Agents | Skills | Dispatchers | MCP |
|---|---:|---:|---:|---|
| `replatforming` | 58 | 4 | 7 | none |
| `dev-standards` | 12 | 29 | 0 | `browser` |
| `deliberation` | 7 | 0 | 1 | none |
| `analysis-architecture` | 5 | 3 | 1 | none |
| `docs-branding` | 4 | 7 | 0 | `uml` |
| `caveman` | 0 | 3 | 0 | none |

**Zero commands.** `find plugins -path '*/commands/*' -name '*.md' | wc -l` returns 0. The markdown-to-TOML conversion
problem does not exist here, and the "drive the phases from a custom command" fix for a lost supervisor is green field
on both sides, not a translation.

**Nine dispatchers.** Nine of 87 agents hold the `Agent` tool: `orchestrator`, `deliberative-decision-engine` and the
seven `replatforming` supervisors. They are also, exactly, the nine carrying `experimental.cacheTtl`
(`docs/registry/version-requirements.md`). The set that fans out and the set that needs a warm cache are the same set,
and on Gemini CLI that set has no shape. Alongside them sit **137 eval directories**, holding 137 `triggers.json` and
31 `evals.json`.

## 3. Repository topology

**Recommendation: one source repository, this one, carrying a committed and reviewed twin tree at
`gemini/extensions/<name>/`. Skills distribute from the monorepo by URL. Extensions distribute by local path after a
clone. A per-extension repository is built only for an extension that is both publishable and actually needs the
gallery.**

The asymmetry that decides it is easy to miss: `gemini skills install <repo-url> --path skills/my-skill` takes a
subdirectory selector, while `gemini extensions install <source>` has no equivalent (confirmed against `gemini
extensions install --help` on 0.57.0). The 50 skills are the bulk of the value and are already monorepo-installable by
URL. Only the extension wrapper, which carries agents, hooks and MCP servers, needs the one-repository-one-unit shape,
and that is the layer cheap enough to install by path. Distribution reinforces it: this repository publishes
internally and holds client material (`unicredit-design-system` in `dev-standards`), so the gallery is unavailable for
the plugin most people would want, and paying six repositories for a listing we cannot collect is a bad trade.

**Trade-off accepted.** Gains: one repository, one CI run, one review, one ledger, and a freshness check that is a
local `git log` rather than a cross-repository API call with a token; client material never leaves a repository that
already governs it. Costs: no gallery listing, so discovery is a README and a link; anything richer than a skill needs
`git clone` then `gemini extensions install <path>`, with `git pull` plus `gemini extensions update` afterwards
because `install` copies rather than symlinks; and a Gemini-only user clones 87 agents, most of which they cannot run.
Risk: a committed tree is editable in place, exactly what the single-source rule forbids, and section 6 is what makes
that rule real.

**Alternatives considered.** *One repository per extension*: pays six repositories, six CI configs and a
cross-repository drift check for a gallery listing `dev-standards` cannot take; revisit only if Q2 answers "public".
*Build the twin at install time*: removes direct edits, but `capability-parity-sync` is explicit that generating prose
mirrors automatically is wrong, and an unreviewed build cannot be signed. *No generated tree*: the substitutions need
somewhere reviewable. One escape hatch stays in reserve either way: `scripts/publish-extension.sh <name>`, splitting a
single `gemini/extensions/<name>` directory onto its own repository root, so a publishable extension can be promoted
later without reorganising the source.

## 4. Source of truth, naming and the ledger

**The rule.** The Claude side owns every host-neutral capability. The Gemini side owns only what exists because of a
Gemini constraint.

| Material | Source |
|---|---|
| the 50 skills, the 46 plus the 4 in `gemini-interop` | `claude` |
| the 78 non-dispatching agents, `gemini-porter` included | `claude` |
| the neutral eval corpus (section 7) | `claude` |
| `gemini-extension.json`, per-extension `GEMINI.md` | `gemini` |
| `hooks/hooks.json`, `policies/*.toml` | `gemini` |
| the replacement for a dispatching supervisor | `gemini`, a new capability rather than a mirror |

**Propagation, both directions.** A PR touching `plugins/**` must, in the same PR, either carry the mirror under
`gemini/extensions/**` or add a `diverged` or `pending` ledger row. A PR touching `gemini/extensions/**` for a row
whose `source` is `claude` fails unless the same PR flips `source` and says why. That second rule stops a hotfix on
the derived side from silently becoming the new source of truth and being reverted at the next sync.

**Naming.** `validate_skills()` in `.github/scripts/validate_registry.py` rejects a skill name containing `claude` or
`anthropic`; cite the function, not a line number, which moves whenever anything is inserted above it. In a twin this
stops being cosmetic: the ledger requires `capability` to be identical on both sides, so a name carrying a host name
cannot be mirrored without either renaming it or breaking the identity the presence check depends on. Apply it
symmetrically, in either direction. The rename of the parity skill to `cross-host-parity` is the worked example, and
it happened because the gate caught it, not because anyone remembered.

**The ledger.** `parity/ledger.json`, one JSON array, one object per capability, the seven fields from
`capability-parity-sync`. JSON rather than YAML or CSV because CI is already Python and already gates JSON here.

```json
{ "capability": "spring-expert", "kind": "skill", "source": "claude",
  "status": "mirrored", "reason": "",
  "source_sha": "9f2c1ab7e4d0c3b1a8f6e2d5c9b4a7f0e3d6c1b8", "recheck": "" }
```

On a later split, this file is copied verbatim and a hash equality check joins both gates.

## 5. Port buckets

| Plugin | Bucket | Cost |
|---|---|---|
| `caveman` | 3 skills, portable as is | trivial |
| `gemini-interop` | 4 skills and 1 agent, portable as is | trivial |
| `docs-branding` | 7 skills and 4 agents with adaptation; `uml` MCP moves into the manifest; 2 agents lose `skills:` preload | low |
| `analysis-architecture` | 3 skills and 4 agents port; `orchestrator` restructures | low |
| `dev-standards` | 29 skills and 12 agents with adaptation; `browser` MCP moves into the manifest; 1 skill is distribution-restricted | low per file, high volume |
| `deliberation` | 6 personas port as plain sub-agents; the engine restructures | medium, concentrated in one file |
| `replatforming` | 4 skills and 51 workers port; 7 supervisors restructure; 6 pipelines lose their driver | high |

**The nine dispatchers are the whole problem.** A supervisor ported as a Gemini sub-agent loads, reads correctly,
runs, and quietly does the work itself in one context instead of fanning out. Nothing errors. This is trap 5 in the
fact base and the most expensive fact in this plan. The fix per `cross-host-parity` is one of two: promote the
supervisor's protocol into a skill the main agent loads and executes, or drive the phases from a custom command. Both
are restructures raised as their own work, never folded into a sync. There is no `gemini agents` subcommand, so
sub-agents stay file-based and nothing in the CLI will do this for us.

**What ports with mechanical adaptation.** All 50 skills, because Agent Skills is the same open standard on both
hosts. Two substitutions each: a plugin-root path becomes a plain relative path in `SKILL.md`, and Claude Code tool
names in prose become Gemini names. Two skills carry an MCP dependency, `browser-automation` on `@playwright/mcp` at
`0.0.79` and `uml-diagram-generator` on the pinned uml server; neither can ship as a bare skill, because MCP wiring
lives in `gemini-extension.json`, so both need their extension wrapper.

**What is rewritten rather than substituted.** Any agent body instructing "read each file in turn" fights the host,
because `read_many_files` is the batching read and Google's own evals assert on it. Prose about Claude Code's approval
flow becomes prose about consent prompts.

**What loses a field.** `effort: high` on 24 agents, `background: true` on `registry-auditor` and
`experimental.cacheTtl` on the nine dispatchers change cost and latency, not behaviour, and the ported file records
the drop. `skills:` preload on `api-designer`, `presentation-creator`, `document-creator` and `test-data-seeder`
changes behaviour: with no preload each produces a consent prompt on first activation, so either the extension's
`GEMINI.md` carries the content or the prompt is the cost of the port.

**What the CLI now ports for us.** Three 0.57.0 subcommands cut work this plan had costed as manual, all three run
here. `gemini extensions new <path> <template>` ships seven templates including `skills`, `hooks` and `policies`, so
wave 1's skeleton is a scaffold rather than a hand-written manifest. `gemini extensions validate <path>` is the
counterpart of `claude plugin validate`; section 6 has it. `gemini hooks migrate --from-claude` reads
`.claude/settings.json` or `settings.local.json` in the working directory, maps event names (`PreToolUse` to
`BeforeTool`, `Stop` to `AfterAgent`) and seven tool names inside matchers, rewrites `$CLAUDE_PROJECT_DIR` to
`$GEMINI_PROJECT_DIR`, and writes into workspace `.gemini/settings.json`. Two limits, both read off the installed
bundle, stop it being free: it copies `timeout` verbatim while Claude counts seconds and Gemini milliseconds, so it
reproduces the factor-of-a-thousand trap instead of fixing it, and it targets workspace settings rather than an
extension's `hooks/hooks.json`, so its output is a seed a human transplants. Hook work re-costs from manual
translation to seed-plus-review, on future work only: `hooks` is empty in both `.claude` settings files here.

**What tightens, and what stays behind.** An extension can tighten and never loosen: `allow` decisions and `yolo`
configuration in extension policy load, are ignored, and never warn, so deny rules port and allow rules become a note
in `GEMINI.md` naming what the user will be asked to approve. `unicredit-design-system` is client material: under the
recommended topology it mirrors into the monorepo and nowhere else, recorded as `diverged` with a reason and a recheck
date so it stays visible rather than looking like an oversight. Extension policy loads at its own tier, above defaults
and below user and admin, so it is untouched by the Workspace tier being non-functional today
(`docs/reference/policy-engine.md`, issue #18186); nothing here should fall back to `.gemini/policies`, which is
inert. The mechanical work in every bucket above belongs to `gemini-porter` in `gemini-interop`; waves 5 and 6 do
not.

## 6. The drift gate

`.github/scripts/check_parity_drift.py`, a step in the `validate-catalog` job of `.github/workflows/validate-pr.yml`.
It fails the build, reports by capability name, and never says only "the registries differ".

1. **Presence.** For every `status: mirrored` row, both the source path and the mirror path exist. Catches a
   capability added on one side and forgotten.
2. **Freshness.** For every mirrored row, `git log -1 --format=%H -- <source path>` equals `source_sha`. Catches a
   source edit that never propagated. In one repository this is a local command with no network and no token, which is
   the operational reason section 3 chose one repository.
3. **Justification.** Every `diverged` row has a non-empty `reason` and a `recheck` date not in the past. Every
   capability in either tree has a row, and every row names a capability that exists.

Three further checks belong to the committed-twin topology and are not in `capability-parity-sync`. **No orphan
edits**: a PR changing a file under `gemini/extensions/**` whose row says `source: claude`, without changing the
corresponding source file, fails; without it the committed tree invites exactly the edit the single-source rule
forbids. **No client material in a publishable unit**: a denylist of capability names barred from any extension
directory the publish script would touch, landing in wave 1 rather than wave 7, because adding it late is adding it
after the mistake. **Required Gemini fields**: every mirrored agent declares a non-empty `tools` list in its
frontmatter, since an omitted `tools` inherits every tool rather than none (`docs/core/subagents.md`); this belongs to
the script rather than a `grep`, which cannot tell frontmatter from a body line.

The manifest layer is not ours to gate. `gemini extensions validate <path>` exits 1 on a missing, malformed or
incomplete `gemini-extension.json` and 0 otherwise, so CI runs it over every `gemini/extensions/*` and the parity
script never re-implements it. Verified here that it does *not* catch a `name` disagreeing with its directory, an
agent with no `tools`, or a hook `timeout` in the wrong unit, which is why those three stay above.

Flags, because the wave exits depend on them: `--kind`, `--plugin`, `--side`, `--print-mirrored` and `--print-pending`
(one capability name per line, for set comparison), and `--expect-total N`, which exits non-zero unless mirrored plus
diverged plus pending equals N, so that no exit criterion can be met by an empty ledger. While the twin lives here
there is one gate; on a split, the twin runs the same script with `--side gemini` and both gates additionally assert
the ledger hashes are equal.

## 7. Evals: one corpus, two harnesses

The harnesses do not converge and should not be forced to. Claude Code runs `claude plugin eval` with trigger cases
and grader prompts over a transcript. Gemini runs the EDK, `evals/*.eval.ts` under vitest, asserting on tool calls
with `rig.waitForToolCall`. Host-independent is the corpus: queries, should-trigger flags and expected behaviours are
facts about the capability, not the host.

**Neutral corpus**, one file per capability at `evals/corpus/<capability>.json`.

```json
{ "capability": "spring-expert", "kind": "skill",
  "triggers": [ { "query": "how do I wire @ConfigurationProperties", "should_trigger": true,
      "description": "asks about binding external configuration onto a typed object" } ],
  "behaviours": [ { "query": "review this Spring Boot config", "files": ["app.yml"],
      "expected_behavior": "identifies the profile that overrides the datasource",
      "expected_tools": ["read_many_files"] } ] }
```

**Two generators, one script, neither output hand-edited.** `scripts/gen-evals.py --side claude` writes
`plugins/<plugin>/evals/<name>/triggers.json` and `evals.json` in exactly the key set `validate_evals()` already
gates. `--side gemini` writes `gemini/extensions/<name>/evals/<capability>.eval.ts`. CI runs `--check`, regenerating
into a temporary tree and failing on any diff, because generated files that can be edited are files that will be
edited.

**Two asymmetries to record rather than paper over.** Gemini has no trigger-eval equivalent, so a `should_trigger:
true` case becomes a behavioural case asserting an `activate_skill` call naming the skill, and `should_trigger: false`
becomes the same assertion negated, which is weaker; the corpus records that. Separately, `expected_tools` is new on
the Claude side and worth adding regardless: the fact base recommends asserting on tool calls rather than prose, and
it is the only field both harnesses check identically.

UNVERIFIED: whether the EDK is consumable outside the `google-gemini/gemini-cli` repository as an installable package
rather than as in-tree tooling. The fact base names the harness and `npm run eval:validate` but not its distribution.
Settle before wave 3 with `npm view @google/gemini-cli dist-tags` plus a search of the `v0.57.0` tree for a published
eval package. If it is in-tree only, wave 3 falls back to `gemini -p ... -e <extension> -o stream-json` with `jq`
assertions on `tool_name`, the same shape waves 0 and 5 use. The corpus is unaffected either way.

## 8. Phasing

Eight waves, one exit criterion each, every one a command that exits non-zero when the wave is incomplete. Three rules
make that real rather than decorative. A check whose subject can be empty carries a count assertion first, because
"prints nothing" is also what an empty tree prints. A check against `gemini skills list` or `gemini extensions list`
asserts a **subset**, never a total, because both listings carry built-ins, headers, blank lines and every other
installed unit. A count is compared with `test "$(... | wc -l)" -eq N`, never `wc -l | grep -qx N`, because BSD `wc`
pads its output and the `grep` form then silently never matches. Commands assume `bash`.

**Wave 0. Gate zero, and one skill that actually loads.** Upgrade the CLI (section 1), then prove one real skill
activates. `rest-api-standards` is the candidate: pure reference material, one reference link, no MCP dependency,
names no host. An exit not met here stops the plan, because everything after it assumes skills load.
- **Exit**: three commands, all exiting 0. Version floor, `printf '0.57.0\n%s\n' "$(gemini --version)" | sort -V |
  head -1 | grep -qx 0.57.0`, which also fails on a downgrade where `grep 0.57` would not. Presence,
  `gemini skills list --all | grep -q '^rest-api-standards \['`, anchored at column 0 where only the name line
  starts. Activation, `gemini -p "review this API contract for versioning" -o stream-json | jq -e
  'select(.type=="tool_use" and .tool_name=="activate_skill") | .parameters | tostring |
  test("rest-api-standards")'`, which fails both when nothing activates and when the wrong skill does.
  `docs/cli/headless.md` documents the event types; `tool_name` and `parameters` come from the installed bundle.

**Wave 1. Twin skeleton, ledger, drift gate.** Three pilot skills, one extension wrapper (`analysis-architecture`, the
smallest carrying both skills and agents), `parity/ledger.json`, and `check_parity_drift.py` wired into CI with all
six checks including the client-material denylist.
- **Exit**: `gemini extensions validate gemini/extensions/analysis-architecture` exits 0; `test "$(python3
  .github/scripts/check_parity_drift.py --print-mirrored | wc -l)" -eq 3`, an equality, because "reports no problems"
  is also what an empty ledger reports; and after `gemini extensions link
  "$PWD/gemini/extensions/analysis-architecture"`, `gemini extensions list | grep -q analysis-architecture`.

**Wave 2. Skills bulk mirror.** All 50 skills, the 46 in the six plugins plus the 4 in `gemini-interop`, minus
recorded divergences. The biggest lever in the plan and the cheapest wave per unit of value delivered.
- **Exit**: `check_parity_drift.py --kind skill --expect-total 50` exits 0 with no `pending` row, which fails on a
  survivor and on a ledger that never grew to 50. Then `check_parity_drift.py --kind skill --print-mirrored | sort >
  /tmp/w2-want`, `gemini skills list --all | awk '/^[a-z0-9-]+ \[/ {print $1}' | sort > /tmp/w2-have`, and `test
  "$(comm -23 /tmp/w2-want /tmp/w2-have | wc -l)" -eq 0`. `comm -23` asks the answerable question, whether every
  mirrored skill is present, and ignores what else the host lists.

**Wave 3. Eval corpus and dual generation.** Migrate 137 eval directories into the neutral corpus, then generate both
sides from it.
- **Exit**: `test "$(ls evals/corpus/*.json | wc -l)" -eq 137` first, because `--check` regenerates and diffs, and an
  empty corpus generates nothing and diffs clean. Then `python3 scripts/gen-evals.py --check` exits 0, and `python3
  .github/scripts/validate_registry.py` still reports `Errors: 0 | Warnings: 0`.

**Wave 4. Non-dispatching agents.** 78 of 87: the 77 in the six plugins plus `gemini-porter`, leaving the 9
dispatchers to waves 5 and 6. Flatten `agents/<domain>/<name>.md` into `agents/<name>.md` keeping the domain in the
name, and set an explicit `tools` list on every one, because an omitted `tools` inherits everything rather than
nothing (`docs/core/subagents.md`).
- **Exit**: `check_parity_drift.py --kind agent --expect-total 87` reports 78 mirrored and 9 pending and exits 0,
  which also enforces the `tools` field as check 6 of section 6; then `test "$(find gemini/extensions -path
  '*/agents/*.md' | wc -l)" -eq 78`, which is what gives the field check a subject: with an empty `agents/` a `grep -L
  '^tools:'` over the glob matches no file, complains on stderr, exits 2 and prints nothing on stdout, so it passes.

**Wave 5. Dispatch restructure, proven on the two cheap cases.** `orchestrator` (4 siblings) and
`deliberative-decision-engine` (6 personas). The proving ground, because they are small and the deliberation fan-out
is a fixed persona list, the easiest shape to express as a command driving the main agent. The exit is a transcript
assertion rather than a file count, because the failure is silent: one persona call means the restructure failed and
the agent did the work itself.
- **Exit**: `gemini -p "deliberate: monolith or modular services" -e deliberation -o stream-json > /tmp/w5.jsonl`,
  then `test "$(jq -r 'select(.type=="tool_use") | .tool_name' /tmp/w5.jsonl | grep '^debate-' | sort -u | wc -l)" -ge
  2`. `sort -u` counts *distinct* personas, which is what the sentence above claims; a `grep -c` counts matching
  lines, so one persona invoked twice passes. A Gemini sub-agent is invoked as a tool whose name is the agent slug
  (`docs/core/subagents.md`), so `tool_name` carries `debate-critic` with no prose matching.

**Wave 6. Replatforming: decide, then act.** 58 agents, 7 dispatchers, 6 phase pipelines. This wave opens with the Q3
decision, not with work. Whichever option is chosen, the exit is the same shape: every replatforming capability is
`mirrored` or `diverged` with a reason and a recheck date, and none survives as `pending`.
- **Exit**: `check_parity_drift.py --plugin replatforming --expect-total 62` exits 0 with no `pending` row. The 62,
  being 58 agents plus 4 skills, is the half that matters: "zero pending rows" is also true of a ledger replatforming
  was never entered into.

**Wave 7. Distribution and release.** Prove a clean-machine install, the property `scripts/test-clean-install.sh`
already asserts on the Claude side.
- **Exit**: after `git clone <repo-url> /tmp/twin`, `gemini extensions validate
  /tmp/twin/gemini/extensions/dev-standards` exits 0, then `gemini extensions install` on the same path exits 0 and
  `gemini extensions list | grep -q dev-standards`. For the skills, `check_parity_drift.py --plugin dev-standards
  --kind skill --print-mirrored | sort > /tmp/w7-want` with a non-zero line count, and `test "$(comm -23 /tmp/w7-want
  <(gemini skills list --all | awk '/^[a-z0-9-]+ \[/ {print $1}' | sort) | wc -l)" -eq 0`. The ledger and not a
  hardcoded 29 decides what that extension owes, because Q5 may make `unicredit-design-system` `diverged`.

## 9. Non-functional impact

| Dimension | Effect |
|---|---|
| **Security** | Net positive on the twin, net cost on ours. An extension can tighten and never loosen, so every permissive rule becomes an interactive approval plus a note in `GEMINI.md`. The extension environment is an allowlist, so every variable an MCP server reads is declared in `settings[]`, with `sensitive: true` sending credentials to the keychain. Against that, the twin doubles the surface on which client material could be published by mistake, which is why the denylist is a wave 1 check. |
| **Performance** | Each skill activation costs a consent turn. Four agents lose `skills:` preload. `effort` has no counterpart, so 24 agents lose their "think harder" hint and the nearest levers, `max_turns` and `temperature`, are not equivalent. Agent bodies instructing sequential reads are measurably slower than the host's `read_many_files` until rewritten. |
| **Reliability** | The failure modes are silent. All eight traps in the fact base produce no error: a ported supervisor that self-executes, an omitted `tools` list, a hook `timeout` off by a factor of a thousand, an extension `name` that does not match its directory. `gemini extensions validate` catches none of those four, only a broken manifest, so section 6 and the wave 5 transcript check exist because neither review nor the official validator catches them. |
| **Maintainability** | The definition of done for a capability doubles. The ledger is the only thing converting that cost into effort rather than into drift, and it works only because the freshness check fails the build. |
| **Deployment** | Two-step onboarding: clone, then install by path. `install` copies, so updating is `git pull` plus `gemini extensions update`. Everything takes effect only on session restart, including agents and commands. |
| **Cost** | Authoring cost roughly doubles per capability. Model cost is separate and undecided (Q7). CI cost is one Python step plus a vitest run, negligible against the existing `claude plugin validate` and clean-install jobs. |

## 10. Risks

Ranked by expected damage, each with the signal that says it is materialising.

1. **Consent friction makes the twin unpleasant enough to abandon.** A pipeline silently loading eight skills here
   becomes eight prompts there. *Signal*: a realistic wave 0 or 1 run produces more than two consent prompts, or a
   user adds a skill to `skills.disabled` in `~/.gemini/settings.json`. *Mitigation, designed in from wave 2*: fewer
   and larger skills on the Gemini side, and preload through `GEMINI.md` for the four agents losing `skills:`.
2. **The nine dispatchers are never restructured and the twin is a library, not a pipeline.** *Signal*: wave 6 opens
   with `pending` rows that survive two iterations, or the wave 5 transcript shows a single sub-agent call.
   *Response*: accept it explicitly. A twin carrying 50 skills and 78 workers has already delivered most of the value,
   and the pipelines can be recorded as `diverged` rather than left as permanent debt.
3. **Drift despite the gate, because the ledger is maintained by hand.** The freshness check catches a stale mirror;
   nothing catches a lazy `diverged` row except a human reading the reasons. *Signal*: `diverged` rows rise between
   releases, or `recheck` dates are pushed not resolved.
4. **Distribution blocked by enterprise policy.** `security.blockGitExtensions` blocks installing and loading
   **extensions** from Git and nothing else. It does **not** remove `gemini skills install --path`, and the difference
   matters because section 3 calls the skill layer the bulk of the value. Verified in the installed bundle: the
   extension manager is the only reader of the setting, and `installSkill` clones from Git behind its own consent
   prompt without ever consulting it. The sharper setting is `security.allowedExtensions`, patterns that "Overrides the
   blockGitExtensions setting". When non-empty it is tested against the resolved source of *every* install, local
   paths included, and the patterns are unanchored, so a managed workstation can block the local-path fallback this
   plan relies on, which `blockGitExtensions` alone cannot. *Signal*: `gemini extensions install
   /tmp/twin/gemini/extensions/<name>` fails with "not allowed by the allowedExtensions security setting", or a Git
   skill install succeeds where an extension install did not.
5. **Client material reaches a publishable unit.** *Signal*: a restricted capability name appears under a directory
   `publish-extension.sh` would touch, or an extension repository acquires the `gemini-cli-extension` topic. The wave
   1 denylist is the control.
6. **The Gemini surface moves under us.** Sub-agents are a preview feature and model identifiers churn faster than the
   rest of the surface. *Signal*: `npm update -g` followed by an empty `gemini extensions list`, or an agent that
   stops loading. *Mitigation*: pin no model string in ported material, set it once in `settings.json` or
   `agents.overrides`, and re-verify the fact base against the tag the team is on before each wave. It moves toward us
   as well as away: 0.57.0 provides `CLAUDE_PROJECT_DIR` in the hook environment as a documented compatibility alias
   (`docs/hooks/index.md`) and ships `gemini hooks migrate --from-claude`, so some divergence recorded today will
   resolve without work, and a `diverged` row is worth a recheck date rather than a rewrite.
7. **Two registries, one set of authors.** *Signal*: median PR size touching `plugins/**` grows, or contributors open
   `diverged` rows for plainly portable capabilities. The second signal is the honest one: the twin's cost has
   exceeded its perceived value, and the response is to narrow its scope, not to tighten the gate.

## 11. Open decisions for the user

**Q1. Where does the twin tree live?** (a) `gemini/extensions/` in this repository, as recommended; (b) a second
repository, `gemini-registry`; (c) one repository per extension. (b) and (c) turn the freshness check into a
cross-repository API call that needs a token and cannot block the offending PR.

**Q2. Who is the twin for?** (a) Accenture teammates already using Gemini CLI internally; (b) client delivery teams on
client infrastructure; (c) a public audience through the gallery. Only (c) justifies the per-repository topology, and
(c) is incompatible with `dev-standards` in its current shape.

**Q3. Does `replatforming` port at all?** (a) full restructure, seven supervisors become commands or main-agent
skills; (b) partial, mirror the 51 workers and let a human drive the phases; (c) leave it behind as `diverged` with a
recheck date. The largest cost item in the plan, and it should be decided at wave 0, not discovered at wave 6.

**Q4. What do the enterprise settings say on an Accenture managed workstation?** UNVERIFIED and not answerable here.
`cat ~/.gemini/settings.json` is not enough: the hierarchy is seven layers and layer 5 is a **system settings file**
that overrides the user and project files, for exactly this purpose, at `/Library/Application
Support/GeminiCli/settings.json` on macOS, `/etc/gemini-cli/settings.json` on Linux,
`C:\ProgramData\gemini-cli\settings.json` on Windows, or wherever `GEMINI_CLI_SYSTEM_SETTINGS_PATH` points. Read that
file and the user file, check `security.blockGitExtensions` and `security.allowedExtensions` in both, and look at the
admin policy directory while there. If either is set, every install becomes local path or fails outright, changing
wave 7 and risk 4 but not topology.

**Q5. Does the client design-system skill mirror at all?** (a) into the monorepo only, never into a publishable
extension; (b) not at all, recorded as `diverged`; (c) into a separate access-controlled extension. A client-contract
question, not an engineering one.

**Q6. Who owns the twin?** (a) the same authors, under a doubled definition of done enforced by the drift gate; (b) a
named twin owner running the sync on a cadence and holding a backlog of `pending` rows. (a) is cheaper and drifts
slower; (b) protects delivery velocity on the Claude side at the cost of a lag the ledger will at least report
honestly.

**Q7. Which Gemini model class replaces `opus` plus `effort: high`, and which `sonnet`?** Needs someone with current
access to the model line-up and its pricing. The fact base is deliberately silent on identifiers because they churn.
Whatever is chosen goes into `settings.json` or `agents.overrides` once, never into a ported agent body.

**Q8. One context file or two?** Gemini's `context.fileName` accepts a list, so `["AGENTS.md", "GEMINI.md"]` lets one
repository brief both hosts from a shared file. (a) Keep `CLAUDE.md` and per-extension `GEMINI.md` separate, as this
plan assumes; (b) extract the host-neutral conventions into `AGENTS.md` and leave each host file thin. (b) removes a
class of drift the ledger does not cover, because `CLAUDE.md` is not a capability and has no row. Whether Claude Code
reads a shared `AGENTS.md` the same way is UNVERIFIED here, and settles before (b) can be chosen.
