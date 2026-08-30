# Review Checklist

Use this checklist when reviewing a PR that adds or modifies a capability.

---

## 1. Frontmatter correctness

- [ ] `name` field is present
- [ ] `name` value matches the filename exactly (without `.md`)
- [ ] `name` is lowercase with hyphens only (no underscores, no spaces)
- [ ] `description` field is present
- [ ] `description` is specific enough to guide automatic delegation, not generic
- [ ] `description` does not use vague phrases like "helps with" or "assists in"
- [ ] A quote inside `description` is escaped, so the frontmatter still parses as YAML
- [ ] `tools` list is explicit and minimal (no unnecessary tools granted)
- [ ] `Skill` is in `tools` if the body mentions the `Skill` tool or tells the agent to
      invoke a skill
- [ ] `model` follows the policy in `how-to-write-a-capability.md`, or an HTML comment in
      the body says why it does not
- [ ] No unrecognized frontmatter fields. An unknown multi-line key corrupts the value of
      the key above it
- [ ] No secrets, tokens, API keys, or credentials

## 2. System prompt quality

- [ ] The role is clearly defined in the opening section
- [ ] At least one explicit output format is defined (tables, sections, templates)
- [ ] The subagent's scope is bounded. It knows what it does NOT do
- [ ] Mandatory behaviors are listed (things that happen in every interaction)
- [ ] Quality self-check is included (the subagent verifies its output before responding)
- [ ] The prompt is opinionated, with specific standards rather than general guidance
- [ ] Under `## What you never do`, no bullet joins a prohibition to its alternative with a
      colon or a dash. The alternative is in its own sentence
- [ ] Every capability the body names exists, under the flat name the runtime resolves
- [ ] No contradictory instructions
- [ ] No instructions that would conflict with Claude's safety guidelines

## 3. Behavior completeness (for analytical roles)

- [ ] Defines what information to gather before analyzing
- [ ] Defines how to handle missing context (ask for it, or note the assumption)
- [ ] Output includes severity/priority signals (not just a flat list of findings)
- [ ] Recommendations are actionable, not just observational

## 4. Behavior completeness (for developer roles)

- [ ] Architecture and layering rules are explicit
- [ ] Testing standards are defined (which frameworks, what coverage expectations)
- [ ] Error handling approach is defined
- [ ] Logging/observability standards are defined
- [ ] Security baseline is defined
- [ ] The subagent does not silently skip tests or omit error handling

## 5. Supporting artifacts

- [ ] At least one example file exists in `plugins/<plugin>/examples/`
- [ ] At least two scenarios in `plugins/<plugin>/evals/<name>/evals.json`, in the
      `{agent, query, files, expected_behavior}` shape, with `agent` equal to the directory
      name
- [ ] `plugins/<plugin>/evals/<name>/triggers.json` exists, in the
      `{query, should_trigger, description}` shape, with at least one negative case naming
      the sibling that should handle it instead
- [ ] CHANGELOG.md has an entry under `[Unreleased]`

## 6. Versioning

- [ ] The plugin's `version` in `plugin.json` is bumped per `release-process.md`
- [ ] A change to `name` or `description` is a MAJOR bump. Both are routing contract
- [ ] A capability this PR removes or renames is in the `RETIRED` dict, and no reference to
      the old name survives in `plugins/`, `wiki/`, `docs/`, `README.md` or `CLAUDE.md`
- [ ] If this modifies tools (removing one): this is a MAJOR version bump
- [ ] If this adds new behavior: this is a MINOR version bump
- [ ] If this is a prompt bug fix with no behavior change: this is a PATCH version bump

## 7. Naming conventions

- [ ] Filename follows `{role}.md` or `{role}-{specialization}.md` pattern
- [ ] No version numbers in filename
- [ ] No technology-first naming (`spring-developer.md` where `developer-java.md` is meant)

## 8. Common issues to watch for

- **Overlap**: Does this capability duplicate what another capability already does?
  If yes, consider extending the existing one instead.
- **Scope creep**: Is the capability trying to do too many unrelated things?
  If yes, split it.
- **Vague description**: Will Claude know when to automatically delegate to this?
  Test it: read the description and ask "would I know exactly when to use this?"
- **Missing constraints**: Does the developer capability omit critical standards
  (e.g. no testing guidance, no error handling)?
- **Tool excess**: Does the capability request tools it doesn't actually need?

## 9. Anti-pattern check (for new capabilities or substantial rewrites)

