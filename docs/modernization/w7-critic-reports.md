# W7 adversarial review of the two verification reports

Reviewed: `docs/modernization/w7-final-audit.md` and `docs/modernization/w7-install-verification.md`.
Both were written against `756f883`. This review re-runs their evidence against `15f4749`, and
re-runs it a second time against a `git archive` export of `756f883` so that "was the claim true when
it was made" and "is it true now" are separated.

Environment for every measurement below: Claude Code 2.1.251, system `python3` 3.14.6, plus a
throwaway venv holding `tiktoken` 0.14.0 and `pyyaml` (system `python3` has neither, so the validator
silently takes its character-estimate branch on this machine). The `756f883` tree was exported with
`git archive 756f883 | tar -x -C <scratch>`; no worktree or branch was created and nothing in the
repository was modified.

Two framing corrections before the table, because both affect how the rest reads.

1. The brief states that 12011 was measured "for the same state" as the audit's 11798. It was not.
   11798 is `756f883`; 12011 is `15f4749`. The gap is two independent effects, separated below.
2. The brief states that neither report examined `wiki/`, `bmad/`, `templates/`, `settings/` or the
   root `.mcp.json`. The audit examined all five, in P2-6, P2-8 and P2-12, and its counts hold.
   `policies/`, `hooks/`, `archive/` and `.github/` are genuinely unexamined by both.

---

## Part 1: every finding in both reports, one row each

Verdict key. **FIXED** = true at `756f883`, not true at `15f4749`. **STILL PRESENT** = true at both.
**NEVER TRUE** = not reproducible at the state it was measured. **OVERSTATED** = the defect is real
but the number attached to it is not reproducible. **NEW DEFECT** = the repair introduced one.

### `w7-final-audit.md`, Part 1

| # | Claim | Verdict | Command I ran and what it returned |
|---|---|---|---|
| 1.1a | 114 `${CLAUDE_PLUGIN_ROOT}` refs all resolve inside their plugin | STILL TRUE, count now 188 | `grep -rho '\${CLAUDE_PLUGIN_ROOT}' plugins \| wc -l` returns `188` at tip, `114` in the `756f883` export; `python3 .github/scripts/validate_registry.py` reports 0 errors for `validate_plugin_root_refs` at both |
| 1.1b | 70 relative links survive; 1 `claude-catalog` marker survives | Links FIXED, marker STILL PRESENT | link scan below returns 0 at tip; `grep -rn 'claude-catalog' plugins` still returns exactly `plugins/deliberation/evals/deliberative-decision-engine-eval.md:273` |
| 1.2 | 11798 tokens `cl100k_base`, validator says 10166 | REPRODUCES EXACTLY, but the method is wrong | see the numbers section below; the audit's own extraction on the `756f883` export gives 11798 and the validator gives 10166 |
| 1.3a | All 46 `SKILL.md` at the documented depth | STILL TRUE | `find plugins -name SKILL.md \| grep -cv '^plugins/[^/]*/skills/[^/]*/SKILL.md$'` returns `0` |
| 1.3b | Frontmatter is exactly `name` plus `description` | STILL TRUE | per-file frontmatter key census over 46 files returns `46 description` and `46 name`, nothing else |
| 1.3c | Largest body 478 lines | OVERSTATED BY ONE, still under the gate | recount gives `479 plugins/docs-branding/skills/frontend-documentation/SKILL.md`, then 445 and 444 |
| 1.3d | 21 skill reference links, all resolve, none deeper than one level | STILL TRUE | python scan of `plugins/*/skills/*/SKILL.md` bodies returns `links: 21 broken: 0 deep: 0` |
| 1.4 | Manifests conform; unverified by the official CLI | CONFORM, and the "unverified" caveat is now FALSE | `claude plugin validate .` runs on this machine today and returns `Validation passed with warnings`, with 6 warnings neither report contains |
| 1.5 | Agent frontmatter uses only documented fields | STILL TRUE, and I checked the field list against the docs | census returns `name`/`description`/`tools`/`model`/`color` 86 each, `effort` 24, `experimental` 9, `skills` 4, `background` 1; all four unusual ones are documented subagent fields per `code.claude.com/docs/en/sub-agents`; all 4 `skills:` preloads resolve |

### `w7-final-audit.md`, Part 2

