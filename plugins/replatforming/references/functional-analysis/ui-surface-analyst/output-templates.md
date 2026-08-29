# Output file shapes — `ui-surface-analyst`

> Reference doc for `ui-surface-analyst`. Read at runtime when writing the
> four output files in Wave 1.

This doc fixes the file layout, frontmatter, and section order for the
files the agent emits. Independently readable: every reference back to
the agent body is by ID convention only (S-NN, IN-NN, OUT-NN, TR-NN,
A-NN, F-NN).

All file content output (Markdown with Mermaid diagrams) MUST be written
through the `Write` tool. See § File-writing rule in the agent body.

---

## File 1 — `docs/analysis/01-functional/03-ui-map.md`

```markdown
---
agent: ui-surface-analyst
generated: <ISO-8601>
sources:
  - .indexing-kb/05-streamlit/pages.md       # if applicable
  - .indexing-kb/01-overview.md
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# UI map

## Summary
- UI mode: streamlit-multipage | streamlit-monolithic | web-templated | cli | none
- Screens: <N>
- Navigation edges: <N>
- Cross-screen state keys: <N>  # streamlit-only

## Entrypoint
- Screen: S-01 (<name>)
- File: <path>
- Layout: <e.g., wide / centered / sidebar-on-left>

## Navigation graph

\`\`\`mermaid
graph LR
    S-01[Home] --> S-02[Dashboard]
    S-02 --> S-03[Reports]
    S-02 -.reactive.-> S-04[Detail view]
    S-03 --> S-05[Export]
\`\`\`

Legend:
- solid arrow: explicit navigation (link, st.switch_page, route)
- dotted arrow with `reactive` label: state-driven logical transition
  (no page change, but rendered content changes substantially)

## Cross-screen state (Streamlit only)

| State key | Read in | Written in | Role |
|---|---|---|---|
| `current_dataset` | S-02, S-03, S-05 | S-01 | shared selection |
| `step` | S-04 | S-04 | wizard step toggle |

## Open questions
- <e.g., "Page `pages/3_Admin.py` is in the directory but does not appear
  in any navigation; is it accessed via direct URL?">
```

---

## File 2 — `docs/analysis/01-functional/04-screens/README.md`

```markdown
# Screens index

| ID | Name | File | Type | Actors |
|---|---|---|---|---|
| S-01 | Home | app.py | landing | A-01 |
| S-02 | Dashboard | pages/1_Dashboard.py | overview | A-01, A-02 |
| ... |
```

---

## File 3 (per screen) — `docs/analysis/01-functional/04-screens/S-NN-<slug>.md`

```markdown
---
agent: ui-surface-analyst
generated: <ISO-8601>
sources:
  - <file path>
  - .indexing-kb/05-streamlit/pages.md       # if applicable
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
id: S-02
title: "Dashboard"
related:
  features: [F-01, F-03]
  actors: [A-01, A-02]
---

# S-02 — Dashboard

## Purpose
<1-2 sentences in plain language>

## Layout
<short description: sidebar left, 2-column main area, etc.>

## Component tree

\`\`\`
Page: Dashboard
├── Sidebar
│   ├── selectbox  key=dataset_choice  options=[<dynamic>]
│   └── button     label="Refresh"     on_click=refresh_data
├── Main column 1
│   ├── metric     label="Total rows"
│   └── dataframe  data=current_df
└── Main column 2
    └── plotly_chart figure=trend_fig
\`\`\`

## Inputs (widgets receiving user input)
- `dataset_choice` (selectbox) — IN-04 in input catalog
- `refresh_data` (button) — triggers transformation TR-02

## Outputs (widgets emitting data to user)
- "Total rows" metric — OUT-01
- `current_df` dataframe — OUT-02
- `trend_fig` chart — OUT-03

## State
- Reads: `current_dataset`, `filters`
- Writes: `current_df`, `last_refresh`

## Navigation
- Reachable from: S-01 (sidebar link)
- Leads to: S-04 (reactive on row selection — see ui-map.md)

## Notes
- <anything ambiguous or noteworthy>

## Open questions
- <e.g., "the `Refresh` button has no on_click handler — what does it do?">
```

---

## File 4 — `docs/analysis/01-functional/05-component-tree.md`

```markdown
---
agent: ui-surface-analyst
generated: <ISO-8601>
sources: [<all screen files>]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# Component tree (whole application)

A high-level component tree across all screens. For per-screen detail,
see `04-screens/S-*.md`.

## Reusable components

Components used in 2+ screens (candidates for reuse documentation):

| Component pattern | Used in screens | Notes |
|---|---|---|
| sidebar dataset picker | S-02, S-03, S-05 | identical selectbox + state key |
| date range filter (two date_inputs) | S-02, S-04 | always paired |

## Custom components / raw HTML

If `st.components.v1.html(...)` or third-party Streamlit components
are used, list them here:

| Pattern | Used in | What it renders |
|---|---|---|

## Layout patterns

- 2-column main area: S-02, S-03
- 3-tab layout: S-04 only
- Sidebar-driven filter: S-02, S-03, S-05

## Open questions
```
