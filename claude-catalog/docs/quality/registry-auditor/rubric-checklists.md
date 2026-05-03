# Rubric checklists — embedded fallback

> Reference doc for `registry-auditor`. Read at runtime when the official
> Anthropic rubric skills (`agent-development`, `skill-development`,
> `skill-creator`, `claude-md-improver`) are not installed locally.

These checklists are the embedded fallback used to grade the registry when the
authoritative skill files cannot be resolved on disk. Cite criteria by name and
number when reporting findings (e.g., "agent-development §6").

## Agents (per `agent-development`)

1. **Frontmatter required:** `name`, `description`, `model`, `color`. Optional:
   `tools`, `model_justification` (this registry requires it for `model: opus`
   per its CLAUDE.md).
2. **`name`:** 3–50 chars, lowercase + hyphens, must start/end alphanumeric.
3. **`model`:** `inherit` | `sonnet` | `opus` | `haiku`. Spec recommends
   `inherit`. This registry uses `sonnet`/`opus` deliberately — flag once, not
   per-file.
4. **`color`:** `blue` | `cyan` | `green` | `yellow` | `magenta` | `red`. Flag
   missing or non-spec values (`purple`, `orange`).
5. **`tools`:** principle of least privilege. Read-only analysts should not ship
   `Bash` or `Write` unless they actually shell out or write files.
6. **Description shape:** "Use this agent when [conditions]. Typical triggers
   include [scenario 1], [scenario 2], …" + pointer `See "When to invoke" in the
   agent body for worked scenarios.` Length 200–1000 chars ideal; 5000 char hard
   ceiling.
7. **Body has a `## When to invoke` section** with 2–4 worked scenarios as prose
   bullets.
8. **System prompt in second person** ("You are…"). Flag first- or third-person
   drift.
9. **Body length:** 500–3000 chars ideal, 10 000 char hard ceiling. Flag bodies
   >10k as candidates for extracting per-phase content into
   `claude-catalog/docs/`.
10. **Standard sections present:** `## Role`, ideally `## Output format`,
    `## What you always do`, `## What you never do`, `## Quality self-check
    before submitting`.

## Skills (per `skill-development` + `skill-creator`)

1. **Frontmatter required:** `name`, `description`. Recommended: `version`. This
   registry also enforces `tools: Read` and `model: haiku` (registry convention;
   do not flag).
2. **Description MUST start with "This skill should be used when…"** in third
   person. Flag any prefix like `Use to load…`, `Use when…`, `Use for…`, `Use to
   retrieve…`.
3. **Description must contain specific trigger phrases** users would say
   (concrete utterances, not "provides X guidance"). Score severity = High.
4. **Description should say when NOT to use** the skill (`Do not use…`, `Do not
   trigger when…`, scope-out clause). Flag if missing.
5. **Body in imperative form** ("Parse the frontmatter", "Validate values").
   Flag any second-person drift (`you should`, `you can`, `you must`, `you
   have`, `you need`) and any first-person drift.
6. **Length:** 1500–2000 words ideal, 5000-word hard ceiling. Body >2500 words =
   candidate for splitting into `references/`.
7. **Bundled resources** referenced from SKILL.md. N/A for flat single-file
   registries — note in summary.

## CLAUDE.md (per `claude-md-improver`)

Score across six dimensions:

| Criterion | Weight | Check |
|-----------|--------|-------|
| Commands/workflows documented | 20 | Build/test/deploy/publish commands present, copy-paste ready |
| Architecture clarity | 20 | Reader can understand structure without reading code |
| Non-obvious patterns | 15 | Gotchas, conventions, project-specific rules captured |
| Conciseness | 15 | No verbose explanations of obvious things |
| Currency | 15 | Reflects current state, not stale references |
| Actionability | 15 | Instructions executable, not vague |

Total /100. Grades: A 90+, B 70–89, C 50–69, D 30–49, F <30.
