# Phase 1 — Output layout & frontmatter contract

> Reference doc for `functional-analysis-supervisor`. Read at runtime when planning where workers write their outputs and what frontmatter / per-item ID schema every artefact must carry.

## Output root

All outputs go under `<repo>/docs/analysis/01-functional/`. This directory is the single writable location for sub-agents. Layout:

```
docs/analysis/01-functional/
├── README.md                    (you — index/navigation; lists the
│                                 feature narrative as the first read)
├── 00-context.md                (you — system summary, scope, sources)
├── 00b-feature-narrative.md     (you — HUMAN-READABLE ENTRY POINT;
│                                 feature-by-feature chapters in plain
│                                 prose. ALWAYS the first technical
│                                 document a reviewer reads. Slotted
│                                 between 00- and 01- so existing
│                                 numbering is preserved.)
├── 01-actors.md                 (actor-feature-mapper)
├── 02-features.md               (actor-feature-mapper)
├── 03-ui-map.md                 (ui-surface-analyst)
├── 04-screens/                  (ui-surface-analyst — one file per screen)
│   ├── README.md
│   └── S-NN-<slug>.md
├── 05-component-tree.md         (ui-surface-analyst)
├── 06-use-cases/                (user-flow-analyst — one file per UC)
│   ├── README.md
│   └── UC-NN-<slug>.md
├── 07-user-flows.md             (user-flow-analyst)
├── 08-sequence-diagrams.md      (user-flow-analyst — Mermaid embedded)
├── 09-inputs.md                 (io-catalog-analyst)
├── 10-outputs.md                (io-catalog-analyst)
├── 11-transformations.md        (io-catalog-analyst)
├── 12-implicit-logic.md         (implicit-logic-analyst)
├── 13-traceability.md           (you — generated mechanically from IDs)
├── 14-unresolved-questions.md   (you — aggregated, single file)
├── normalized/                  (JSONL machine-readable artifacts)
├── raw/                         (per-agent raw JSONL before normalization)
├── final/                       (analysis-quality-summary.md after auditor)
├── _meta/
│   ├── manifest.json                       (run history, iterations, status)
│   ├── iteration-log.jsonl                 (one record per iteration with
│   │                                        the captured user delta)
│   ├── phase-verification-report.md        (HITL gate document — see
│   │                                        ../refactoring-workflow/
│   │                                        phase-verification-report.md)
│   ├── snapshots/                          (per-iteration snapshots, written
│   │   └── iter-<K>/                        before overwrite to support
│   │       └── ...                          rollback and diff-vs-prior)
│   ├── challenger-report.md                (challenger — opt-in)
│   └── functional-traceability-report.md   (functional-traceability-auditor)
└── _exports/
    ├── 01-functional-report.pdf  (document-creator — Accenture-branded;
    │                              regenerated only on `approve`)
    └── 01-functional-deck.pptx   (presentation-creator — Accenture-branded;
                                   regenerated only on `approve`)
```

> **Layout note (v3)**. The narrative file is added at slot
> `00b-feature-narrative.md` — between `00-context.md` and `01-actors.md`
> — so the existing numbering of all downstream artifacts is preserved.
> Other agents (baseline-testing, refactoring-tobe, ...) that reference
> the Phase 1 outputs by file name keep working unchanged. The README
> always lists the narrative as the first technical document to read,
> regardless of its file-system position.

## The feature narrative — `00b-feature-narrative.md`

This file is written by the supervisor in Wave 3c (synthesis, supervisor
only). It is the **first technical document a human reviewer reads**.
It is plain prose, organised into one chapter per major feature.

Required structure:

```markdown
---
agent: functional-analysis-supervisor
generated: <ISO-8601>
iteration: <K>
status: complete | partial
audience: human-reviewer
purpose: feature-by-feature narrative of what the application does
---

# What the application does — feature narrative

> One short paragraph (3–5 sentences) describing the application in
> business terms, derived from `00-context.md` + the feature catalogue.
> No jargon, no technology names unless essential. The reader should
> finish this paragraph with a working mental model of what the app
> is for.

## Reading order

This document is the entry point for human review. Each chapter below
describes one feature of the application in plain prose. The
structured catalogue (`02-features.md`), the use-case detail
(`06-use-cases/`), and the UI map (`03-ui-map.md`) provide the
machine-readable views and cross-link back into this narrative.

## Feature <F-NN-slug>: <Feature title>

**What it is.** 2–4 sentences in plain prose: what this feature does
for the user, in the user's own terms. No code, no class names.

**Who uses it.** Which actors trigger or consume this feature
(reference A-NN actors). Brief — one sentence.

**When and why.** What triggers the feature in normal operation, and
the business reason it exists. 1–2 sentences.

**What happens.** A short story-form walkthrough: the user does X →
the app does Y → the user sees Z. 4–8 sentences. Reference UC-NN
flows by ID but tell the story in prose; do not paste the UC.

**What the user sees.** Reference the screen(s) by S-NN. One sentence
on the visible artifacts (a form, a chart, a table, a notification).

**Outputs and side effects.** Reference IN-NN / OUT-NN / TR-NN where
relevant. State plainly what the app produces or changes as a result
of the feature (a record in DB, an email sent, a file generated).

**Open questions.** If any UC inside this feature is `candidate_not_
confirmed` or has open questions, list them here as a 1-line bullet
each. Do NOT hide them — the reviewer must see uncertainty inline.

## Feature <F-NN-slug-2>: ...

...

## Cross-feature notes

Anything that cuts across features and would otherwise be missed by
reading them in isolation: shared state, ordering constraints,
shared validation rules.

## Reading paths for technical reviewers

A short closing section pointing technical reviewers to the
structured artifacts they want next:

- Use-case detail per feature → `06-use-cases/`
- Screen-by-screen UI → `04-screens/`
- Implicit logic and validations → `12-implicit-logic.md`
- I/O catalogue → `09-inputs.md` / `10-outputs.md`
- Traceability matrix → `13-traceability.md`
```