| # | Claim | Verdict | Command I ran and what it returned |
|---|---|---|---|
| P2-1 | 86 agents carry `tools:`, 0 permit `Skill`, 7 agents instruct skill loading | Tool gap FIXED for 19, the count of 7 was WRONG | `find plugins -path '*/agents/*' -name '*.md' -exec grep -l '^tools:.*Skill' {} + \| wc -l` returns `19` at tip and `0` on the export. But at `756f883` **19** agents already carried a `## Skills` section and **20** carried skill-loading language. The audit's table of 7 is a sample presented as the full set |
| P2-2 | 70 dangling links, 102 of 157 fail, 3 mangled rows in flight | Links FIXED; 70 and 102 are two different detectors and only 70 reproduces | see the counting section below |
| P2-3 | `~/.claude/CLAUDE.md` lines 37, 41, 58, 59 stale | STILL PRESENT | `grep -n 'developer-java-spring\|code-reviewer\|setup-capabilities\|claude-catalog' ~/.claude/CLAUDE.md` returns those four line numbers unchanged |
| P2-4 | Undeclared cross-plugin dependency on `deliberation`, no degradation note | STILL PRESENT | `.claude-plugin/marketplace.json` has no dependency field of any kind; `grep -rn 'deliberative-decision-engine' plugins/replatforming \| wc -l` returns `20`; the three cross-plugin rows are now prose, not links, and carry no fallback sentence |
| P2-5 | 40 of 46 persona openings, "eleven lines" of return contract | 40 REPRODUCES, 11 does not | `find plugins -name SKILL.md -exec grep -l '^You are ' {} + \| wc -l` returns `40` at both states. The audit's own command returns `10` on the export and `9` at tip, never 11 |
| P2-6 | 13 of 14 `wiki/` stale, 4 of 4 `bmad/` stale, `bmad/workflows.json` names two dead agents | STILL PRESENT, counts REPRODUCE | `grep -rl 'claude-catalog\|claude-marketplace\|setup-capabilities\|catalog\.json\|publish\.sh' wiki \| wc -l` returns `13` of 14 files, only `_Sidebar.md` clean; same grep on `bmad` returns all 4; `grep -n 'developer-java-spring\|code-reviewer' bmad/workflows.json` returns `92` and `97` |
| P2-7 | `scripts/present.sh:125` names a dead branding path | STILL PRESENT | `sed -n '125p' scripts/present.sh` prints the `claude-catalog/policies/accenture-branding.md` line; `ls policies/` returns only `python-conventions.md` |
| P2-8 | `settings/shared-settings-example.json` wires hooks to a dead prefix | STILL PRESENT | `grep -n 'claude-catalog' settings/shared-settings-example.json` returns lines 74 and 87; `ls hooks/scripts/` shows both scripts exist one directory up |
| P2-9 | `bmad/scripts/backfill-dag.py:12` cannot run | STILL PRESENT | `sed -n '12p' bmad/scripts/backfill-dag.py` prints the `claude-marketplace/catalog.json` constant; `ls claude-marketplace` returns `No such file or directory` |
| P2-10 | 4 orphaned reference files, 0 inbound references | STILL PRESENT, count REPRODUCES | all four exist; for each, `grep -rl "$(basename f)" plugins` excluding itself returns 0 |
| P2-11 | 16 surviving `beta` / `roadmap` flags | STILL PRESENT, count REPRODUCES | `grep -rn 'Status.*beta\|status: roadmap' plugins \| wc -l` returns `16`. Line numbers have shifted, for example `technical-analyst.md` is now `:122` not `:120` |
| P2-12 | Root `.mcp.json` duplicates the plugin MCP configs and is unpinned | STILL PRESENT | `cat .mcp.json` shows `@playwright/mcp@latest` and `git+https://github.com/antoinebou12/uml-mcp` with no ref, against `@0.0.79` and `@78137bd6...` in the two plugin files |
| P2-13 | 14 official plugins; 16 official agents contributing about 2275 tokens | Overlap table STILL TRUE, the numbers are OVERSTATED | de-duplicating the cache by `(plugin, agent)` (it holds three copies of most plugins) gives **15** unique agents carrying a description and **1976** `cl100k_base` tokens, not 16 and 2275 |

### `w7-final-audit.md`, Part 3

| # | Claim | Verdict | Command I ran and what it returned |
|---|---|---|---|
| P3-1 | `WORDS_TO_TOKENS = 1.35` undercounts by 16.05 percent; real margin 1.7 percent; per-user total 14073 of 15000 | Heuristic FIXED, the 14073 figure is WRONG | the constant is gone; `.github/scripts/validate_registry.py:31` now tries `tiktoken` and falls back to `CHARS_PER_TOKEN = 4.67`. The 15000 per-user ceiling is confirmed verbatim from `code.claude.com/docs/en/sub-agents`. But 14073 = 11798 + 2275 and 2275 is a triple count. Recomputed total below |
| P3-2 | CI has no gate for repo-relative links | FIXED, with a hole | `grep -n 'def validate_' .github/scripts/validate_registry.py` now lists `validate_relative_links` and `validate_agent_references`. Both holes are in the "missed" list below |
| P3-3 | `license: "UNLICENSED"` is not SPDX | STILL PRESENT | `grep -h '"license"' plugins/*/.claude-plugin/plugin.json \| sort \| uniq -c` returns `6 "license": "UNLICENSED",`. The official CLI does not flag it |
| P3-4 | Validator's reserved-name list has 5 of at least 16 | STILL PRESENT | `sed -n '17,18p' .github/scripts/validate_registry.py` shows the same 5 names |
| P3-5 | Skill glob non-recursive; `field()` truncates at an inner `word:` line | STILL PRESENT | line 141 in the audited copy is now `glob.glob("plugins/*/skills/*/SKILL.md")` at line 182, still non-recursive against the `**` used for agents; `field()` at line 82 is unchanged |
| P3-6 | The two colour sources conflict; magenta is safe | Conflict CONFIRMED, "safe" NOT ESTABLISHED | web doc lists `red blue green yellow purple orange pink cyan`, bundled `agent-development/SKILL.md:111` lists `blue cyan green yellow magenta red`. Registry uses exactly the bundled six (14 blue, 14 cyan, 12 green, 14 magenta, 15 red, 17 yellow). But the CLI does not validate colour at all: I put `color: chartreuse` on an agent in a scratch plugin and `claude plugin validate` passed it. The audit's inference from string counts in the bundle is not evidence about validation |
| P3-7 | `claude plugin validate .` blocked by managed settings | NO LONGER TRUE | the command runs and exits 0 on this machine, same CLI build (2.1.251) both reports cite |
| P3-8 | Skill descriptions third person; all 86 agents carry `## When to invoke` | STILL TRUE | per-file loop over 86 agents reports `count=0` missing the section |

