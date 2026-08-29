# Design tokens

## Contents

- Color palette
- Primary — use freely
- Functional / state palette (Bricks-aligned, derived from public refresh)
- Neutrals — Bricks "lighter chromatic" approach
- Typography
- Brand typeface — public truth
- Fallback stack (ship by default unless the WeAreDesign font is provisioned)
- Type scale (rem, root = 16 px)
- Spacing, radius, elevation
- CSS custom-properties block — paste verbatim

## Color palette

### Primary — use freely

| Role | Hex | RGB | Notes |
|---|---|---|---|
| UniCredit Red | `#E30613` | 227, 6, 19 | PMS 485 C · CMYK 0/97/92/11. Primary brand colour. CTAs, links, headlines. |
| White | `#FFFFFF` | 255, 255, 255 | Surfaces, reverse logo. |
| Black | `#000000` | 0, 0, 0 | Body text on white only. Avoid for very large surfaces. |
| Dark Navy | `#1A1A2E` | 26, 26, 46 | Limited application: dark themes, footer surfaces, inverted hero blocks. |

> The 2012 brand book also defined a "Mediterranean" warm palette
> (terracotta / sand) for collateral. **Do not use it for digital UI** —
> the Bricks refresh removed it.

### Functional / state palette (Bricks-aligned, derived from public refresh)

These are the safe defaults for state semantics. Override only against
the gated WeAreDesign tokens.

| Role | Hex | Use |
|---|---|---|
| Success | `#1F9D55` | Confirmations, positive deltas |
| Warning | `#F0A500` | Soft warnings, advisory |
| Error | `#E30613` (UniCredit Red) | Destructive actions, validation errors |
| Info | `#0050B3` | Informative banners, neutral notifications |

### Neutrals — Bricks "lighter chromatic" approach

| Token | Hex | Use |
|---|---|---|
| Neutral 0 | `#FFFFFF` | Page background |
| Neutral 50 | `#F7F7F8` | Cards, secondary surfaces |
| Neutral 100 | `#EDEDEF` | Dividers, disabled fills |
| Neutral 300 | `#C5C5CC` | Borders, separators |
| Neutral 500 | `#7B7B85` | Muted text, captions |
| Neutral 700 | `#3F3F46` | Body text on light surface |
| Neutral 900 | `#0E0E12` | Headings on light surface |

**Forbidden:** any palette outside the matrix above (no purple, no teal,
no neon green, no off-brand red).

---

## Typography

### Brand typeface — public truth

UniCredit commissioned a custom typeface for its wordmark and digital
properties (publicly described as "energetic and modern, evoking the
warmth and openness of the bank"). The custom face is **not licensed for
public redistribution** and may not be available outside the
WeAreDesign masterfiles.

**Historic / supporting brand fonts** (from the public 2012 brand book):

- **Pryor Medium** — used for brand creation
- **Dax** (Light / Regular / Medium / Bold) — used for stationery and
  descriptors. Designer: Hans Reichel. Closest match for the wordmark
  shapes.
- **FS Joey** (Fontsmith) — licensed for some publications.

### Fallback stack (ship by default unless the WeAreDesign font is provisioned)

```
font-family:
  "UniCredit",                /* official custom face when provisioned */
  "Dax",                      /* historical Bricks fallback */
  "FS Joey",                  /* licensed fallback */
  "Inter",                    /* open-source modern geometric sans, very close metrics */
  -apple-system, BlinkMacSystemFont,
  "Segoe UI", Roboto, Helvetica, Arial,
  sans-serif;
```

If the `UniCredit` / `Dax` / `FS Joey` faces are not delivered through
the project's asset pipeline, **Inter** is the recommended open-source
fallback (geometric sans, friendly aperture, excellent multi-script support).

### Type scale (rem, root = 16 px)

| Token | rem | px | Weight | Use |
|---|---|---|---|---|
| `--uc-fs-display` | 3.5 | 56 | 700 | Hero titles, marketing only |
| `--uc-fs-h1` | 2.5 | 40 | 700 | Page titles |
| `--uc-fs-h2` | 2.0 | 32 | 700 | Section titles |
| `--uc-fs-h3` | 1.5 | 24 | 600 | Sub-section titles |
| `--uc-fs-h4` | 1.25 | 20 | 600 | Card titles |
| `--uc-fs-lg` | 1.125 | 18 | 400 | Lead paragraphs |
| `--uc-fs-base` | 1.0 | 16 | 400 | Body |
| `--uc-fs-sm` | 0.875 | 14 | 400 | Secondary text, helper |
| `--uc-fs-xs` | 0.75 | 12 | 500 | Micro-copy, legal |

Line-heights: 1.2 for headings ≥ 24 px, 1.5 for body, 1.4 for sub-headings.

---

## Spacing, radius, elevation

```
Spacing — 8 px base grid (Bricks "streamlined grid")
--uc-space-2xs:  0.25rem;   /*  4 px */
--uc-space-xs:   0.5rem;    /*  8 px */
--uc-space-sm:   0.75rem;   /* 12 px */
--uc-space-md:   1rem;      /* 16 px */
--uc-space-lg:   1.5rem;    /* 24 px */
--uc-space-xl:   2rem;      /* 32 px */
--uc-space-2xl:  3rem;      /* 48 px */
--uc-space-3xl:  4rem;      /* 64 px */

Radius — restrained, banking-appropriate
--uc-radius-sm:   4px;
--uc-radius-md:   8px;
--uc-radius-lg:   12px;
--uc-radius-xl:   16px;
--uc-radius-pill: 9999px;

Elevation — subtle, never decorative
--uc-shadow-sm: 0 1px 2px rgba(14, 14, 18, 0.06);
--uc-shadow-md: 0 2px 6px rgba(14, 14, 18, 0.08), 0 1px 2px rgba(14, 14, 18, 0.06);
--uc-shadow-lg: 0 8px 24px rgba(14, 14, 18, 0.10);
```

**Container width**: 1200 px max for dashboards / banking workflows;
1320 px max for marketing / public website pages.

**Breakpoints** (mobile-first; matches the public website refresh):

```
sm:  576px
md:  768px
lg:  1024px   /* tablet landscape — banking app primary breakpoint */
xl:  1280px
2xl: 1440px
```

---

## CSS custom-properties block — paste verbatim

Drop this into the project's `_uc-tokens.scss` (or equivalent global
stylesheet). The `--uc-*` prefix prevents collisions with the host design
system; the framework agent then aliases the local tokens
(`--color-primary` → `var(--uc-color-primary)`).

