---
name: unicredit-design-system
description: "ALWAYS use this skill when the project end client is UniCredit (UC banking group, including UniCredit Bank Italy/Germany/Austria/CEE). Trigger phrases: \"UniCredit\", \"UCB\", \"Bricks design system\", any UC product or app. Provides UniCredit brand identity rules (logo, colors, typography), the Bricks design-system component catalogue, accessibility targets (EN 301 549 / WCAG 2.1 AA), tone of voice, and ready-to-use design tokens for HTML/CSS/SCSS. Loaded automatically by the frontend-developer agent (Angular, React, Vue, Qwik, Vanilla). Do not use for non-UniCredit projects (use design-expert + accenture-branding for Accenture deliverables)."
---

# Unicredit Design System

This skill is the authoritative source for UniCredit's public brand and
digital design system ("Bricks", surfaced through the UniCredit
**WeAreDesign** brand-management platform).

When invoked, you return the brand constants, layout rules, component
inventory, accessibility targets, and ready-to-paste design tokens that the
calling agent must apply when delivering frontend code for the UniCredit
client.

You **do not generate components or screens**. You provide the standards
so the framework-specific frontend agent (Angular, React, Vue, Qwik,
Vanilla) can apply them consistently.

---

## When to load this skill

Load this skill when **any one** of the following is true:

- The user explicitly mentions UniCredit, UC, "WeAreDesign", "Bricks
  Design System", or any UniCredit subsidiary (UniCredit Bank Italy,
  HypoVereinsbank, UniCredit Bank Austria, UniCredit Bulbank, UniCredit
  CZ&SK, UniCredit Hungary, UniCredit Romania, Zagrebačka banka, …).
- The project's `package.json`, `pom.xml`, repository name, organisation,
  Git remote, or top-level README contains `unicredit`, `uc-`, `wearedesign`,
  `bricks-ds`, `hvb`, `zaba`, or `bulbank`.
- A previous conversation turn established the client as UniCredit.

If none of the signals above are present, this skill is **not applicable**:
fall back to the project's design system or to `design-expert` defaults.

---

## Source authority and gaps

The authoritative source is UniCredit's own portal, `WeAreDesign`
(`zeroheight.com/44059a76b/p/51d64e-wearedesign`) and the related Figma
masterfiles. That portal is **gated**: requires UniCredit SSO. The values
collected here are reconstructed from UniCredit's public corporate site,
the UniCredit Brand Book PDF (2012, public), Tangity's published case
studies on the public website / mobile app / accessibility evolution, and
the public press / fonts archives.

**Rule for the calling agent**: the values below are the safe public
defaults. If access to the gated WeAreDesign tokens is available (Figma
variables, Bricks component library, official Sketch/Figma kits), those
override every default in this file, but never silently. Reference the
source explicitly in code comments: `// source: WeAreDesign Bricks
v<x.y.z>` so reviewers can trace the values.

---

## Brand identity

### Brand essence

> "Dynamism, reliability, and a global approach. The number 1 within the
> design symbolises the unique strength and leadership our group offers."
> Source: UniCredit, Our Brand and Design System

Five descriptors to anchor every design decision:

| Pillar | Implication for UI |
|---|---|
| Reliable | Strong, predictable interaction patterns. No experimental controls. |
| Dynamic | Confident motion, but never decorative. 150–250ms cubic transitions. |
| Open / warm | Generous white space, inviting headlines, never cold/stark layouts. |
| Global | Localisable copy, RTL-safe layouts, locale-aware date/number formats. |
| Simple, clear, clean | The three Bricks UI principles: every decision must serve at least one. |

### Logo rules

| Rule | Value |
|---|---|
| Primary lockup | Red sphere with white "1", wordmark to the right |
| Allowed variants | Red on white **or** white on red. Dark navy backgrounds use the white-on-red sphere. |
| Forbidden | Recolouring, distortion, stretching, rotation, gradients, drop shadows, outlines |
| Minimum size, symbol alone (digital) | 16 px |
| Minimum size, full lockup width (digital) | 80 px |
| Clear space | One sphere-diameter on every side (no other element inside this box) |
| File formats | SVG / PNG@2x for screen, EPS / PDF for print |

In code, always reference the logo via a versioned asset (`/assets/brand/unicredit-logo.svg`).
Never inline it as a base64 blob, and never recreate it as `<svg>` paths.
The asset must come from the WeAreDesign masterfiles or from a UniCredit-owned
brand repository.

---

## Accessibility: non-negotiable

The public-website redesign targeted the European harmonised standard
**EN 301 549 v3.2.1**, which incorporates **WCAG 2.1 level AA** for the
web. Treat **AA** as the minimum bar; AAA where reasonable.

| Concern | Rule |
|---|---|
| Text contrast | ≥ 4.5:1 (body); ≥ 3:1 (large text ≥ 18 pt or 14 pt bold) |
| Non-text contrast | ≥ 3:1 for UI controls and meaningful icons (WCAG 1.4.11) |
| Focus indicator | 2 px solid `--uc-color-red` with 2 px white halo, **never** `outline: none` without a replacement |
| Touch / click target | ≥ 44 × 44 px (WCAG 2.5.5) |
| Keyboard | Every interactive element reachable by Tab, no traps, visible focus |
| Forms | Every input has a programmatic `<label>`; errors via `aria-describedby` |
| Motion | Respect `prefers-reduced-motion: reduce` and disable non-essential motion |
| Screen reader | Landmarks (`<header>` / `<main>` / `<nav>` / `<footer>`); semantic headings; meaningful `alt` text |
| Language | `<html lang="…">` set per locale (it / de / en / hr / bg / cs / hu / ro / sk / ru) |
| Colour | Never the sole carrier of meaning (e.g. red error must also have an icon and text) |

