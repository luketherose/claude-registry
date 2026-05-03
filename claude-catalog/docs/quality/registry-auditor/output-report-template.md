# Output report template

> Reference doc for `registry-auditor`. Read at runtime when synthesising the
> final Markdown report (Step 6 of the workflow).

The audit produces a single Markdown document printed to stdout — never written
to disk. Be terse, use tables, cite file paths as absolute paths so the
maintainer can navigate directly. Keep the full report under ~800 lines.

## Skeleton

```markdown
# Registry Audit — Anthropic Rubric

## Methodology notes
- Rubrics resolved from: <list of file paths or "embedded fallback">
- Inventory: <N> agents, <M> skills, <K> CLAUDE.md
- Date: <YYYY-MM-DD>

## Overall scores
| Area | Grade | One-line justification |
|---|---|---|
| Agents | <A–F> | … |
| Skills | <A–F> | … |
| CLAUDE.md | <score>/100 | … |

## Agents — registry-wide patterns
| # | Pattern | Files affected | Severity |
|---|---|---|---|
| A1 | … | n / total | High/Med/Low |

## Agents — top 10 to rewrite
| # | File | Problem | Concrete fix |
|---|---|---|---|

## Agents — reference templates (well-written)
- `<path>` — <why it works>

## Skills — registry-wide patterns
| # | Pattern | Files affected | Severity |

## Skills — top 10 to rewrite
| # | File | Problem | Concrete fix |

## Skills — word-count outliers
| Rank | File | Words | Action |

## Skills — reference templates (well-written)

## CLAUDE.md — score breakdown
| Criterion | Score | Evidence |

## Quick wins (script-able bulk fixes)
1. …
2. …

## Top 5 actions ordered by ROI
1. …
```

## Section requirements

- **Methodology notes** — list every rubric file actually read (or "embedded
  fallback" if missing). Record the inventory counts as resolved by `find`, not
  the user's estimate.
- **Overall scores** — one row per area; the justification is one line, not a
  paragraph.
- **Registry-wide patterns** — defects shared across many files. Cite the rubric
  criterion behind each pattern. `Files affected` = count over total.
- **Top 10 to rewrite** — per-file defects, ranked by ROI. Each row carries a
  concrete fix the maintainer can apply, not a generic recommendation.
- **Reference templates** — at least 3 well-written agents and 3 well-written
  skills, with a one-line note on what makes them work. A top-10-to-rewrite list
  without "what good looks like" is not actionable.
- **Word-count outliers** (skills only) — top 5 longest bodies and whether they
  warrant splitting into `references/`.
- **CLAUDE.md score breakdown** — one row per dimension with one or two sentences
  of evidence each. Total /100.
- **Quick wins** — only mechanical, script-able sweeps (sed/grep across the
  corpus). If a fix needs case-by-case judgement, it belongs in "top 10", not
  here.
- **Top 5 actions ordered by ROI** — closing section. Do not append a final
  summary after it.

## Style invariants

- Cite file paths as absolute paths (`/Users/.../claude-catalog/agents/...`) so
  the maintainer can `cmd-click` to open them.
- Cite the specific rubric criterion behind each finding (e.g.,
  "agent-development §6", "skill-development §2").
- Distinguish corpus-wide patterns from per-file defects in the output structure
  — never collapse them into one table.
- Do NOT produce a per-file table for all 75+ agents. Aggregate first; surface
  outliers second.
