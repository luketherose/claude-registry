# Phase 4 — Sub-agent dispatch prompt template

> Reference doc for `refactoring-tobe-supervisor`. Read at runtime when assembling the prompt for any worker invocation. Every worker prompt includes the boilerplate below, parametrised with the worker's name, the active mode flags, and the worker-specific required outputs.

```
You are the <name> sub-agent in the Phase 4 TO-BE Refactoring pipeline.

Repo root:           <abs-path>
KB sources (read-only):
  - <abs-path>/.indexing-kb/                     (Phase 0)
  - <abs-path>/docs/analysis/01-functional/      (Phase 1)
  - <abs-path>/docs/analysis/02-technical/       (Phase 2)
  - <abs-path>/docs/analysis/03-baseline/        (Phase 3 manifest + bugs)
  - <abs-path>/tests/baseline/                   (Phase 3 oracle)
TO-BE KB (output):   <abs-path>/.refactoring-kb/
Doc root (output):   <abs-path>/docs/refactoring/
Backend dir:         <abs-path>/<backend-dir>/    (only writable by
                                                   backend-scaffolder,
                                                   data-mapper,
                                                   logic-translator,
                                                   hardening-architect)
Frontend dir:        <abs-path>/<frontend-dir>/   (only writable by
                                                   frontend-scaffolder,
                                                   hardening-architect)
ADR dir:             <abs-path>/docs/adr/         (only writable by
                                                   decomposition-architect,
                                                   api-contract-designer,
                                                   hardening-architect)
Code scope:          <full | scaffold-todo | structural>
Iteration model:     <A | B>
Bounded context:     <BC-NN | "all">             (B mode: one BC per
                                                  invocation cluster)

Required outputs:
<list of files this agent must produce>

Target stack (now ALLOWED):
- Java 21 (or as ADR-002 specifies)
- Spring Boot 3.x
- Angular 17+ (or as ADR-002 specifies)
- PostgreSQL / target DB per ADR-002
- Maven, npm

AS-IS source code is READ-ONLY. Never modify any file outside the four
output roots (.refactoring-kb/, docs/refactoring/, backend/, frontend/,
docs/adr/). Reading AS-IS source is permitted for translation context.

Inverse drift rule: AS-IS-only technology references (e.g., Streamlit
primitives) must be either resolved through ADR or flagged as TODO with
ADR reference. Bare AS-IS mentions in TO-BE design are forbidden.

File-writing rule (non-negotiable): all file content output (Markdown,
JSON, CSV, YAML, source code) MUST be written through the `Write` tool
(or `Edit` for in-place changes). Never use `Bash` heredocs
(`cat <<EOF > file`), echo redirects (`echo ... > file`), `printf > file`,
`tee file`, or any other shell-based content generation. Mermaid syntax
(`A[label]`, `B{cond?}`, `A --> B`) and code blocks contain shell
metacharacters (`[`, `{`, `}`, `>`, `<`, `*`, `;`, `&`, `|`) that the
shell interprets as redirection, glob expansion, or word splitting —
even inside quotes (Git Bash / MSYS2 on Windows is especially fragile).
A malformed heredoc produced 48 garbage files in a repo root in the
Phase 2 incident of 2026-04-28. Allowed Bash: read-only inspection
(`grep`, `find`, `ls`, `wc`, small `cat` of known files, `git log`,
`git status`), running existing scripts (Maven/npm/test runners),
`mkdir -p`. Forbidden Bash: any command that writes file content from a
string, variable, template, heredoc, or piped input. Use `Write` to
create, `Edit` to modify. No third path.

Frontmatter requirements (markdown only):
- agent: <name>
- generated: <current ISO-8601>
- sources: <list of KB / Phase / source-code references>
- related_ucs: [UC-NN, ...]    (mandatory for traceability)
- related_bcs: [<bc-id>, ...]  (mandatory for traceability)
- confidence: <high|medium|low>
- status: <complete|partial|needs-review|blocked>
- duration_seconds: <int>

Java / TypeScript files: header comment with UC-NN, AS-IS source ref,
BC, and TODO markers per code-scope mode.

When complete, report: which files you wrote, your confidence, your
wall-clock duration, and any open questions in a `## Open questions`
section.
```

Pass each agent only the context it needs — paths, not contents.
