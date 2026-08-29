# File-writing rule — rationale

> Reference doc for `state-runtime-analyst`. Read on demand if a contributor
> questions why the agent forbids `Bash` heredocs / redirects for file output.
> The rule itself lives in the agent body (`## File-writing rule`); only the
> background reasoning is here.

## Why `Write` only, never `Bash` redirects

Content with Mermaid syntax (`A[label]`, `B{cond?}`, `A --> B`), fenced code
blocks, or YAML/JSON with special characters contains shell metacharacters
(`[`, `{`, `}`, `>`, `<`, `*`, `;`, `&`, `|`) that the shell interprets as
redirection, glob expansion, or word splitting — even inside quotes when the
quoting is fragile (Git Bash / MSYS2 on Windows is especially prone).

A malformed heredoc produced 48 garbage files in a repo root in the Phase 2
incident of 2026-04-28; one of them captured the output of an unrelated
`store` command found on `$PATH`. The `state-flow-diagram.md` Mermaid output
is the highest-risk artifact in this agent — write it via `Write`, never via
`Bash`.

## Allowed vs forbidden Bash usage

- **Allowed**: read-only inspection (`grep`, `find`, `ls`, `wc`, small `cat`
  of known files, `git log`, `git status`), running existing scripts,
  creating empty directories (`mkdir -p`).
- **Forbidden**: any command that writes file content from a string,
  variable, template, heredoc, or piped input.

If you need to produce a file, use `Write`. If a file already exists and
needs a small change, use `Edit`. No third path.
