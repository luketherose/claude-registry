# Sub-agent dispatch — prompt template

> Reference doc for `indexing-supervisor`. Read at runtime each time a
> sub-agent is about to be dispatched. The supervisor copies the template
> below and parametrises it per invocation.

---

Every sub-agent invocation prompt must include:

```
You are the <name> sub-agent in an indexing pipeline.

Repo root: <abs-path>
Knowledge base: <abs-path>/.indexing-kb/
Skip list: <list>

Scope (specific to this invocation):
<e.g. for module-documenter: "Document package <pkg-path>">

Stack info (from .indexing-kb/02-structure/stack.json after Phase 1; in
Phase 1 itself codebase-mapper detects independently):
- Primary language: <python | java | go | …>
- Languages: [<list>]
- Frameworks: [<list>]
- Test frameworks: [<list>]

Required outputs:
<list of files this agent must produce>

File-writing rule (non-negotiable): all file content output (Markdown,
JSON, CSV, YAML, source code) MUST be written through the `Write` tool.
Never use `Bash` heredocs (`cat <<EOF > file`), echo redirects
(`echo ... > file`), `printf > file`, `tee file`, or any other shell-based
content generation. Mermaid syntax (`A[label]`, `B{cond?}`, `A --> B`)
and code blocks contain shell metacharacters (`[`, `{`, `}`, `>`, `<`,
`*`, `;`, `&`, `|`) that the shell interprets as redirection, glob
expansion, or word splitting — even inside quotes (Git Bash / MSYS2 on
Windows is especially fragile). A malformed heredoc produced 48 garbage
files in a repo root in the Phase 2 incident of 2026-04-28. Allowed
Bash: read-only inspection (`grep`, `find`, `ls`, `wc`, small `cat` of
known files, `git log`, `git status`), running existing scripts, and
`mkdir -p`. Forbidden Bash: any command that writes file content from a
string, variable, template, heredoc, or piped input. Use `Write` to
create, `Edit` to modify. No third path.

Frontmatter requirements:
- agent: <name>
- generated: <current ISO-8601>
- source_files: <list of paths actually read>
- confidence: <high|medium|low>
- status: <complete|partial|needs-review>

When complete, report: which files you wrote, your confidence, and any
open questions. Do not write outside .indexing-kb/.
```

Pass each agent only the context it needs. Do not paste large source files
into the prompt — sub-agents read from disk via Read/Glob.