- [ ] Searched `ANTI-PATTERNS.md` for the role keywords of the proposed capability
- [ ] No matching precedent exists, OR a matching entry exists and the **Do not retry
      unless** clause is satisfied (state explicitly in the PR discussion which condition
      changed)
- [ ] If this PR deprecates an existing capability, an entry has been added to
      `ANTI-PATTERNS.md` in the same PR (per `GOVERNANCE.md` deprecation rule)

## 10. Skill-specific checks (only when the PR adds or modifies a skill)

- [ ] Skill lives at `plugins/<plugin>/skills/<name>/SKILL.md`, not under `agents/`
- [ ] Frontmatter has exactly `name` and `description`. `model`, `tools` and `color` are
      not SKILL.md fields and CI rejects them
- [ ] `name` equals the directory name, is kebab-case, is at most 64 characters, and
      contains neither `anthropic` nor `claude`
- [ ] `description` is at most 1024 characters, third person, and names the sibling skill
      to use instead where confusion is likely
- [ ] Body is under 500 lines. Overflow moved into `references/`, not compressed
- [ ] Content is declarative: standards, rules, templates, not workflow logic
- [ ] Each consuming agent loads it with the `Skill` tool and holds `Skill` in `tools`, or
      preloads it via `skills:` when it is needed on every run
- [ ] The skill lives in the same plugin as the agents that always need it. Any
      cross-plugin dependency is stated in the agent body and degrades gracefully

### If the skill ships a `scripts/` directory

- [ ] `scripts/README.md` exists and documents each script's **invocation, inputs,
      outputs, and exit codes** (so a consuming agent can call the script without
      reading the source)
- [ ] Each script's logic is genuinely deterministic: `if X then Y` rules, parsing,
      counting, regex checks. Judgment-bearing rules stay in the skill body
- [ ] The skill body names each script explicitly with a Bash recipe. The agent
      that invokes the skill must know exactly when and how to run it
- [ ] No script duplicates logic that already lives in another skill's `scripts/`. If the
      same check appears twice, factor it into a single source of truth

### If the skill ships a `references/` directory

- [ ] The body has crossed the 500-line gate, or is close enough that the next edit will
- [ ] Each reference file is linked from the skill body with a plain markdown link, one
      line per file saying what is in it, and resolves one level deep from `SKILL.md`
- [ ] A reference file over 100 lines opens with a `## Contents` table, so a partial read
      still shows the full scope

## Approval criteria

A PR can be approved when:
- All mandatory items above are checked
- The reviewer has read the full system prompt and found no contradictions or gaps
- The reviewer has confirmed the eval scenarios are realistic and would catch regressions

Leave a comment for each failing item. Do not approve with unchecked mandatory items.

## Automated gates

All four run in CI. Run them locally first.

```bash
python3 .github/scripts/validate_registry.py
```

```bash
claude plugin validate .
```

```bash
bash hooks/tests/test-pre-tool-safety.sh
```

```bash
bash scripts/test-clean-install.sh
```

- [ ] Every frontmatter under `plugins/` survives `yaml.safe_load`
- [ ] Combined subagent description budget under 13000 tokens (hard ceiling 15000)
- [ ] Every `SKILL.md` body under 500 lines
- [ ] Skill `description` under 1024 characters, third person
- [ ] `model`, `tools`, `color` absent from every `SKILL.md` frontmatter
- [ ] Reference links resolve and are one level deep
- [ ] Every `${CLAUDE_PLUGIN_ROOT}` path resolves inside its own plugin
- [ ] No repo-relative path to bundled material
- [ ] Every `references/...` path resolves in its own plugin, or its line names the owner
- [ ] Every agent body has `## When to invoke`
- [ ] Every agent that talks about skills holds the `Skill` tool
- [ ] No reference to a name in the `RETIRED` dict
- [ ] Every MCP server spec names an exact version or commit SHA
- [ ] `evals.json` and `triggers.json` key sets match, and every fixture path resolves
- [ ] No `triggers.json` description states a verdict or names a capability its query omits
- [ ] `bmad/design/workflow-dag-draft.json` lists exactly the agents in the tree

The run also prints warnings, which do not block: an agent body over 10000 characters,
`model: opus` with no HTML comment giving the reason, a `SKILL.md` over 400 lines with no
`references/` directory, a `when to use` heading inside a `SKILL.md`, a reference file over
100 lines with no `## Contents`, and a reference link deeper than one level. Read them
before approving.

The full gate table, with the validator function behind each one, is in
`how-to-write-a-capability.md` under "What CI enforces".
