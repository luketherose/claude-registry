# Evals: document-creator

---

## Eval-001: Technical PDF — happy path

**Input context**: Directory with `scope.md`, `architecture.md`, `effort.md`.

**User prompt**: "Create a technical PDF from the files in ./estimation/. Output to /tmp/test-doc.pdf."

**Expected output characteristics**:
- File exists at /tmp/test-doc.pdf
- PDF opens without errors, is text-selectable (not an image)
- Cover page present: project name, date, version, Accenture footer
- Document control table present
- Sections 1–8 all present
- Architecture section uses cloud service names exactly as in source
- Effort table numbers match source `effort.md` exactly

**Must NOT contain**:
- Invented estimates
- Missing cover page
- Non-Accenture colors (check HTML source before conversion)

**How to run**:
1. Create `./estimation/` with sample files
2. Copy `document-creator.md` to `.claude/agents/`
3. Run the prompt
4. Open the PDF and inspect visually

---

## Eval-002: Business DOCX

**Input context**: Same files.

**User prompt**: "Create a business Word document from ./estimation/. Audience is executive. Output to /tmp/brief.docx."

**Expected behavior**:
- `.docx` file produced and opens in Word/LibreOffice Writer
- Headings styled correctly (Arial Bold, colors from brand palette)
- No code blocks in the body
- Executive summary on page 1
- Footer on every page: "© [Year] Accenture. All rights reserved."

---

## Eval-003: Missing Chrome (PDF fallback)

**Input context**: Chrome not installed at expected path.

**Expected behavior**:
- Agent detects Chrome is not available
- Notifies user with clear message
- Offers to produce DOCX as alternative
- Does NOT crash silently

---

## Eval-004: Delegation to software-architect

**Input context**: `architecture.md` is very brief (just a list of services, no design rationale).

**User prompt**: "Create a technical PDF. Include a detailed architecture section."

**Expected behavior**:
- Agent spawns `software-architect` to produce a deeper architecture analysis
- Uses the returned analysis as section 3 content
- Cites "Architecture analysis produced by software-architect subagent" in notes
