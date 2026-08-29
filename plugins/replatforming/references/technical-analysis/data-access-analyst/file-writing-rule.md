# Data-access analyst — file-writing rule (non-negotiable)

> Reference doc for `data-access-analyst`. Read once before producing any
> output file. The rule is non-negotiable: the agent body summarises it
> in one sentence and points here for the rationale.

## Rule

All file content output (Markdown, JSON, CSV, YAML, source code) MUST be
written through the `Write` tool. Never use `Bash` heredocs
(`cat <<EOF > file`), echo redirects (`echo ... > file`), `printf > file`,
`tee file`, or any other shell-based content generation.

## Why

Content with Mermaid syntax (`A[label]`, `B{cond?}`, `A --> B`),
fenced code blocks, or YAML/JSON with special characters contains shell
metacharacters (`[`, `{`, `}`, `>`, `<`, `*`, `;`, `&`, `|`) that the
shell interprets as redirection, glob expansion, or word splitting — even
inside quotes when the quoting is fragile (Git Bash / MSYS2 on Windows is
especially prone). A malformed heredoc produced 48 garbage files in a
repo root in the Phase 2 incident of 2026-04-28; one of them captured the
output of an unrelated `store` command found on `$PATH`. The
`data-flow-diagram.md` Mermaid output is the highest-risk artifact in
this agent — write it via `Write`, never via `Bash`.

## Allowed Bash usage

Read-only inspection (`grep`, `find`, `ls`, `wc`, small `cat` of known
files, `git log`, `git status`), running existing scripts, creating empty
directories (`mkdir -p`).

## Forbidden Bash usage

Any command that writes file content from a string, variable, template,
heredoc, or piped input.

## Decision tree

- Need to produce a new file → `Write`.
- Need a small change to an existing file → `Edit`.
- No third path.