**Critical contrast notes**: UniCredit Red `#E30613` on `#FFFFFF` is
`4.16:1`, which **fails AA for normal body text**. Use it for ≥ 18 px body or
for headings / CTAs only, or pair it with white text on red surfaces
(`#FFFFFF` on `#E30613` gives the same ratio, valid for large text and
icons but not for body). For inline danger / link text, use
`var(--uc-color-red-darker) #B00010` (≥ 6.7:1 on white).

---

## Tone of voice

| Attribute | Do | Don't |
|---|---|---|
| Warm, open | "Welcome back, Anna." | "User authenticated." |
| Plain banking | "Transfer", "Send money" | "Disposition", "Pecuniary instrument" |
| Confident | "Your transfer is on its way." | "We will try to process your transfer." |
| Localised | Italian / German / English / CEE locales, never auto-translate Italian banking terms | Untranslated Italian on a German screen |
| Accessible | Active voice, short sentences, ≤ 18 words | Passive, nested clauses, jargon |

Currency: locale-aware, never hard-code € (use `Intl.NumberFormat`).
Dates: locale-aware, never hard-code `dd/mm/yyyy`.

---

## Iconography & imagery

- **Iconography**: stroke-based, 24 × 24 grid, 1.5 px stroke, rounded
  joins. Restrict to `--uc-color-text` / `--uc-color-text-muted` /
  `--uc-color-primary`. No filled emojis, no flat-design caricature icons.
- **Imagery**: photographic, human-centred, natural light. Crop on
  meaningful detail. Avoid stock-cliché. Bricks refresh allows
  "photographic elements on flat backgrounds".
- **Illustration**: minimal, monochrome line. Brand red as a single accent
  per illustration.

---

## How the framework agent must apply this skill

The calling agent (Angular, React, Vue, Qwik, Vanilla) follows this
sequence:

1. **Detect UniCredit context**, using the signals in *When to load
   this skill*. If unclear, ask the user once: "Is this delivery for
   the UniCredit client?".
2. **Confirm the host project's token system**: does it already define
   `--color-primary` / `_tokens.scss` / Tailwind config? If yes, **alias**
   the host tokens to the `--uc-*` ones from this skill, and do **not**
   duplicate or rewrite.
3. **Adopt the `--uc-*` block** verbatim into a single `_uc-tokens.scss`
   imported once, before any component styles.
4. **Apply Bricks components first.** Pick the closest entry from the
   Component inventory section before drawing anything custom.
5. **Verify accessibility budget.** Run a final pass against the
   Accessibility section before submitting code. The focus ring,
   contrast, target size, and reduced-motion rules are mandatory.
6. **Tag every gap explicitly.** When a value is reconstructed (because
   the gated WeAreDesign value was unavailable), add an inline comment
   `/* TODO: confirm against WeAreDesign Bricks v<x.y.z> */` so the
   client reviewer can resolve it.

---

## What you never do

- Substitute UniCredit Red with another red. `#E30613` is the brand red.
- Use UniCredit Red for body text on white (fails WCAG AA contrast).
- Recolour, distort, or recreate the logo as inline SVG paths.
- Mix in palettes from other banks or generic Tailwind/Material defaults.
- Apply Bricks rules to a non-UniCredit project: this skill is **client-scoped**.
- Hardcode hex values in component styles: always reference `--uc-*` tokens.
- Disable focus rings or motion preferences for visual reasons.

---

## Public references

- UniCredit, Our Brand and Design System: `unicreditgroup.eu/en/unicredit-at-a-glance/our-brand.html`
- UniCredit WeAreDesign (gated): `zeroheight.com/44059a76b/p/51d64e-wearedesign`
- Tangity, Bricks design system case study: `tangity.global/works/unicredit-new-design-ecosystem-for-home-banking-and-public-website`
- Tangity, UniCredit Public Website Digital Accessibility Evolution: `tangity.global/works/unicredit-public-website-digital-accessibility-evolution`
- Tangity, UniCredit Global Mobile Banking App: `tangity.global/en/works/unicredit-global-mobile-banking-app`
- UniCredit Brand Book (2012, public PDF): `static.thefinancialbrand.com/uploads/2012/06/unicredit_brand_book.pdf`
- BrandingStyleGuides, UniCredit: `brandingstyleguides.com/guide/unicredit/`
- DesignYourWay, UniCredit logo, colours, font: `designyourway.net/blog/unicredit-logo/`
- 1000logos, UniCredit Bank: `1000logos.net/unicredit-bank-logo/`
- EN 301 549 v3.2.1: European harmonised accessibility standard for ICT
- WCAG 2.1: `w3.org/WAI/WCAG21/quickref/` (level AA target)

## Detailed references

- **Colour palette, typography, spacing scale and the full CSS custom-properties block**: see [references/design-tokens.md](references/design-tokens.md)
- **Bricks component inventory and ready-to-adapt CSS samples**: see [references/component-catalogue.md](references/component-catalogue.md)
