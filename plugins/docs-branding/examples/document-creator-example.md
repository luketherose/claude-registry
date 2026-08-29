# Example: document-creator

## Scenario 1: Technical PDF from estimation package

**Setup**: Directory `./estimation/` with `scope.md`, `architecture.md`, `effort-breakdown.md`.

**User prompt**:
> Create a technical PDF document from the files in ./estimation/. Project: "Payment Service Migration". Output to ./output/technical-doc.pdf.

**Expected output characteristics**:
- Cover page: project name, date, version 1.0, Accenture footer
- Document control table
- Executive summary (3–5 bullets)
- Sections 1–8 from the standard structure
- Architecture section uses GCP/AWS/Azure naming exactly as in source
- Effort estimate table derived from effort-breakdown.md
- Risks table populated from source, not invented
- Accenture brand colors and Arial font throughout

**Must NOT contain**:
- Invented numbers
- Missing cover page
- Non-Accenture colors or fonts

---

## Scenario 2: Business Word document

**Setup**: Same files, business audience.

**User prompt**:
> Create a business Word document from ./estimation/. Audience is executive. Output to ./output/executive-brief.docx.

**Expected output characteristics**:
- Executive summary on page 1
- Plain language throughout (no raw tech jargon without explanation)
- Architecture described in prose + table, no code
- Timeline prominent with business milestones
- python-docx output, Accenture heading styles applied

**Must NOT contain**:
- Deep technical patterns unexplained
- Code blocks
- Missing footer