### `w7-install-verification.md`

| Step | Claim | Verdict | Command I ran and what it returned |
|---|---|---|---|
| Verdict | "Everything the migration was supposed to fix is fixed" | NEVER TRUE | at the very commit it verified, 84 relative links inside `plugins/` did not resolve, spread over 14 files. Its own Step 5 found 8 of them |
| Verdict 1 | "8 dangling read instructions" | NEVER TRUE as a repo-wide count | the report traced two supervisor files by hand and generalised. Per-file counts on the `756f883` export: `refactoring-tobe-supervisor.md` 16, `baseline-testing-supervisor.md` 14, `technical-analysis-supervisor.md` 13, `functional-analysis-supervisor.md` 12, `tobe-testing-supervisor.md` 9, `user-flow-analyst.md` 7. None of those files appears anywhere in the report |
| Verdict 2 | `code-reviewer` named but never defined | TRUE then, FIXED now | `grep -rn '^name: code-reviewer' plugins \| wc -l` returns `0` at both states, but every call site now reads `pr-review-toolkit:code-reviewer (official Anthropic marketplace, optional: skip this step when the plugin is not installed)` |
| Verdict 3 | End-to-end install never executed; CLI blocked | Install still untested, the block is GONE | `claude plugin validate .` succeeds today |
| Drift note | `f58d52d` touches no path under `plugins/` or `.claude-plugin/` | TRUE | `git show f58d52d | grep '^diff'` returns exactly the two `.github/` files |
| 2.1 | 6 plugins, all sources resolve | STILL TRUE | `claude plugin validate .` resolves all 6 and validates each manifest |
| 2.2 | Inventory 58/12/7/4/5/0 agents, 46 skills, no duplicate names | STILL TRUE, REPRODUCES EXACTLY | per-plugin `find` counts match row for row; `uniq -d` over agent basenames and skill directory names returns nothing |
| 2.3 | 114 refs, 78 unique, 0 unresolved, 0 bare `$CLAUDE_PLUGIN_ROOT` | TRUE then, count now 188 | `grep -rho '[^{]\$CLAUDE_PLUGIN_ROOT' plugins \| wc -l` returns `0`; validator reports no unresolved ref at 188 |
| 2.4 | Two `.mcp.json`, both valid, both pinned | STILL TRUE | both parse; pins as quoted in P2-12 above |
| 2.5 | Validator 0 errors 0 warnings, 10166 tokens | TRUE then; the number is now environment dependent | at tip the same script prints `11974` under system `python3` and `12011` under a `tiktoken` interpreter, both with 0 errors and 0 warnings |
| 4 | Path independence holds; 0 absolute host paths; 0 root escapes | STILL TRUE | `grep -rn '/Users/luca' plugins \| wc -l` and `grep -rn '${CLAUDE_PLUGIN_ROOT}/\.\.' plugins \| wc -l` both return `0` |
| 5.1 | `indexing-supervisor` 9 of 9 reference docs resolve | TRUE | that file contains zero `docs/` links; it was already on `${CLAUDE_PLUGIN_ROOT}` |
| 5.2 | `refactoring-supervisor` 18 of 19 resolve | TRUE | exactly one entry for that file in my `756f883` broken-link list, at `:96` |
| 5.3 D1 | `refactoring-supervisor.md:96` cross-plugin link | FIXED as prose | line 96 now reads `the \`deliberation\` plugin's \`references/deliberation/integration-replatforming.md\``, no longer a link, still not machine-resolvable |
| 5.3 D2 to D4 | `deliberation-integration.md:25,43,88` | FIXED as prose | same treatment at lines 25, 43, 88 |
| 5.3 D5 | `cross-phase-iteration.md:173` bare filename | STILL PRESENT | `grep -n 'integration-replatforming' plugins/replatforming/references/refactoring-workflow/cross-phase-iteration.md` returns `173:` with the bare filename unchanged |
| 5.3 D6 | `iteration-loop.md:22` bare filename | STILL PRESENT | same grep on `iteration-loop.md` returns `22:` bare, while `112`, `162` and `168` in the same file did get the prose treatment |
| 5.3 D7 | `per-phase-protocol.md:405` points at a section that does not exist | STILL PRESENT | line 405 still says `refactoring-supervisor.md` section "Decision rules"; `grep -n '^#' plugins/replatforming/agents/refactoring-supervisor.md` returns only Role, When to invoke, Reference docs |
| 5.3 D8 | `ui-smoke-gate.md:5` says "in the registry root" | STILL PRESENT | `sed -n '1,8p'` on that file still says "in the registry root"; the file is at `archive/INFOSYNC-REFACTORING-AGENT-GAP-REPORT.md` |
| 5.5 | `deliberative-decision-engine-eval.md:273` and `orchestrator.md:59` stale | STILL PRESENT | both greps return the cited lines unchanged |
| Assets | Root trees unreachable, no manifest declares `hooks` | STILL TRUE | `grep -l '"hooks"' plugins/*/.claude-plugin/plugin.json` returns nothing |

