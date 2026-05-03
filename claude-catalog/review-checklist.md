# Review Checklist

Use this checklist when reviewing a PR that adds or modifies a capability.

---

## 1. Frontmatter correctness

- [ ] `name` field is present
- [ ] `name` value matches the filename exactly (without `.md`)
- [ ] `name` is lowercase with hyphens only (no underscores, no spaces)
- [ ] `description` field is present
- [ ] `description` is specific enough to guide automatic delegation — not generic
- [ ] `description` does not use vague phrases like "helps with" or "assists in"
- [ ] `tools` list is explicit and minimal (no unnecessary tools granted)
- [ ] If `model: opus` is specified, the PR description explains why sonnet is insufficient
- [ ] No unrecognized frontmatter fields
- [ ] No secrets, tokens, API keys, or credentials

## 2. System prompt quality

- [ ] The role is clearly defined in the opening section
- [ ] At least one explicit output format is defined (tables, sections, templates)
- [ ] The subagent's scope is bounded — it knows what it does NOT do
- [ ] Mandatory behaviors are listed (things that happen in every interaction)
- [ ] Quality self-check is included (the subagent verifies its output before responding)
- [ ] The prompt is opinionated — it has specific standards, not just general guidance
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

- [ ] At least one example file exists in `examples/capability-name-example.md`
- [ ] At least two eval scenarios exist in `evals/capability-name-eval.md`
- [ ] CHANGELOG.md has an entry under `[Unreleased]`

## 6. Versioning

- [ ] If this is a new capability: version will be `0.1.0` (beta) or `1.0.0` (stable)
- [ ] If this modifies `name` or `description`: this is a MAJOR version bump
- [ ] If this modifies tools (removing one): this is a MAJOR version bump
- [ ] If this adds new behavior: this is a MINOR version bump
- [ ] If this is a prompt bug fix with no behavior change: this is a PATCH version bump

## 7. Naming conventions

- [ ] Filename follows `{role}.md` or `{role}-{specialization}.md` pattern
- [ ] No version numbers in filename
- [ ] No technology-first naming (e.g. `spring-developer.md` instead of `developer-java.md`)

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

## 10. Promotion-specific checks (only for beta → stable promotion PRs)

A promotion PR moves a capability's `"tier"` in `catalog.json` from `"beta"` to
`"stable"`. The PR description must state explicitly which criterion from
`release-process.md` § "Promotion: beta → stable" is being used.

- [ ] The PR description names the criterion: **A (time + adoption)** or **B (convergence)**
- [ ] If **Criterion A**: the capability has been in `beta` for ≥30 days since the last
      beta release, and is in active use in ≥2 projects. The PR description names the
      two projects.
- [ ] If **Criterion B**: the PR description cites **two or more independent project
      specializations** (under different projects' `.claude/agents/`) that have
      introduced the same modification, with the path under each project and the diff
      hunk that demonstrates the shared change.
- [ ] `CHANGELOG.md` entry for the new stable version states which criterion was used
      (and, for Criterion B, the convergence evidence)
- [ ] No critical issues are open against the capability

## 11. Skill-specific checks (only when the PR adds or modifies a skill)

- [ ] Skill file is in `claude-catalog/skills/`, not `agents/`
- [ ] `model: haiku` (knowledge retrieval; justify if higher model needed)
- [ ] `tools: Read` only — no Edit, Write, Bash, or Agent
- [ ] No `## Skills` section (skills are leaf nodes; they cannot delegate further)
- [ ] Content is purely declarative: standards, rules, templates — not workflow logic
- [ ] `catalog.json`: skill entry has `"type": "skill"` and `"tier": "skill"`
- [ ] Each dependent agent has this skill listed in its `"dependencies"` in `catalog.json`
- [ ] Each dependent agent's system prompt has a `## Skills` section invoking this skill

## Approval criteria

A PR can be approved when:
- All mandatory items above are checked
- The reviewer has read the full system prompt and found no contradictions or gaps
- The reviewer has confirmed the eval scenarios are realistic and would catch regressions

Leave a comment for each failing item. Do not approve with unchecked mandatory items.
