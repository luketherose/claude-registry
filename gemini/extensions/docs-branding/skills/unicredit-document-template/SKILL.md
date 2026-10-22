---
name: unicredit-document-template
description: "This skill should be used when producing, restyling or checking a Word (.docx) document written for UniCredit: runbooks, cutover plans, design documents, procedures, assessments, plans. It defines the UniCredit document template measured from a reference UniCredit runbook: page setup, Arial type scale, the five-colour palette, cover page with logo and metadata table, document control (revision history, approval, conventions), the mandatory table of contents, PART labels, numbered sections, table design and the tables every document must carry. Ships a JSON-to-DOCX builder and a checker that reports what a reader will see. Trigger phrases: \"documento UniCredit\", \"template UniCredit\", \"runbook per UniCredit in Word\", \"UC document template\", \"format this docx the UniCredit way\". Do not use for UniCredit web or app UI (use unicredit-design-system) or for Accenture-branded deliverables (use accenture-branding)."
---

# UniCredit document template

The template is measured, not designed: every value below was read from the OOXML of a
reference UniCredit runbook (17 pages, 23 tables, Word 16). The few values the reference does
not carry are marked **added** and listed in `_added` of
[doc-tokens.json](assets/doc-tokens.json), which is the single source the scripts read. When
a value changes, change the tokens file first, then this page.

The logo is not bundled: the registry is public and the mark belongs to UniCredit. Take it
from an existing UniCredit document (`--logo-from`) or from a UniCredit-owned brand source
(`--logo`). Never redraw it.

## Workflow

1. Pick the profile, runbook or generic, in [structure.md](references/structure.md).
2. Write the content as a JSON spec, starting from
   [example-spec.json](assets/example-spec.json). The format is in
   [spec-format.md](references/spec-format.md). Section numbers, Part labels, the TOC and
   every visual value are computed: the spec holds words only.
3. Build:
   ```bash
   python3 scripts/build_uc_docx.py spec.json out.docx --logo-from <existing UniCredit .docx>
   ```
4. Check, and paste the output to the user before calling the document done:
   ```bash
   python3 scripts/check_uc_docx.py out.docx
   ```
   Zero `ERROR` is the bar. Every `WARN` is either fixed or justified in the reply.
5. Tell the user that Word asks to update fields on first open: accepting fills the TOC page
   numbers. Saving once in Word keeps them.

Escape hatch: when the user hands over an existing UniCredit `.docx` to restyle rather than a
content brief, edit it in place with python-docx following the rules below, then run the
checker on the result. Do not rebuild a document whose layout the user has tuned by hand.

Both scripts need `python3` and `python-docx`. Check before promising a file:
`python3 -c "import docx"`.

## Hard rules

1. **Arial, only Arial.** The reference declares a `UniCredit` typeface in its heading styles
   but overrides every heading run to Arial and does not embed it, so a reader never sees it.
   Do not use it: on a machine without the font Word substitutes silently.
2. **Five colours.** Nothing outside the palette below: no brand red `#E2001A`, no theme
   blue, no coloured table bands.
3. **A table of contents on its own page** after document control (added: the reference has
   none, the template requires one).
4. **No em dash** in titles, labels or prose. Part labels take a colon (`PART I: FRAMEWORK`).
   The en dash of the cover title (`<Scope> – <Document type>`) stays.
5. **Roles, not names.** People appear only in the contact annex, which the reference ships
   as a template held separately.
6. **Every `[TBC]` is listed in Open points**, and Open points is the last numbered section.
7. **Numbering is in the heading text**, continuous across Parts: `1.`, `1.1`, `Annex A.`,
   `A.1`. No Word auto-numbering on headings.

## Page setup

| Property | Value |
|---|---|
| Paper | US Letter, 21.59 x 27.94 cm, portrait (as in the reference) |
| Margins | top 2.50 cm, right, bottom and left 2.00 cm |
| Header distance | 1.00 cm; no header and no footer content |
| Content width | 17.59 cm, which every table fills |
| Sections | one; page breaks are paragraph breaks, not section breaks |

## Typography

All Arial, black unless stated. Spacing is before / after in points; line spacing is 1.15
unless stated.

| Element | Size | Weight | Spacing | Notes |
|---|---|---|---|---|
| Cover title | 26 pt | bold | 0 / 3 | keep with next |
| Cover subtitle | 14 pt | bold | 0 / 6 | often `Source (X) → Target (Y)` |
| Cover abstract | 10 pt | italic, grey `777777` | 0 / 12 | one or two sentences |
| Front title (Document control, Contents) | 14 pt | bold | 0 / 6 | not a heading style, so not in the TOC |
| Front subheading (Revision history, Approval, Conventions) | 12 pt | bold | 12 / 5 | own style without outline level |
| Part label | 13 pt | bold, red `B00417` | 14 / 8 | page break before, 2.25 pt red rule below at 4 pt |
| Heading 1 | 14 pt | bold | 18 / 6 | `N. Title`, keep with next and together |
| Heading 2 | 12 pt | bold | 12 / 5 | `N.M Title` |
| Body | 11 pt | regular | 0 / 7 | left aligned, never justified |
| Bullet | 11 pt | regular | 3 / 3 | `•` at 1.26 cm, hanging 0.63 cm; level 2 `◦` (added) |
| Note | 11 pt | `Note.` bold lead-in | 5 / 7 | directly after the table it qualifies |
| Legend | 9 pt | grey `777777` | 3 / 7 | under a table, for example the RACI key |
| Table text, standard | 10 pt | header bold | 2 / 2, single 1.08 | document control and context tables |
| Table text, compact | 8.5 pt | header bold | 2 / 2, single | working tables |
| TOC level 1 / 2 (added) | 11 / 10 pt | regular | 4 / 2 and 0 / 2 | level 2 indented 0.44 cm, dot leader to the margin |