---

## Part 2: the numbers, recomputed

Both reports assert numbers. Every one is below, measured by me.

### Description budget: which method, and which is right

Four extractions of the same 86 descriptions, all encoded with `cl100k_base`:

| Extraction | `756f883` | `15f4749` |
|---|---:|---:|
| A. Audit's script: single-line `^description:` regex, then `.strip('"')` | **11798** | 11917 |
| B. Validator `field()`: multi-line, keeps the surrounding quotes | 11892 | **12011** |
| C. Real YAML parse of the frontmatter | 11777 (86 files) | 11573 (**84** files; 2 fail to parse) |
| D. Validator's fallback, `len(chars) / 4.67`, no tokenizer | 11894 | 11974 |
| E. Old heuristic, `words * 1.35` | **10166** | 10278 |

So 11798 and 12011 differ for two independent reasons, not one:

- +119 tokens is real content restored by `15f4749`.
- +94 tokens is measurement. Extraction B keeps the two `"` characters that YAML strips. Every one
  of the 86 descriptions is a double-quoted scalar, and B's character total is exactly
  86 x 2 = 172 characters higher than A's at both commits.

Which is right: **neither**. Claude Code parses YAML, so the counted string is row C, not A or B.
The audit is closer than the validator, because stripping the quotes is what YAML does. The
validator over-reports by about 0.8 percent by keeping them, and by considerably more on the two
agents whose frontmatter no longer parses, where it counts a duplicated garbage fragment as budget
that at runtime contributes nothing. Reproduce:

```bash
python3 - <<'PY'
import glob, yaml, tiktoken
enc = tiktoken.get_encoding("cl100k_base")
tot = n = bad = 0
for p in sorted(glob.glob("plugins/*/agents/**/*.md", recursive=True)):
    t = open(p).read(); e = t.find("\n" + "-"*3, 3)
    try: d = yaml.safe_load(t[3:e])
    except Exception: bad += 1; continue
    tot += len(enc.encode(d["description"])); n += 1
print("parsed", n, "tokens", tot, "unparseable", bad)
PY
```

### Per-user total against the 15000 ceiling

The 15000 figure is confirmed verbatim from `code.claude.com/docs/en/sub-agents`, so the audit is
right to correct the brief's 12000. Its arithmetic is not.

| Component | Audit | Mine |
|---|---:|---:|
| This registry | 11798 | 11573 (YAML-parsed, tip) |
| Official plugins already enabled | 2275 over 16 agents | 1976 over 15 agents |
| **Total** | **14073**, 94 percent of ceiling | **13549**, 90 percent of ceiling |

The audit's official-plugin figure counts the cache directory as flat. It is not: `agent-sdk-dev`,
`code-review`, `commit-commands`, `feature-dev`, `hookify`, `plugin-dev`, `pr-review-toolkit`,
`session-report` and `skill-creator` each hold three copies (`1b46aa6d4a11`, `ed404106fcd8`,
`unknown`) and `chrome-devtools-mcp` holds two. De-duplicating by `(plugin, agent name)` is what
produces 15 and 1976. Reproduce with `ls ~/.claude/plugins/cache/claude-plugins-official/*/`.

### 70 against 84 dangling links

Both are correct; they are different detectors run on the same tree, and the difference is entirely
explained by regex shape. Measured on the `756f883` export:

| Detector | Pattern | Unresolved |
|---|---|---:|
| Audit's published command | `\]\((\.\.[^)\s]*)\)`, requires a leading `..` | **70** |
| `validate_relative_links` as shipped | `\]\((\.\.?/...\.md)\)` or backticked `` `../...md` ``, so it also catches `./` and bare backticks | **84** |
| Every relative target of any shape | `\]\(([^)\s]+)\)` minus http, anchor, mailto, variable | 105 of 157 |

