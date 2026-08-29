# Output file shapes — `io-catalog-analyst`

> Reference doc for `io-catalog-analyst`. Read at runtime when writing the
> three output files in Wave 1.

This doc fixes the file layout, frontmatter, and section order for the three
files the agent emits. Independently readable: every reference back to the
agent body is by ID convention only (IN-NN, OUT-NN, TR-NN, IL-NN).

---

## File 1 — `docs/analysis/01-functional/09-inputs.md`

```markdown
---
agent: io-catalog-analyst
generated: <ISO-8601>
sources:
  - .indexing-kb/05-streamlit/ui-patterns.md
  - .indexing-kb/06-data-flow/file-io.md
  - .indexing-kb/06-data-flow/external-apis.md
  - .indexing-kb/07-business-logic/validation-rules.md
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# Inputs catalog

## Summary
- Total inputs: <N>
- User-supplied (UI): <N>
- File uploads: <N>
- External system pushes: <N>
- Scheduled / batch: <N>
- Configuration (functional): <N>

## Input catalog

### IN-01 — <descriptive name in business language>
- **Source**: UI widget | file upload | webhook | schedule | config
- **Where**: <screen S-NN> / <endpoint> / <cron name> / <config path>
- **Type**: text | number | date | file | enum | structured
- **Validation**: required, min=0, max=100, regex=`...` (or "see IL-NN")
- **Used by**: TR-01, TR-03 (transformations)
- **Sources**:
  - .indexing-kb/05-streamlit/ui-patterns.md#dashboard-page
  - .indexing-kb/04-modules/<pkg>.md
- **Confidence**: high | medium | low
- **Notes**: <e.g., "actually a JSON blob; structure not enforced">

### IN-02 — ...

## Open questions
- <e.g., "input IN-04 is a free-text field; the parsing logic is hidden
  in transform_data() — see implicit-logic.md">
```

---

## File 2 — `docs/analysis/01-functional/10-outputs.md`

```markdown
---
agent: io-catalog-analyst
generated: <ISO-8601>
sources:
  - .indexing-kb/05-streamlit/ui-patterns.md
  - .indexing-kb/06-data-flow/file-io.md
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# Outputs catalog

## Summary
- Total outputs: <N>
- Rendered to UI: <N>
- File downloads: <N>
- External system writes: <N>
- Notifications: <N>

## Output catalog

### OUT-01 — <descriptive name>
- **Type**: ui-render | file-download | external-write | notification
- **Format**: text | dataframe | chart | csv | xlsx | pdf | json | image
- **Where**: <screen S-NN> / <endpoint> / <channel>
- **Produced by**: TR-01 (transformation)
- **Consumed by**: A-01 (actor)
- **Sources**:
  - .indexing-kb/05-streamlit/ui-patterns.md
  - .indexing-kb/04-modules/<pkg>.md
- **Confidence**: high | medium | low
- **Notes**: <e.g., "chart updates reactively when filter changes">

### OUT-02 — ...

## Open questions
- <e.g., "OUT-05 is generated only conditionally; the condition is
  unclear — see implicit-logic.md">
```

---

## File 3 — `docs/analysis/01-functional/11-transformations.md`

```markdown
---
agent: io-catalog-analyst
generated: <ISO-8601>
sources:
  - .indexing-kb/07-business-logic/business-rules.md
  - .indexing-kb/04-modules/
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# Transformation matrix

## Summary
- Total transformations: <N>
- Average inputs per transformation: <N>
- Average outputs per transformation: <N>

## Transformation catalog

### TR-01 — <verb-led name, e.g., "Generate monthly sales report">
- **Trigger**: button click S-03 "Generate" | scheduled daily 02:00 | webhook /events
- **Inputs**: IN-01, IN-02, IN-04
- **Outputs**: OUT-01, OUT-03
- **Business rules applied** (high-level):
  - validate that month is not in the future
  - exclude rows where status = 'cancelled'
  - aggregate by product family
  (full detail in .indexing-kb/07-business-logic/business-rules.md)
- **Side effects**: writes audit log entry; updates DB table `report_runs`
- **Implicit logic referenced**: IL-03 (currency conversion fallback)
- **Sources**: .indexing-kb/04-modules/reports.md
- **Confidence**: high | medium | low

### TR-02 — ...

## Cross-cutting matrix

| Input \ Output | OUT-01 | OUT-02 | OUT-03 | ... |
|---|---|---|---|---|
| IN-01 | TR-01 | — | TR-01 | ... |
| IN-02 | TR-01 | — | — | ... |
| IN-03 | — | TR-02 | — | ... |

## Orphans
- Inputs with no transformation: <list — likely dead code or doc gap>
- Outputs with no transformation: <list — same>

## Open questions
- <e.g., "TR-04 has a documented business rule about partial refunds
  but the implementation is unclear in the KB; flagged for implicit-logic-analyst">
```
