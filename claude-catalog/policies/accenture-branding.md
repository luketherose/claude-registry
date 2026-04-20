# Accenture Brand Guidelines — Quick Reference

This file is the single source of truth for Accenture brand constants
used by `presentation-creator` and `document-creator` capabilities.
All generated output (PPTX, PDF, HTML) must use the values defined here.

---

## Color Palette

### Primary (use freely)

| Role | Hex | RGB | python-pptx |
|------|-----|-----|-------------|
| Accenture Purple | `#A100FF` | 161, 0, 255 | `RGBColor(0xA1,0x00,0xFF)` |
| Purple Dark | `#7500C0` | 117, 0, 192 | `RGBColor(0x75,0x00,0xC0)` |
| Purple Darker | `#460073` | 70, 0, 115 | `RGBColor(0x46,0x00,0x73)` |
| Black | `#000000` | 0, 0, 0 | `RGBColor(0x00,0x00,0x00)` |
| White | `#FFFFFF` | 255, 255, 255 | `RGBColor(0xFF,0xFF,0xFF)` |
| Warm Gray | `#96968C` | 150, 150, 140 | `RGBColor(0x96,0x96,0x8C)` |
| Light Gray | `#E6E6DC` | 230, 230, 220 | `RGBColor(0xE6,0xE6,0xDC)` |

### Extended Purples (use as tints/accents)

| Role | Hex | RGB |
|------|-----|-----|
| Purple Pink | `#B455AA` | 180, 85, 170 |
| Purple Light | `#BE82FF` | 190, 130, 255 |
| Purple Lighter | `#DCAFFF` | 220, 175, 255 |

### Secondary (use ONLY for data visualization, never as brand elements)

| Name | Hex |
|------|-----|
| Blue | `#0041F0` |
| Cyan | `#00FFFF` |
| Green | `#64FF50` |
| Teal | `#05F0A5` |
| Red | `#FF3246` |
| Pink | `#FF50A0` |
| Orange | `#FF7800` |
| Yellow | `#FFEB32` |

### CSS variables (for HTML/PDF generation)

```css
:root {
  --acc-purple:       #A100FF;
  --acc-purple-dark:  #7500C0;
  --acc-purple-dk2:   #460073;
  --acc-black:        #000000;
  --acc-white:        #FFFFFF;
  --acc-gray:         #96968C;
  --acc-gray-light:   #E6E6DC;
  --acc-purple-pink:  #B455AA;
  --acc-purple-lt:    #BE82FF;
  --acc-purple-lt2:   #DCAFFF;
}
```

---

## Typography

| Font (brand) | System fallback | Use |
|---|---|---|
| Graphik | **Arial** | Body, labels, captions, headings |
| GT Sectra Fine | **Palatino Linotype** | Cover titles, dividers only |

- Body text: Arial 12–14pt, Black
- Slide titles: Arial Bold 24–28pt, Black (on light BG) or White (on dark BG)
- Cover/divider title: Palatino Linotype 40–60pt, White
- Cover subtitle: Arial 18–24pt, White or Light Purple
- Footnotes/footer: Arial 8–10pt, Warm Gray

---

## Slide Dimensions

- Widescreen 16:9: **13.33" × 7.50"** (standard)

---

## python-pptx Constants Block

Copy this block verbatim at the top of any python-pptx generation script:

```python
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

# Accenture brand colors
ACC_PURPLE      = RGBColor(0xA1, 0x00, 0xFF)
ACC_PURPLE_DARK = RGBColor(0x75, 0x00, 0xC0)
ACC_PURPLE_DK2  = RGBColor(0x46, 0x00, 0x73)
ACC_PURPLE_PINK = RGBColor(0xB4, 0x55, 0xAA)
ACC_PURPLE_LT   = RGBColor(0xBE, 0x82, 0xFF)
ACC_PURPLE_LT2  = RGBColor(0xDC, 0xAF, 0xFF)
ACC_BLACK       = RGBColor(0x00, 0x00, 0x00)
ACC_WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
ACC_GRAY        = RGBColor(0x96, 0x96, 0x8C)
ACC_GRAY_LT     = RGBColor(0xE6, 0xE6, 0xDC)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.50)
FONT_BODY    = "Arial"
FONT_DISPLAY = "Palatino Linotype"
```

---

## Slide Layout Rules

### Cover slide (opening + section dividers)
- Background: `#000000` (black) or `#460073` (dark purple)
- Left accent bar: `#A100FF`, width ~0.07"
- Title: Palatino Linotype Bold, 48–60pt, White
- Subtitle: Arial, 22–26pt, White or `#DCAFFF`
- Presenter/date: Arial, 12–14pt, `#96968C`
- Footer: "© [Year] Accenture. All rights reserved." — Arial 9pt, `#96968C`

### Content slide (standard)
- Background: `#FFFFFF` (white)
- Title: Arial Bold, 26–28pt, `#000000`
- Body: Arial Regular, 12–14pt, `#000000`
- Accent elements: `#A100FF` — borders, bullets, icons, highlights
- Divider line under title: `#A100FF`, height 2pt
- Footer: Arial 8pt, `#96968C` — "© [Year] Accenture. All rights reserved."

### Dark content slide
- Background: `#000000` or `#460073`
- Title/body: White
- Accent: `#A100FF`

### Table styling
- Header row fill: `#A100FF` (purple) — text White, Bold
- Alternating rows: `#FFFFFF` / `#E6E6DC`
- Border color: `#96968C`

---

## CSS Template for HTML → PDF

```css
body {
  font-family: Arial, 'Graphik', sans-serif;
  color: #000000;
  background: #FFFFFF;
  margin: 0;
  padding: 0;
}

.cover {
  background: #000000;
  color: #FFFFFF;
  min-height: 100vh;
  padding: 60px 80px;
  border-left: 8px solid #A100FF;
}

.cover h1 {
  font-family: 'Palatino Linotype', 'Palatino', Georgia, serif;
  font-size: 52pt;
  font-weight: bold;
  margin: 0 0 16px 0;
}

.cover .subtitle {
  font-size: 22pt;
  color: #DCAFFF;
}

.content-section {
  padding: 48px 80px;
  page-break-before: always;
}

h2 {
  font-size: 24pt;
  font-weight: bold;
  color: #000000;
  border-bottom: 3px solid #A100FF;
  padding-bottom: 8px;
  margin-bottom: 24px;
}

h3 {
  font-size: 16pt;
  color: #7500C0;
  margin-top: 24px;
}

.accent { color: #A100FF; }

table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

th {
  background: #A100FF;
  color: #FFFFFF;
  font-weight: bold;
  padding: 8px 12px;
  text-align: left;
}

td {
  padding: 8px 12px;
  border-bottom: 1px solid #E6E6DC;
}

tr:nth-child(even) td { background: #F9F9F6; }

.footer {
  font-size: 9pt;
  color: #96968C;
  text-align: center;
  padding: 16px;
  border-top: 1px solid #E6E6DC;
}
```

---

## Logos and Assets

- Asset library: **Accenture Brand Space** — brandspace.accenture.com
- Contact for brand assets: brandsupport@accenture.com
- Footer text: `Copyright © [Year] Accenture. All rights reserved.`
- The Accenture logo must appear on cover slides/pages. If the logo file is not
  available locally, insert a text placeholder: `[Accenture Logo]` in `#A100FF`.