84 is the better number: the audit's regex misses the `./`-prefixed and backticked forms. The audit's
narrative figure of "102 fail of 157" is the one that does not reproduce. 157 reproduces exactly.
I get 105, and the audit's three named exclusion classes are not among the 70 its own command
returns, so the arithmetic 102 minus 32 equals 70 does not describe any run I can reconstruct.

At the tip all three detectors return 0 genuinely broken links. The 35 residual hits from the
broadest detector are 31 intentional template links in the three classes the audit named, plus 3
anchor-fragment false positives (`policies.md#...`, `output-layout.md#...`) whose files exist.

### Link rewrites: correctness of the 84

- 70 markdown links removed, 74 `${CLAUDE_PLUGIN_ROOT}` refs added, 0 relative links added.
  `git diff 756f883 15f4749 plugins` then filtering on `](` shows this.
- I paired removed and added targets hunk by hunk. Every pair keeps the same basename and the same
  subpath below `docs/` to `references/`. **No link was rewritten to the wrong target.**
- The 3 mangled table rows the audit warned about at `baseline-testing-supervisor.md:67`,
  `technical-analysis-supervisor.md:63` and `functional-analysis-supervisor.md:60` are **gone**.
  All three are now well-formed table cells with no unclosed `[`. `grep -rn "plugin's \`references/"
  plugins` returns 16 occurrences across 9 files, all well-formed prose.

### Other counted claims

| Claim | Source | Mine |
|---|---|---|
| 86 agents, 46 skills, 6 plugins, 0 commands | both | reproduces exactly |
| 46 skills carry exactly `name` and `description` | audit 1.3b | reproduces |
| 40 of 46 persona openings | audit P2-5 | reproduces |
| 11 return-contract lines | audit P2-5 | 10 on the export, 9 at tip |
| 478-line largest skill body | audit 1.3c | 479 |
| 16 beta or roadmap flags | audit P2-11 | reproduces |
| 13 of 14 wiki, 4 of 4 bmad | audit P2-6 | reproduces |
| 114 plugin-root refs, 78 unique | install 2.3 | reproduces on the export |
| 67 eval suites | commit message | 73 `triggers.json` and 27 `evals.json` over 73 directories |

---

## Part 3: what both reports missed, most severe first

### M1 CRITICAL. The repair commit broke two agents' YAML and the official CLI now fails the marketplace

`plugins/analysis-architecture/agents/technical-analyst.md:3` and
`plugins/docs-branding/agents/documentation/wiki-writer.md:3`. The fix for the description content
loss appended the restored text after an unescaped closing `"`, leaving a bare `."produce a technical
health report for this repo\", \", and \". Typical user phrasings: ...` on the same line. The
double-quoted scalar terminates early and the rest is a syntax error.

`claude plugin validate plugins/analysis-architecture` returns, verbatim:

> `frontmatter: YAML frontmatter failed to parse: YAML Parse error: Unexpected token. At runtime this
> agent loads with its name taken from the filename and every other frontmatter field silently
> dropped.`

Consequences all at once: both agents lose their `description`, so they will never be delegated to;
both lose `tools`, including the `Skill` entry the same commit added; both lose `model` and `color`.
The `", and "` fragment that finding 3 of the commit set out to remove is still present in both, so
the defect was not fixed, it was upgraded from cosmetic to load-breaking.

This is a regression, not a pre-existing condition. Reproduce:

```bash
git archive 756f883 | tar -x -C /tmp/at756 && claude plugin validate /tmp/at756/plugins/analysis-architecture   # passes
claude plugin validate plugins/analysis-architecture                                                            # fails
python3 - <<'PY'
import glob, yaml
for p in sorted(glob.glob("plugins/*/agents/**/*.md", recursive=True)):
    t = open(p).read(); e = t.find("\n" + "-"*3, 3)
    try: yaml.safe_load(t[3:e])
    except Exception as ex: print(p, "::", str(ex).splitlines()[0])
PY
```

### M2 CRITICAL. CI cannot fail on the official validator, which is why M1 landed

`.github/workflows/validate-pr.yml:43` to `:54`. The step that runs the official tool is
`claude plugin validate . 2>&1 || echo "(unavailable in this environment)"` and additionally carries
`continue-on-error: true` at line 54. The `||` swallows the exit code before `continue-on-error` even
matters, and the only failure gate, at line 92, keys on `steps.validate.outcome` where `validate` is
the id of the **Python** step at line 31, not the Claude step. So the official validator's verdict is
posted to the PR comment and can never fail the build.

The repo validator does not catch M1 either, because `field()` at
`.github/scripts/validate_registry.py:82` is a regex, not a YAML parser. Both gates are green on a
tree the official tool rejects.

