# Spec format for build_uc_docx.py

## Contents

- Top level
- Cover and document control
- Parts, sections and annexes
- Blocks
- Inline markup
- What the builder computes
- Errors

## Top level

One JSON object. `cover`, `document_control` and `parts` are required; `annexes` and
`language` are optional.

```json
{
  "language": "en-GB",
  "cover": { },
  "document_control": { },
  "parts": [ ],
  "annexes": [ ]
}
```

`language` sets the proofing language of the whole document; the default is `en-GB`.

## Cover and document control

```json
"cover": {
  "title": "Sample Programme – Cutover runbook",
  "subtitle": "Source region (A) → Target region (B)",
  "abstract": "One or two sentences on what the document covers and its baseline.",
  "metadata": {
    "Version": "0.1", "Date": "01/01/2027", "Author": "Accenture · Migration Programme",
    "Status": "Draft for review", "Classification": "Strictly confidential"
  }
},
"document_control": {
  "revisions": [["0.1", "1 Jan 2027", "First draft; issued for review"]],
  "approvals": [["Cutover leader", "Programme", "Execution of the runbook"]],
  "conventions": ["**T** is the cutover day.", "**[TBC]** marks a value to be confirmed."]
}
```

`title` is required, `subtitle` and `abstract` are optional. All five `metadata` keys are
required. `revisions` rows have three cells, `approvals` rows three cells.

## Parts, sections and annexes

```json
"parts": [
  {
    "label": "Framework",
    "sections": [
      {
        "title": "Purpose, scope and related documents",
        "blocks": [],
        "subsections": [
          {"title": "Purpose", "blocks": [{"type": "paragraph", "text": "..."}]}
        ]
      }
    ]
  }
],
"annexes": [
  {"title": "Glossary and sources", "blocks": [], "subsections": []}
]
```

A part `label` is written without its number: `Framework` becomes `PART I: FRAMEWORK`. A
section `title` is written without its number: the builder numbers sections across all
parts, subsections within their section, annexes by letter. A section's own `blocks` render
before its first subsection.

## Blocks

| `type` | Keys | Renders as |
|---|---|---|
| `paragraph` | `text` | body paragraph |
| `bullets` | `items` | bullet list; a nested list inside `items` is a second level |
| `table` | `columns`, `rows`, optional `size`, `widths_cm`, `first_column_bold` | template table |
| `note` | `text` | paragraph opening with a bold `Note.` |
| `legend` | `text` | 9 pt grey line, for a key under a table |

Table keys:

- `columns`: the header cells, exact text.
- `rows`: a list of rows; each row has exactly one cell per column. A cell is a string, or a
  list of strings for several paragraphs in one cell.
- `size`: `compact` (default, 8.5 pt) or `standard` (10 pt).
- `widths_cm`: optional, one value per column; scaled to the content width when the sum
  differs. Omit it to size columns from their content.
- `first_column_bold`: `true` for identifier, label or term columns.

```json
{"type": "table", "first_column_bold": true,
 "columns": ["ID", "Activity", "Why it is done", "Owner (role)", "Exit check · evidence"],
 "rows": [["N1", "Freeze inbound traffic [Proposed]", "No write reaches the source", "Cutover leader", "Traffic at zero"]]}
```

## Inline markup

Valid in every text: paragraphs, bullets, notes, legends, table cells and cover fields.

- `**text**` renders bold.
- `[TBC]` and `[Proposed]` render bold in the accent red. Inside `**...**` they render bold
  black, which is how the Conventions bullets define them.

Nothing else is parsed. Write `→`, `·` and `–` as characters; never an em dash.

## What the builder computes

- Section, subsection and annex numbers, and the Part labels with roman numerals.
- The TOC field and its pre-rendered entries, so a preview shows the outline before Word
  updates the field with page numbers.
- Page breaks before Document control, Contents and every Part label.
- Column widths, when `widths_cm` is absent: each column first gets room for its longest
  word, the rest is shared by average content length.
- Document properties: title from the cover, author from the metadata.

## Errors

The builder exits 1 with `invalid spec:` and the reason when a required key is missing, a
row has the wrong number of cells, `widths_cm` does not match the columns, `size` is not
`standard` or `compact`, a block `type` is unknown, or the columns cannot fit the page at
their minimum width.