Hard rules on the narrative:

- **One chapter per `F-NN` in the feature catalogue.** Features that
  are too thin to deserve a chapter on their own should be grouped
  under a parent chapter, with the grouped IDs cited.
- **Plain prose only.** No bullet lists for the main narrative
  (bullets allowed for "What the user sees" and "Open questions"
  subsections only). No code blocks. No Mermaid (Mermaid lives in
  `08-sequence-diagrams.md`).
- **Reference IDs, do not duplicate content.** Each chapter cites
  UC-NN, S-NN, A-NN, IN-NN, OUT-NN by ID and links into the
  structured artifacts. The narrative tells the story; the
  structured artifacts hold the detail.
- **Open questions are visible inline.** A feature with unresolved
  questions makes those questions visible in its own chapter — the
  reviewer must not have to cross-read `14-unresolved-questions.md`
  to discover them.
- **Audience is "engaged business stakeholder" or "incoming dev".**
  A reader with no exposure to the codebase should be able to
  understand what the application does after reading this file
  alone.

The narrative is the audience-facing complement to the use-case
catalogue. The use cases are precise but dry; the narrative is
human and lossy. The pair gives both views.

Reference `docs/functional-analysis/normalized-output-schema.md` for JSONL schemas.

Sub-agents must not write outside `docs/analysis/01-functional/`. Verify after each dispatch by listing modified files.

## Normalized JSONL artifacts

For full schemas of the JSONL files in `normalized/` and `raw/`, see [`normalized-output-schema.md`](../../docs/functional-analysis/normalized-output-schema.md).

Key schemas in brief:

**use-case-candidates.jsonl** — one record per use case:
- `uc_id`, `title`, `status` (confirmed | candidate_not_confirmed | requires_human_confirmation)
- `actors`, `trigger`, `main_flow`, `alternative_flows`, `business_rules`
- `evidence_ids` (required — must cite EV-NNNNNN from evidence-ledger.jsonl)
- `source_confidence` (high | medium | low), `inference_level` (direct | derived | speculative)
- `unknowns` (open questions)

**functional-gaps.jsonl** — one record per gap:
- `gap_id`, `category`, `description`, `blocking` (bool), `source_agent`

## Frontmatter contract (every output)

Every markdown file written by sub-agents has YAML frontmatter:

```yaml
---
agent: <sub-agent-name>
generated: <ISO-8601 timestamp>
sources:
  - .indexing-kb/<path>#<anchor-or-line>
  - <repo>/<source-path>:<line>   # only if implicit-logic-analyst
confidence: high | medium | low
status: complete | partial | needs-review | blocked
---
```

For deliverables containing items with stable IDs (actors, features, screens, use cases, inputs, outputs, transformations, implicit-logic items), each item has its own per-item frontmatter or YAML header:

```yaml
id: A-01 | F-01 | S-01 | UC-01 | IN-01 | OUT-01 | TR-01 | IL-01
title: <human title>
related: [<other-ids>]
sources: [<.indexing-kb/... or repo/...:line>]
status: draft | needs-review | blocked
```

The traceability matrix (`13-traceability.md`) is generated by the supervisor from these IDs after Wave 2 completes.

## Manifest schema (`_meta/manifest.json`)

After every wave, the supervisor updates `docs/analysis/01-functional/_meta/manifest.json`:

```json
{
  "schema_version": "1.0",
  "supervisor_version": "0.1.0",
  "repo_root": "<abs-path>",
  "kb_source": "<abs-path>/.indexing-kb/",
  "stack_mode": "streamlit | generic | hybrid",
  "challenger_enabled": true,
  "exports_policy": "overwrite | keep | rename",
  "resume_mode": "fresh | resume-incomplete | exports-only | full-rerun",
  "scope_filter": null,
  "runs": [
    {
      "run_id": "<ISO-8601>",
      "waves": [
        {
          "wave": 1,
          "agents": ["actor-feature-mapper", "ui-surface-analyst", "io-catalog-analyst"],
          "started": "<ISO-8601>",
          "completed": "<ISO-8601>",
          "outputs": ["<paths>"],
          "status": "complete | partial | failed",
          "open_questions_count": 0
        }
      ]
    }
  ]
}
```

If the file does not exist, create it. Append to `runs` for resumed sessions.
