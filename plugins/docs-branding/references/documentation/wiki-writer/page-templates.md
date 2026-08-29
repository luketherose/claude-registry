# Wiki page templates

> Reference doc for `wiki-writer`. Read at runtime when authoring the
> canonical page set, the global navigation files, or the per-page front
> matter. Contains boilerplate only — decision logic on which pages to
> author lives in the agent body (`## Method`).

## Diataxis quadrants

Organize pages around the **Diataxis framework**:

| Quadrant | Goal | Examples |
|---|---|---|
| **Tutorials** | Learn by doing — hand-holding | "Your first capability", "Set up the registry locally" |
| **How-to guides** | Solve a specific problem | "How to publish a capability", "How to write a skill" |
| **Reference** | Look up facts | "Capability schema", "CLI reference", "Catalog manifest format" |
| **Explanation** | Understand the design | "Why catalog vs marketplace", "Versioning policy", "Subagent dispatch model" |

## Canonical page set

Wikis with mixed audiences benefit from this canonical page set:

```
Home                       — landing page with TL;DR + quick links + sidebar overview
What-is-this               — one-page explanation (Explanation)
Quick-start                — install + verify in 5 minutes (Tutorial)
Installation               — full procedure with prerequisites (How-to)
Usage                      — common workflows, with examples (How-to)
Architecture               — diagrams, components, data flow (Explanation)
Reference                  — schemas, CLI flags, configuration keys (Reference)
Contributing               — how to propose changes, test, and submit (How-to)
FAQ                        — common questions and gotchas
Changelog                  — link to or excerpt of the project changelog
_Sidebar                   — navigation (controls every page's left rail)
_Footer                    — footer (license, version, edit-on-GitHub link)
```

Adapt this list to the project: small projects collapse pages
(Quick-start + Installation), large projects split (one Reference page
per subsystem).

## `_Sidebar.md` template

GitHub wikis use `_Sidebar.md` and `_Footer.md` as global navigation.
Both are markdown files; `_Sidebar.md` appears on the right rail, not
the left, despite the name (GitHub convention).

```markdown
**[Home](Home)**

### Get started
- [What is this](What-is-this)
- [Quick start](Quick-start)
- [Installation](Installation)

### Use
- [Usage](Usage)
- [Reference](Reference)
- [FAQ](FAQ)

### Understand
- [Architecture](Architecture)
- [Decisions (ADRs)](Decisions)

### Contribute
- [Contributing](Contributing)
- [Changelog](Changelog)
```

## `_Footer.md` template

One line is fine:

```markdown
[License](https://github.com/<owner>/<repo>/blob/main/LICENSE) ·
[Edit on GitHub](https://github.com/<owner>/<repo>/edit/main/<page>) ·
v<release>
```

Write the sidebar and footer **before any content page**. They drive
consistency.

## Per-page contract

For each page, follow this contract:

1. **First sentence states the page's purpose**: "This page explains X."
   No throat-clearing.
2. **Above-the-fold TL;DR**: 2-4 lines; reader can stop here and have
   the gist.
3. **Working examples**: every command must run as-is; every code
   block must be copy-pasteable. Test them.
4. **Cross-links**: every reference to another concept links to its
   page. No floating jargon.
5. **Verified facts only**: file paths, function names, flags, env
   vars must match the codebase. Use Grep/Read to verify.
6. **Front matter**: top of every page, an HTML comment with metadata
   (see template below).

## Page front-matter template

Top of every page, an HTML comment with metadata:

```html
<!--
audience: end-user | contributor | operator | integrator | mixed
diataxis: tutorial | how-to | reference | explanation
last-verified: 2026-04-28
verified-against: <commit-sha>
-->
```

The metadata is invisible in rendered GitHub but enables future audits
("which pages are stale?").

## Final-summary template

After writing all pages, post this summary:

```
Wiki authored — <N> pages, <M> sidebar entries.

Output:    <repo>/wiki/
Pages:     [list with page name → audience → diataxis quadrant]
Pending:   [internal/external links flagged for human review]
Stale:     [pages that depend on a part of the codebase you couldn't
            verify — listed in last-verified comments]

Next step: open a PR with the wiki/ folder; on merge, run
`git clone <wiki-url> /tmp/wiki && cp -r wiki/*.md /tmp/wiki/ &&
cd /tmp/wiki && git add -A && git commit -m "Sync wiki" && git push`.
DO NOT push from this agent — pushing the wiki is a separate user
action requiring explicit authorization.
```
