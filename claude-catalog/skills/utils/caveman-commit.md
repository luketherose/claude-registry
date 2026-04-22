---
description: Generates terse, intent-focused commit messages in Conventional Commits format. No emojis, no self-referential text, substance only.
---

Generate commit messages in Conventional Commits format.

## Format
`<type>(<scope>): <imperative>` — max 50 chars, hard cap 72

## Allowed types
feat, fix, refactor, perf, docs, test, chore, build, ci, style, revert

## Rules
- Imperatives only in subject
- Body only if "the why is not obvious"
- Priority to reasoning, not description
- No emojis, no attributions, no repeated file names
- No self-referential phrases ("This commit does..."), first person, AI credits

## Body required for
- Breaking changes
- Security fixes
- Data migrations
- Reverts
- Non-obvious reasoning

## Output
Only the message text in a code block. Do not run git, do not stage.

---

**See also**: `/utils/caveman` for general terse communication · `/utils/caveman-review` for one-line code review

---

$ARGUMENTS
