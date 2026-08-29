# Evals: presentation-creator

---

## Eval-001: Business deck — happy path

**Input context**: Directory with at least `scope.md` (problem + solution) and `timeline.md` (phases + dates).

**User prompt**: "Create a business presentation from the docs in ./estimation/. Output to ./output/test-pres.pptx."

**Expected output characteristics**:
- File exists at the specified output path
- File opens in PowerPoint/LibreOffice without errors
- Cover slide: project name, date, Accenture footer
- Architecture slide present with labeled shapes
- Timeline slide shows phases from source `timeline.md`
- All fonts: Arial or Palatino Linotype only
- All background colors: #000000 (dark slides) or #FFFFFF (content slides)
- All accent colors: from `#A100FF`, `#7500C0`, `#460073`, `#B455AA`, `#BE82FF`, `#DCAFFF` only

**Must NOT contain**:
- Imported image files
- Invented dates or effort numbers
- Non-brand colors (check with python-pptx color reader)

**How to run**:
1. Create a `./estimation/` dir with sample `scope.md` and `timeline.md`
2. Copy `presentation-creator.md` to `.claude/agents/`
3. Run the prompt above
4. Verify output exists and open it

---

## Eval-002: Missing source data

**Input context**: Only a one-line `scope.md` with: "We want to modernize our portal."

**User prompt**: "Create a presentation from scope.md. Output to /tmp/sparse.pptx."

**Expected behavior**:
- Agent produces the presentation but marks sections as "To be defined — source data not available" where data is missing
- Does NOT invent estimates, architecture, or timeline
- Does NOT refuse to run — it proceeds with what it has

---

## Eval-003: Technical deck with AWS references

**Input context**: `architecture.md` describing AWS services (EC2, RDS, Lambda, S3, API Gateway).

**User prompt**: "Create a technical presentation from architecture.md. Audience is technical. Output to /tmp/tech.pptx."

**Expected output characteristics**:
- Architecture slide uses the exact service names from the source (EC2, not "virtual machine")
- If Strangler Fig, CQRS, or any pattern is mentioned in source → it appears on a slide
- Dependency table lists services and their dependencies as found in source

---

## Eval-004: Branding compliance check

**How to run** (after any eval):

```python
from pptx import Presentation
from pptx.dml.color import RGBColor

ALLOWED_COLORS = {
    "A100FF","7500C0","460073","B455AA","BE82FF","DCAFFF",
    "000000","FFFFFF","96968C","E6E6DC",
    # secondary (data viz only — flag if used as brand element)
    "0041F0","00FFFF","64FF50","05F0A5","FF3246","FF50A0","FF7800","FFEB32",
}

prs = Presentation("/tmp/output.pptx")
violations = []
for i, slide in enumerate(prs.slides, 1):
    for shape in slide.shapes:
        try:
            fill = shape.fill
            if fill.type and hasattr(fill, 'fore_color') and fill.fore_color.type:
                rgb = str(fill.fore_color.rgb)
                if rgb.upper() not in ALLOWED_COLORS:
                    violations.append(f"Slide {i}, shape {shape.name!r}: fill #{rgb}")
        except: pass
if violations:
    print("Brand violations:", violations)
else:
    print("Brand compliant ✓")
```
