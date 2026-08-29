# File-writing rule — `user-flow-analyst`

> Reference doc for `user-flow-analyst`. Read once at session start; the
> rule is non-negotiable for every file emitted.

All file content output (Markdown with Mermaid sequence diagrams) MUST be
written through the `Write` tool. Never use `Bash` heredocs
(`cat <<EOF > file`), echo redirects (`echo ... > file`),
`printf > file`, `tee file`, or any other shell-based content generation.

Mermaid syntax (`A[label]`, `B{cond?}`, `A --> B`,
`Actor->>System: msg`) contains shell metacharacters (`[`, `{`, `}`,
`>`, `<`, `*`, `&`) that the shell interprets as redirection, glob
expansion, or word splitting — even inside quotes (Git Bash / MSYS2 on
Windows is especially fragile). A malformed heredoc produced 48 garbage
files in a repo root in the Phase 2 incident of 2026-04-28.

Use `Write` to create files, `Edit` to modify. Bash is allowed only for
read-only inspection. No third path.
