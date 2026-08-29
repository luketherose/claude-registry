# Output rules — file-writing and push policy

> Reference doc for `wiki-writer`. Read at runtime when about to write
> Markdown files or push to the wiki remote. These rules are
> non-negotiable; the agent body's decision logic still drives **when**
> to write and push.

## File-writing rule (non-negotiable)

All Markdown content output MUST be written through the `Write` tool
(or `Edit` for in-place changes). Never use `Bash` heredocs
(`cat <<EOF > file`), echo redirects (`echo ... > file`),
`printf > file`, `tee file`, or any other shell-based content
generation. Markdown content with code fences, sidebars, and tables
contains shell metacharacters (`[`, `{`, `}`, `>`, `<`, `*`, `;`, `&`,
`|`) that the shell interprets as redirection, glob expansion, or
word splitting — even inside quotes (Git Bash / MSYS2 on Windows is
especially fragile).

Allowed Bash usage: read-only inspection (`grep`, `find`, `ls`, `wc`,
`git log`, `git status`, `git remote`), cloning a wiki repo for
inspection (`git clone --depth 1 <wiki-url> /tmp/...`), creating
empty directories (`mkdir -p`). Forbidden: any command that writes
file content from a string, variable, template, heredoc, or piped
input. Use `Write` to create, `Edit` to modify. No third path.

## Push policy (non-negotiable)

You **never push to the wiki remote** without explicit user
authorization in the same session. The wiki is a public-facing
artifact; an accidental force-push or wrong-content push is hard to
revert and visible to all consumers.

The intended flow is:

1. You write `<repo>/wiki/*.md`.
2. The user opens a PR against the main repo, with reviewers.
3. After PR merge, the user (or a CI job they configure) runs the
   sync command in the final summary.

If the user explicitly says "push the wiki now", you may run the
clone-copy-commit-push sequence — but only after re-stating the
target URL and getting one final confirmation.

## Quality-gate checklist

Run, in this order, before declaring done:

1. **Internal-link check**: no broken `[text](Page-Name)` anywhere.
2. **External-link sanity**: `WebFetch` HEAD-style check on any link
   to a public URL added by you (skip auth-walled URLs).
3. **Code-block dry run**: every shell snippet runs in a clean shell.
   For language samples (Python, Java, etc.), at minimum lint-check
   syntax.
4. **Audience tag coverage**: every page has the front-matter block
   (see `page-templates.md`).
5. **Sidebar coverage**: every published page is reachable from
   `_Sidebar.md` in ≤ 2 clicks from `Home`.
6. **No duplication with the README**: if a section duplicates the
   README, replace it with a one-sentence link to the README anchor.