```bash
bash -c 'claude plugin validate plugins/analysis-architecture >/dev/null 2>&1 || echo "(unavailable)"; echo "step exit=$?"'
# prints: (unavailable)  /  step exit=0
python3 .github/scripts/validate_registry.py | tail -3
# prints: **Errors: 0 | Warnings: 0**
```

### M3 HIGH. `developer-frontend` still cannot invoke skills, and the new gate is blind to it

`developer-frontend.md` line 4 is
`tools: Read, Edit, Write, Bash, Grep, Glob`, with no `Skill`. Lines 69 and 80 are
`## Step 2 ... Invoke the framework skill set` and `## Step 3 ... Invoke cross-framework skills`, and
the file mentions skills 14 times. The gate added at `validate_registry.py:174` fires only on the
literal string `## Skills`, and this file uses different headings, so CI passes it.

This is the agent the audit itself singled out as having "an entire Step 2 / Step 3 invoke the
framework skill set protocol", and it is the one agent of the 20 that the repair left behind.

```bash
grep -n '^tools:' plugins/dev-standards/agents/developers/developer-frontend.md
grep -n 'Invoke the framework skill set' plugins/dev-standards/agents/developers/developer-frontend.md
find plugins -path '*/agents/*' -name '*.md' -exec grep -l '^tools:.*Skill' {} + | wc -l   # 19, not 20
```

### M4 HIGH. 13 skill invocations still use retired catalog paths, now on agents that hold the `Skill` tool

The commit claims 26 old-style paths were normalised. 13 survive, in 5 agent bodies. Three of those
agents were given the `Skill` tool by the same commit, so the instruction is now live and points at
a name that does not exist.

| File and line | Token | Agent holds `Skill` |
|---|---|---|
| `plugins/dev-standards/agents/test-writer.md:50` | `frontend/react/react-expert` | yes |
| `plugins/dev-standards/agents/test-writer.md:54` | `frontend/angular/angular-expert` | yes |
| `plugins/dev-standards/agents/test-writer.md:65,68,77` | `testing/testing-standards` | yes |
| `plugins/dev-standards/agents/test-writer.md:66` | `backend/java-spring-standards` | yes |
| `plugins/dev-standards/agents/developers/developer-java.md:93,94` | `backend/java-spring-standards`, `testing/testing-standards` | yes |
| `plugins/docs-branding/agents/documentation/wiki-writer.md:60` | `documentation/doc-expert` | yes, but see M1 |
| `plugins/dev-standards/agents/developers/developer-frontend.md:84,88,92,98` | `frontend/design-expert`, `frontend/css-expert`, `testing/testing-standards`, `refactoring/refactoring-expert` | no, see M3 |

The real skill names are the bare directory names. Reproduce:

```bash
find plugins -path '*/agents/*' -name '*.md' -exec grep -noE '`(testing|frontend|backend|documentation|analysis|refactoring)/[a-z0-9/._-]+`' {} +
find plugins -name SKILL.md | sed -E 's|plugins/[^/]+/skills/([^/]+)/SKILL.md|\1|' | sort
```

### M5 HIGH. The safety hook fails open on trivial variants and blocks legitimate commands

`hooks/scripts/pre-tool-safety.sh:40` to `:58`. The blocklist entries are fed to `grep -qiE` as
unanchored substrings, so flag reordering walks straight past them, while any path under `/` is
caught. Both reports touched this file only to note that `settings/shared-settings-example.json`
points at the wrong prefix. Neither executed it.

```bash
echo '{"tool_input":{"command":"rm -fr /"}}'                     | bash hooks/scripts/pre-tool-safety.sh; echo $?  # 0, allowed
echo '{"tool_input":{"command":"rm --no-preserve-root -rf /"}}'  | bash hooks/scripts/pre-tool-safety.sh; echo $?  # 0, allowed
echo '{"tool_input":{"command":"rm -rf /"}}'                     | bash hooks/scripts/pre-tool-safety.sh; echo $?  # 2, blocked
echo '{"tool_input":{"command":"rm -rf /tmp/scratch"}}'          | bash hooks/scripts/pre-tool-safety.sh; echo $?  # 2, false positive
```

Separately, `hooks/scripts/pre-tool-safety.sh:11` documents its own install path as
`.claude/hooks/pre-tool-safety.sh`. That is a third path, disagreeing both with where the file lives
(`hooks/scripts/`) and with what the settings example says (`claude-catalog/hooks/scripts/`).

### M6 HIGH. The `RETIRED` gate scans the one tree that is already clean

`validate_registry.py:251` to `:268` globs `plugins/**/*.md`. Every surviving reference to a retired
capability is outside that glob:

- `bmad/workflows.json:92` `developer-java-spring`, `:97` `code-reviewer`, and `CLAUDE.md:107` calls
  this file the phase DAG.
- `bmad/design/workflow-dag-draft.json` and `bmad/design/mapping.md`.
- `wiki/Reference.md`, `wiki/FAQ.md`, `wiki/Usage.md`, `wiki/Governance.md`, `wiki/Quick-start.md`,
  `wiki/Capability-catalog.md`.

