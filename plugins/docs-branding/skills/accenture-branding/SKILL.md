---
name: accenture-branding
description: "This skill should be used when an agent (presentation-creator, document-creator) generates an Accenture-branded deliverable and needs the brand reference data: color palette (hex values, python-pptx + CSS constants), typography (fonts and sizes), slide layout specs, HTML/CSS template for PDF, and usage guidelines. Trigger phrases: \"Accenture branding\", \"Accenture deck\", \"Accenture PDF template\", \"brand colors\". Do not use for client-specific design systems (e.g., UniCredit Bricks, which is covered by unicredit-design-system)."
---

# Accenture Branding

This skill is the authoritative source for Accenture brand standards used
in team-generated presentations and documents. Apply the brand constants,
layout rules and code blocks below to produce brand-correct output.

Generate no presentations or documents here. These are the standards. Other
agents apply them consistently.

---

## Color Palette

The values below are also in `assets/brand-tokens.json`, in hex and RGB. Read
that file rather than parsing these tables: it is the same data without the
prose, and it carries the typography scale and slide dimensions too.

### Primary (use freely)

| Role | Hex | RGB |
|---|---|---|
| Accenture Purple | `#A100FF` | 161, 0, 255 |
| Purple Dark | `#7500C0` | 117, 0, 192 |
| Purple Darker | `#460073` | 70, 0, 115 |
| Black | `#000000` | 0, 0, 0 |
| White | `#FFFFFF` | 255, 255, 255 |
| Warm Gray | `#96968C` | 150, 150, 140 |
| Light Gray | `#E6E6DC` | 230, 230, 220 |

### Extended Purples (use as tints/accents)

| Role | Hex |
|---|---|
| Purple Pink | `#B455AA` |
| Purple Light | `#BE82FF` |
| Purple Lighter | `#DCAFFF` |

### Secondary (use ONLY for data visualization)

Blue `#0041F0` · Cyan `#00FFFF` · Green `#64FF50` · Teal `#05F0A5`
Red `#FF3246` · Pink `#FF50A0` · Orange `#FF7800` · Yellow `#FFEB32`

---

## python-pptx Constants Block

Import `assets/pptx_constants.py` rather than pasting a block into every
script. It defines `ACC_PURPLE`, `ACC_PURPLE_DARK`, `ACC_PURPLE_DK2`,
`ACC_PURPLE_PINK`, `ACC_PURPLE_LT`, `ACC_PURPLE_LT2`, `ACC_BLACK`,
`ACC_WHITE`, `ACC_GRAY`, `ACC_GRAY_LT`, plus `SLIDE_W`, `SLIDE_H`,
`FONT_BODY` and `FONT_DISPLAY`.

When a value changes, change `assets/brand-tokens.json` first and bring the
other two assets into step with it.

---

## Typography

| Font (brand) | System fallback | Use |
|---|---|---|
| Graphik | **Arial** | Body, labels, captions, headings |
| GT Sectra Fine | **Palatino Linotype** | Cover titles, dividers only |

- Cover/divider titles: Palatino Linotype Bold, 48–60pt, White
- Slide titles (content): Arial Bold, 26–28pt, Black
- Body: Arial Regular, 12–14pt, Black (or White on dark slides)
- Footer: Arial 8pt, Warm Gray

---

## Slide Layout Rules

### Cover and divider slides (dark)
- Background: `#000000` (black)
- Left accent bar: `#A100FF`, width ~0.07"
- Title: Palatino Linotype Bold, 48–60pt, White
- Subtitle: Arial, 20–24pt, `#DCAFFF`
- Footer: "© [Year] Accenture. All rights reserved." Arial 9pt, `#96968C`

### Content slides (light)
- Background: `#FFFFFF`
- Title: Arial Bold, 26–28pt, `#000000`
- Accent line under title: `#A100FF`, 2pt height
- Body: Arial Regular, 12–14pt, `#000000`
- Cards/boxes: fill `#E6E6DC` or `#F4F0FF`, border `#A100FF`
- Footer: Arial 8pt, `#96968C`

### Table styling
- Header row: fill `#A100FF`, text White Bold
- Alternating rows: `#FFFFFF` / `#E6E6DC`
- Border: `#96968C`, 1pt

---

## CSS Template for HTML → PDF

The stylesheet is `assets/accenture.css`. Link it from the generated HTML
rather than inlining a copy, so a brand change lands in one place.

---

## Chrome Headless PDF Command

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu \
  --print-to-pdf=<output_path> \
  --print-to-pdf-no-header \
  <html_file_path>
```

---

## Logo and Legal

- Logo: use the text placeholder `[Accenture]` in `#A100FF` if the logo file is not available locally.
- Footer text on every slide/page: `Copyright © [Year] Accenture. All rights reserved.`
- Asset library: Accenture Brand Space (brandspace.accenture.com)
- Contact for brand assets: brandsupport@accenture.com

---

## Never do this

- Deviate from the color palette above
- Use fonts other than Arial and Palatino Linotype (system fallbacks for Graphik and GT Sectra Fine)
- Generate output files. Provide the constants and rules for the calling agent to use instead.