## Colour palette

| Role | Hex | Where |
|---|---|---|
| Text | `000000` | everything not listed below |
| Secondary | `777777` | cover abstract, legends |
| Accent | `B00417` | Part labels and their rule, `[TBC]` and `[Proposed]` tags |
| Table header fill | `D9D9D9` | header row only; body rows are never filled |
| Table grid | `999999` | every cell border, 0.5 pt |

`B00417` is a deep red, darker than the UniCredit brand red. Keep it; do not mix in brand
values from `unicredit-design-system`, which governs screens, not documents.

## Page sequence

1. **Cover** (page 1). Logo centred, 10.21 cm wide, 8 pt after; three empty lines; title;
   subtitle; abstract; the metadata table `Version | Date | Author | Status | Classification`
   in standard size, one row. Typical values: status `Draft for review`, classification
   `Strictly confidential`, date `dd/mm/yyyy`.
2. **Document control** (new page). Front title, then three front subheadings:
   `Revision history` (table `Version | Date | Description`, dates `d Mon yyyy`), `Approval`
   (table `Role | Organisation | Approval scope`) and `Conventions` (bullets with a bold
   lead-in: what T is, the time zone, the meaning of `[Proposed]` and `[TBC]`, roles not
   names).
3. **Contents** (new page). Front title `Contents`, then a TOC field over Heading 1 and 2
   with hyperlinks. Part labels are not in it.
4. **Parts**, each opening on a new page with its label: `PART I: FRAMEWORK`,
   `PART II: <CONTENT>`, `PART III: CONTROL`. Section 1 is always
   `Purpose, scope and related documents` with `1.1 Purpose`, `1.2 Scope` (paragraphs
   opening `In scope:` and `Out of scope:` in bold) and `1.3 Related documents`.
5. **Annexes**, under the label `ANNEXES`, headed `Annex A. <Title>`. The last annex is
   `Glossary and sources`.

The section list for each profile is in [structure.md](references/structure.md).

## Tables

Every table follows the same design:

- full content width (17.59 cm), fixed layout, left aligned, no merged cells;
- header row filled `D9D9D9`, bold, repeated on every page, rows never split across pages;
- 0.5 pt `999999` border on every cell; cell margins 0.13 cm top and bottom, 0.18 cm left
  and right;
- the first column is bold when it holds an identifier, a label or a term (ID, step, phase,
  role, asset, term), and regular when it holds a sentence (risk, lesson, open point);
- an identifier column (`#`, `ID`, `Step`) stays narrow, 0.9 to 1.5 cm;
- a table is introduced by the heading or a sentence above it, and qualified by a `Note.`
  paragraph or a legend below it, never by a caption.

Use **standard** (10 pt) for document control and for the context tables a reader scans
once: related documents, timeline, constraints. Use **compact** (8.5 pt) for working tables:
roles, RACI, criteria, activities, steps, rollback, verification, risks, communication, open
points and annexes.

Seven tables are mandatory in every document, with these exact headers; the checker fails a
document that lacks one:

| Table | Columns |
|---|---|
| Cover metadata | Version, Date, Author, Status, Classification |
| Revision history | Version, Date, Description |
| Approval | Role, Organisation, Approval scope |
| Related documents | Document, Relationship |
| Risks and contingencies | Risk, Mitigation, Owner |
| Open points | #, Open point, Why it matters, Owner (role) |
| Glossary and sources | Term, Meaning |

The catalogue of the other standard tables, with columns and widths, is in
[structure.md](references/structure.md). Reuse a catalogue table before inventing one.

## Writing conventions

- British English (`Organisation`, `summarises`), plain and declarative.
- The reference explains itself: activity tables carry a `Why it is done` column, criteria a
  `Why (source)` column, open points a `Why it matters` column. Keep the why next to the what.
- Every step has an exit check with evidence (`Exit check · evidence`): "executed" is not a
  completion state.
- Relative days as `T-n` / `T+n`, defined once in Conventions; times in Central European Time.
- `[Proposed]` marks content that needs approval, `[TBC]` a value to confirm. Both render
  bold in the accent red, inline, at the size of the surrounding text.
- Bullets open with a bold lead-in when they define or name something
  (`**Verified, not executed:** every step...`).
- Middle dot `·` joins paired labels (`Exit check · evidence`) and legend items.

## Detailed references

- **Profiles (runbook and generic), the section list of each, and the catalogue of standard tables with columns and widths**: see [references/structure.md](references/structure.md)
- **The JSON spec the builder reads: keys, block types, inline markup, errors**: see [references/spec-format.md](references/spec-format.md)
- **Script invocation, inputs, outputs and exit codes**: see [scripts/README.md](scripts/README.md)
- **Every measured value, in twips and points, plus the list of added values**: see [assets/doc-tokens.json](assets/doc-tokens.json)