The gate also skips non-markdown files inside `plugins/`, so the 73 `triggers.json` and 27
`evals.json` are unscanned by it.

```bash
for n in code-reviewer developer-java-spring; do grep -rln "$n" bmad wiki; done
grep -n 'plugins/\*\*/\*.md' .github/scripts/validate_registry.py   # three call sites, all markdown only
```

### M7 MEDIUM. The repair raised the budget gate but left `CLAUDE.md` documenting the old one

`CLAUDE.md:69`, under the heading "Conventions that are enforced by CI", still reads "Combined
subagent descriptions stay under **12000 tokens** across all plugins enabled at once." The repair
commit moved the gate: `BUDGET_FAIL, BUDGET_WARN = 15000, 12000` at `validate_registry.py:23` in the
`756f883` export is `15000, 13000` at the tip.

So the registry now sits at 12011 tokens, which is 11 tokens **over** its own documented convention
and 989 under the gate that actually runs. Nothing reports this, because the number CLAUDE.md states
is no longer a number the validator knows about. `CLAUDE.md` also opens with "Any change to a
capability updates, in the same commit ... the documentation", so the commit that changed the
constant broke the repo's own primary rule.

```bash
grep -n '12000 tokens' CLAUDE.md
grep -n 'BUDGET_FAIL, BUDGET_WARN' .github/scripts/validate_registry.py
git archive 756f883 | tar -xO .github/scripts/validate_registry.py | grep -n 'BUDGET_FAIL, BUDGET_WARN'
```

### M8 MEDIUM. Every eval suite is in a format the official runner cannot execute

The help text for `claude plugin eval` states the runner reads `<eval dir>/**/case.yaml` or
`prompt.md + graders/*.md`. The repository contains zero of those and 100 JSON files instead. No
`plugin.json` declares `experimental.evals` either.

```bash
find plugins -path '*/evals/*' -type f | sed -E 's|.*/||' | sort | uniq -c
# 73 triggers.json, 27 evals.json, 8 *-eval.md, 0 case.yaml, 0 prompt.md
grep -l 'evals' plugins/*/.claude-plugin/plugin.json   # nothing
```

Stated with a caveat: `CLAUDE.md:109` to `:114` defines this JSON convention itself, so the files are
internally consistent with the repo's own rule. The finding is that the repo's convention and the
official tooling have diverged, and `claude plugin eval` on this machine returns
`plugin eval is currently in early access`, so I could not execute it to confirm end to end.

### M9 MEDIUM. Two incompatible `evals.json` schemas coexist

21 files added by `15f4749` use `{agent, query, files, expected_behavior}`. 6 pre-existing files use
`{id, prompt, expectations, timeout}`. Nothing reconciles them, and 3 of the 6 are the pipeline
supervisors.

```bash
python3 - <<'PY'
import json, glob, collections
c = collections.Counter()
for p in sorted(glob.glob("plugins/*/evals/*/evals.json")):
    c[tuple(sorted({k for i in json.load(open(p)) for k in i}))] += 1
print(c)
PY
```

On the consistency question the brief raises: **no eval directory names a capability that does not
exist**, and **no directory belongs to a plugin other than the one that owns the capability**. I
checked all 73 against the 86 agent names and 46 skill names. The `agent` field agrees with the
directory name in all 21 files that carry one; the other 6 simply have no such field.

### M10 MEDIUM. The trigger-eval answer leak is fixed, but a length artefact replaces it

Measured over all 365 cases in the 73 `triggers.json` files: 216 positive, 149 negative, majority
base rate 0.592. The parenthesis classifier the commit describes now scores **0.589**, marginally
below the base rate. That fix is real.

What replaced it: positives are systematically longer. Median query length is 77 characters for
positives against 61 for negatives, and the best single length threshold, "70 characters or more
means trigger", scores **0.699**, which is 10.7 points above the base rate without reading a word.
66 of 73 suites also have the identical shape of exactly 3 positives and 2 negatives.

The rationale that used to sit in the query now sits in the `description` field, where 201 of 216
positives read "Primary invocation" and negatives read strings such as "Confusable query, should
route to `spring-architecture` instead". The label is still recoverable from the record; it moved
rather than disappeared.

```bash
python3 - <<'PY'
import json, glob, statistics
pos, neg = [], []
for p in glob.glob("plugins/*/evals/*/triggers.json"):
    for i in json.load(open(p)):
        (pos if i["should_trigger"] else neg).append(i["query"])
n = len(pos) + len(neg)
print("base rate", round(max(len(pos), len(neg))/n, 3))
print("paren classifier", round((sum("(" not in q for q in pos) + sum("(" in q for q in neg))/n, 3))
best = max((sum(len(q) >= t for q in pos) + sum(len(q) < t for q in neg), t) for t in range(30, 140))
print("best length threshold", best[1], round(best[0]/n, 3))
print("median len pos/neg", statistics.median(map(len, pos)), statistics.median(map(len, neg)))
PY
```