```css
:root {
  /* Brand */
  --uc-color-red:        #E30613;
  --uc-color-red-darker: #B00010;   /* hover */
  --uc-color-red-light:  #FCE6E8;   /* tinted background */
  --uc-color-white:      #FFFFFF;
  --uc-color-black:      #000000;
  --uc-color-navy:       #1A1A2E;

  /* Functional */
  --uc-color-success: #1F9D55;
  --uc-color-warning: #F0A500;
  --uc-color-error:   #E30613;
  --uc-color-info:    #0050B3;

  /* Neutrals */
  --uc-color-neutral-0:   #FFFFFF;
  --uc-color-neutral-50:  #F7F7F8;
  --uc-color-neutral-100: #EDEDEF;
  --uc-color-neutral-300: #C5C5CC;
  --uc-color-neutral-500: #7B7B85;
  --uc-color-neutral-700: #3F3F46;
  --uc-color-neutral-900: #0E0E12;

  /* Semantic aliases (project-facing) */
  --uc-color-primary:    var(--uc-color-red);
  --uc-color-on-primary: var(--uc-color-white);
  --uc-color-bg:         var(--uc-color-neutral-0);
  --uc-color-surface:    var(--uc-color-neutral-50);
  --uc-color-text:       var(--uc-color-neutral-900);
  --uc-color-text-muted: var(--uc-color-neutral-500);
  --uc-color-border:     var(--uc-color-neutral-300);
  --uc-color-link:       var(--uc-color-red);

  /* Typography */
  --uc-font-family: "UniCredit", "Dax", "FS Joey", "Inter",
                    -apple-system, BlinkMacSystemFont,
                    "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --uc-fw-regular: 400;
  --uc-fw-medium:  500;
  --uc-fw-semi:    600;
  --uc-fw-bold:    700;

  --uc-fs-display: 3.5rem;
  --uc-fs-h1:      2.5rem;
  --uc-fs-h2:      2rem;
  --uc-fs-h3:      1.5rem;
  --uc-fs-h4:      1.25rem;
  --uc-fs-lg:      1.125rem;
  --uc-fs-base:    1rem;
  --uc-fs-sm:      0.875rem;
  --uc-fs-xs:      0.75rem;

  --uc-lh-tight:  1.2;
  --uc-lh-normal: 1.5;
  --uc-lh-snug:   1.4;

  /* Spacing — 8 px grid */
  --uc-space-2xs: 0.25rem;
  --uc-space-xs:  0.5rem;
  --uc-space-sm:  0.75rem;
  --uc-space-md:  1rem;
  --uc-space-lg:  1.5rem;
  --uc-space-xl:  2rem;
  --uc-space-2xl: 3rem;
  --uc-space-3xl: 4rem;

  /* Radius */
  --uc-radius-sm:   4px;
  --uc-radius-md:   8px;
  --uc-radius-lg:   12px;
  --uc-radius-xl:   16px;
  --uc-radius-pill: 9999px;

  /* Elevation */
  --uc-shadow-sm: 0 1px 2px rgba(14, 14, 18, 0.06);
  --uc-shadow-md: 0 2px 6px rgba(14, 14, 18, 0.08), 0 1px 2px rgba(14, 14, 18, 0.06);
  --uc-shadow-lg: 0 8px 24px rgba(14, 14, 18, 0.10);

  /* Motion */
  --uc-motion-fast:   150ms cubic-bezier(0.2, 0, 0, 1);
  --uc-motion-base:   250ms cubic-bezier(0.2, 0, 0, 1);
  --uc-motion-slow:   400ms cubic-bezier(0.2, 0, 0, 1);

  /* Focus ring — non-negotiable */
  --uc-focus-ring: 0 0 0 2px var(--uc-color-white),
                   0 0 0 4px var(--uc-color-red);
}

@media (prefers-reduced-motion: reduce) {
  :root {
    --uc-motion-fast: 0ms;
    --uc-motion-base: 0ms;
    --uc-motion-slow: 0ms;
  }
}
```

---
