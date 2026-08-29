# Authoring constraints: the full page-writing checklist

> Reference doc for `wiki-writer`. Read at runtime before Phase 3 (page
> authoring) and again during Phase 4 (quality gate). The agent body carries
> the three constraints that are hard boundaries on where output may go; the
> full content checklist lives here. Every item below is binding.

## Accuracy

- **Verify before writing**. File paths, commands, function names, and config
  keys are checked against the codebase. Never trust the README blindly.
  READMEs drift.
- **Do not invent**. If a fact is not findable, mark the section with
  `> _Needs verification_` and list it in the final summary's `Stale` block.
- **Examples must run**. A code block that does not work is worse than no
  example.

## Structure

- **Do not duplicate the README in full**. The wiki extends the README; it does
  not replace it. Cross-link instead.
- **One topic per page**. If a page covers two unrelated topics, split it.
- **Stable IDs**: use a `<page-slug>` matching GitHub wiki URL slug rules
  (CamelCase or `Hyphenated-Words`, no spaces). GitHub auto-generates the URL
  from the filename.
- **Reference Diataxis explicitly** in the content plan presented to the user,
  so they can challenge the categorization.

## Tone

- **Active voice, present tense, no marketing**. "The script installs
  capabilities" not "Capabilities can be installed by users".
- **Audience-aware tone**: end-user pages avoid implementation jargon;
  contributor pages may assume code familiarity.
- **No emojis** unless the project's existing docs use them consistently.
- **No AI credits** (no "Generated with Claude") in the wiki itself.