### M11 MEDIUM. Six official-CLI warnings neither report contains

`claude plugin validate .` emits one warning per plugin:

> `category: Field 'category' belongs in the marketplace entry (marketplace.json), not plugin.json.
> It's harmless here but unused. Claude Code ignores it at load time.`

Both reports asserted this command could not be run, so neither surfaced them. The audit's finding
1.4 explicitly says its verdict rests on a manual field-by-field comparison "not on the official
tool"; the tool has a different opinion about `category`.

### M12 MEDIUM. The root `.mcp.json` fetches an unpinned third-party server from a personal account

`.mcp.json:3` to `:15` runs `uvx --from git+https://github.com/antoinebou12/uml-mcp uml-mcp` with no
ref, so every session in this repository resolves that repository's default branch at run time and
executes it. `plugins/docs-branding/.mcp.json` pins the same source to
`@78137bd66bfeb9754d0d5de0be1016f4dc053cc6`. The audit noted the pinning inconsistency as its
lowest-severity item and framed it as discipline. The unpinned side is the one that runs code.

```bash
cat .mcp.json plugins/docs-branding/.mcp.json
```

### M13 LOW. The new `validate_relative_links` gate has three shapes it cannot see

`.github/scripts/validate_registry.py:242`. The pattern requires a `./` or `../` prefix **and** a
`.md` suffix, and the backtick alternative only accepts `../`. So a bare sibling link
(`](policies.md)`), any anchored link (`](./output-layout.md#section)`), any non-markdown target and
any directory target are invisible. `plugins/replatforming/references/baseline-testing/wave-overview.md:22`
is a live example of the bare-sibling shape; it happens to resolve today, which is exactly why the
hole is latent rather than visible.

### M14 LOW. `policies/python-conventions.md` is orphaned

`grep -rn 'policies/python-conventions' .` outside `docs/modernization/` returns nothing. The only
reference to anything in `policies/` anywhere in the repo is `scripts/present.sh:125`, and it names a
file that was moved out of `policies/` before it was renamed. Neither report opened the directory.

### M15 LOW. The em dash cleanup covered skills only

The commit reports 589 em dashes replaced across 60 skill files. Remaining under `plugins/`: 351 in
`SKILL.md`, 1229 in agent bodies, 1492 in reference files, plus 39 lines with a spaced double hyphen.
Two of the surviving agent-body instances are inside the M1 descriptions.

```bash
find plugins -name SKILL.md -exec grep -o '—' {} + | wc -l
find plugins -path '*/agents/*' -name '*.md' -exec grep -o '—' {} + | wc -l
```

---

## How much of each report I would trust

**`w7-final-audit.md`: high on structure, medium on arithmetic, and it buried its best finding.**
Every one of its nine Part 1 verdicts survives re-measurement, and its Part 2 medium and low findings
(P2-6 through P2-12) reproduce line for line, including the awkward ones like the 16 beta flags and
the 4 orphan files. Its two critical findings were both real and both got fixed. Where it degrades is
counting: 11798 reproduces but measures the wrong string, 102 of 157 does not reproduce at all, 2275
official tokens is a triple count that propagates into the headline 14073, "eleven" return-contract
lines is 10, "478 lines" is 479, and most consequentially its P2-1 table of 7 skill-loading agents
understates a population of 20 by two thirds, which is how `developer-frontend` survived the repair.
It also let the managed-settings error stand as a reason not to run the official validator, and that
validator finds a real error the audit's own method could not. Trust its findings; recompute every
number it states.

**`w7-install-verification.md`: low. Its headline verdict was false at the commit it verified.**
The mechanical work is sound and reproduces exactly: 6 plugins, 86 agents, 46 skills, 114 plugin-root
references with 0 unresolved, 0 absolute paths, 0 root escapes, path independence, and a careful
guard against its own regex being too lenient. D1 through D8 are all genuine, and D5 through D8 are
still unfixed today, so it found four things nothing else has closed. But "everything the migration
was supposed to fix is fixed" was untrue when written, and "8 dangling read instructions" is a
two-file hand trace generalised into a repo-wide count that was wrong by a factor of ten. It never
opened the five pipeline supervisors that were the worst-affected files in the repository, and it
listed the unpublished root trees without inspecting any of them. Trust its inventory and its
plugin-root verification. Do not trust any statement it makes about coverage.

**On the current tip.** The two critical defects both reports were commissioned to find are fixed and
the fixes are correct where they were applied. The repair introduced one new defect of equal severity
(M1), left one agent of twenty behind (M3), left thirteen skill references pointing at names that do
not exist (M4), pointed its new retirement gate at a tree that was already clean (M6), and moved the
budget gate without moving the number `CLAUDE.md` publishes as the gate (M7). The official CLI,
which runs today, fails this marketplace.
