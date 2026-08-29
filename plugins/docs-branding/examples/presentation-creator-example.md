# Example: presentation-creator

## Scenario 1: Business deck from estimation docs

**Setup**: Directory `./estimation/` contains `scope.md`, `architecture.md`, `timeline.xlsx` description (or `.md`), `risks.md`.

**User prompt**:
> Create a business presentation from the docs in ./estimation/. Project is "Customer Portal Modernization" for client Accenture Internal. Output to ./output/presentation.pptx.

**Expected output characteristics**:
- Cover slide with project name, date, "Accenture" footer
- 10–15 slides following the standard structure
- Architecture shown as labeled python-pptx shapes (no images)
- Timeline rendered as a table or bar chart using shapes
- Every section cites its source file
- All colors from Accenture palette only
- Font: Arial body, Palatino Linotype for cover title

**Must NOT contain**:
- Invented estimates or dates not present in source docs
- Hard-coded images or external image imports
- Non-brand colors

---

## Scenario 2: Technical deck for architecture review

**Setup**: Files `architecture-decision.md`, `component-map.yaml`, `aws-services.md`.

**User prompt**:
> Create a technical presentation from architecture-decision.md and component-map.yaml. Audience is technical. Output to ./output/architecture-deck.pptx.

**Expected output characteristics**:
- Architecture slide with AWS service names (EC2, RDS, Lambda, etc.)
- Dependency map as a table or shape diagram
- Pattern names cited (e.g., CQRS, Strangler Fig) if present in source docs
- Code/config fragments in fixed-width text boxes if in source
- 15–25 slides

**Must NOT contain**:
- Business-only framing ("our clients love...")
- Invented AWS services not in the source docs
