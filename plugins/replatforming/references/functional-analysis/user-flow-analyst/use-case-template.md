# Use-case file shape — `user-flow-analyst`

> Reference doc for `user-flow-analyst`. Read at runtime when writing UC files
> in Wave 2.

This doc fixes the file layout, frontmatter, and section order for the four
files the agent emits. Independently readable: every reference back to the
agent body is by ID convention only.

---

## File 1 — `docs/analysis/01-functional/06-use-cases/README.md`

```markdown
# Use cases index

| ID | Name | Primary actor | Features | Screens | Status |
|---|---|---|---|---|---|
| UC-01 | Sign in | A-01 | F-00 | S-00 | complete |
| UC-02 | Generate monthly report | A-01 | F-03 | S-03, S-05 | complete |
| ... |
```

---

## File 2 (per UC) — `docs/analysis/01-functional/06-use-cases/UC-NN-<slug>.md`

```markdown
---
agent: user-flow-analyst
generated: <ISO-8601>
sources:
  - docs/analysis/01-functional/02-features.md#F-03
  - docs/analysis/01-functional/04-screens/S-03-reports.md
  - .indexing-kb/07-business-logic/business-rules.md
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
id: UC-02
title: "Generate monthly report"
related:
  actors: [A-01]
  features: [F-03]
  screens: [S-03, S-05]
  transformations: [TR-01]
  inputs: [IN-01, IN-02]
  outputs: [OUT-01, OUT-03]
---

# UC-02 — Generate monthly report

## Primary actor
A-01 (End user)

## Secondary actors
- (none)

## Preconditions
- A-01 is signed in
- At least one dataset is loaded (state: `current_dataset != None`)

## Main success scenario
1. A-01 navigates to S-03 (Reports)
2. A-01 selects month (IN-01) and product filter (IN-02)
3. A-01 clicks "Generate" button
4. System validates inputs (see business-rules: month not in future)
5. System invokes TR-01
6. S-03 renders OUT-01 (table) and OUT-03 (chart)
7. A-01 navigates to S-05 (Export) to download
8. A-01 clicks "Download CSV" — produces OUT-04

## Alternate flows
- **2a. Month in future**: validation error displayed (see IL-04 for
  exact validation logic)
- **5a. No data for month**: render empty state with message (no error)

## Exceptional flows
- **TR-01 fails**: error toast displayed, S-03 remains in input state

## Postconditions
- An audit log entry is written for TR-01 (side effect)
- `current_report` session_state populated with the generated dataset

## Sequence diagram
\`\`\`mermaid
sequenceDiagram
    actor U as A-01
    participant S3 as S-03 Reports
    participant TR as TR-01
    participant State as session_state

    U->>S3: select month, filter (IN-01, IN-02)
    S3->>State: write filters
    Note over S3: rerun
    U->>S3: click Generate
    S3->>TR: invoke
    TR->>State: write current_report
    Note over S3: rerun
    S3-->>U: render OUT-01, OUT-03
    U->>S3: navigate to S-05
\`\`\`

## Notes
- The "Generate" action triggers st.rerun(); the chart re-renders only
  if `current_report` changed.
- See implicit-logic.md IL-04 for input validation specifics.

## Open questions
- <if any>
```

---

## File 3 — `docs/analysis/01-functional/07-user-flows.md`

```markdown
---
agent: user-flow-analyst
generated: <ISO-8601>
sources: [<UC files>]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# User flows

High-level narratives chaining multiple UCs into typical journeys.

## Flow 1 — Monthly reporting cycle
**Actor**: A-01

1. UC-01 — Sign in
2. UC-05 — Load latest dataset
3. UC-02 — Generate monthly report
4. UC-08 — Share report via email (if applicable)

## Flow 2 — ...

## Open questions
- <e.g., "Is the typical user expected to chain UC-02 → UC-04 → UC-08, or
  are these independent goals? KB does not document the intended journey.">
```

---

## File 4 — `docs/analysis/01-functional/08-sequence-diagrams.md`

```markdown
---
agent: user-flow-analyst
generated: <ISO-8601>
sources: [<UC files>]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# Sequence diagrams overview

Per-UC sequence diagrams live in their respective `06-use-cases/UC-*.md`
files. This document catalogs and cross-references them.

## Diagrams index

| UC | Title | Diagram type | Notes |
|---|---|---|---|
| UC-02 | Generate monthly report | reactive (Streamlit) | shows reruns |
| UC-04 | Upload dataset | reactive (Streamlit) | file upload + validation |
| ... |

## Cross-cutting patterns

### Pattern 1 — Filter → rerun → render (Streamlit-specific)
Common shape across UC-02, UC-03, UC-05.

\`\`\`mermaid
sequenceDiagram
    actor U as Actor
    participant S as Screen
    participant State as session_state

    U->>S: change filter widget
    S->>State: write filter key
    Note over S: rerun
    S-->>U: re-render with new filter applied
\`\`\`

### Pattern 2 — ...
```
