# Component catalogue

## Contents

- Bricks component inventory
- 1. Inputs & selections
- 2. Actions
- 3. Navigation & search
- 4. Overlays
- 5. Indicators
- 6. Containers
- 7. Navigation structures
- 8. Templates
- Component primer (CSS samples ready to adapt)
- Primary button
- Card
- Input field
- Focus ring (apply globally)

## Bricks component inventory

The Bricks design system "standardises all UX and UI design elements and
components of UniCredit's digital user touchpoints" (UniCredit / Tangity).
The following inventory is the public reconstruction. Always prefer the
WeAreDesign master components when available.

### 1. Inputs & selections
Text field · Password field · Numeric field · Currency field · Search ·
Textarea · Checkbox · Radio · Switch · Select · Multi-select chip ·
Date picker · IBAN field · Selection card · Stepper

### 2. Actions
Primary button · Secondary button · Tertiary / text button · Icon button ·
Danger button · Link · Action group · Quick actions tile · Floating action
(mobile only)

### 3. Navigation & search
Top bar · Breadcrumbs · Tabs · Sub-tabs · Pagination · Page control · Step
counter · Mega menu · Side navigation · Mobile bottom navigation · Back
button · Carousel

### 4. Overlays
Modal · Confirmation modal · Drawer (right) · Side panel · Bottom sheet
(mobile) · Tooltip · Popover

### 5. Indicators
Progress bar · Spinner · Skeleton loader · Tag / chip · Status indicator
(success / warning / error / info / neutral) · Inline alert · Toast ·
Badge

### 6. Containers
Card (text / visual / suggestion / widget) · Accordion · Hero banner ·
Feature highlight · Editorial block · KPI tile · Data table · List item ·
Empty state · Error state

### 7. Navigation structures
Public website header · Authenticated header · Footer (full / compact) ·
Cookie banner · Locale switcher

### 8. Templates
Login · Sign-up / on-boarding · Dashboard · Account detail · Transaction
list · Transaction detail · Payment / transfer flow · Investment hub ·
Form template · Editorial / marketing landing · Error pages (404 / 500 /
session expired)

**Rule for the framework agent**: pick the closest Bricks component
before designing anything custom. If a custom component is unavoidable,
flag the gap with `// TODO: bricks-gap — confirm with WeAreDesign before
go-live`.

---

## Component primer (CSS samples ready to adapt)

### Primary button

```css
.uc-btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--uc-space-xs);
  padding: 0.75rem 1.5rem;          /* 12 / 24 */
  min-height: 44px;                  /* WCAG 2.5.5 target size */
  font-family: var(--uc-font-family);
  font-size: var(--uc-fs-base);
  font-weight: var(--uc-fw-semi);
  line-height: 1;
  color: var(--uc-color-on-primary);
  background: var(--uc-color-primary);
  border: 1px solid transparent;
  border-radius: var(--uc-radius-md);
  cursor: pointer;
  transition: background var(--uc-motion-fast),
              box-shadow var(--uc-motion-fast),
              transform var(--uc-motion-fast);
}
.uc-btn-primary:hover  { background: var(--uc-color-red-darker); }
.uc-btn-primary:focus-visible { outline: none; box-shadow: var(--uc-focus-ring); }
.uc-btn-primary:active { transform: translateY(1px); }
.uc-btn-primary[disabled] {
  background: var(--uc-color-neutral-300);
  color: var(--uc-color-neutral-500);
  cursor: not-allowed;
}
```

### Card

```css
.uc-card {
  background: var(--uc-color-bg);
  border: 1px solid var(--uc-color-border);
  border-radius: var(--uc-radius-lg);
  padding: var(--uc-space-lg);
  box-shadow: var(--uc-shadow-sm);
}
.uc-card__title {
  font-size: var(--uc-fs-h4);
  font-weight: var(--uc-fw-bold);
  color: var(--uc-color-text);
  margin-bottom: var(--uc-space-sm);
}
```

### Input field

```css
.uc-field { display: flex; flex-direction: column; gap: var(--uc-space-2xs); }
.uc-field__label {
  font-size: var(--uc-fs-sm);
  font-weight: var(--uc-fw-medium);
  color: var(--uc-color-text);
}
.uc-field__input {
  font-family: var(--uc-font-family);
  font-size: var(--uc-fs-base);
  min-height: 44px;
  padding: 0.5rem 0.75rem;
  color: var(--uc-color-text);
  background: var(--uc-color-bg);
  border: 1px solid var(--uc-color-border);
  border-radius: var(--uc-radius-md);
  transition: border-color var(--uc-motion-fast), box-shadow var(--uc-motion-fast);
}
.uc-field__input:focus-visible {
  outline: none;
  border-color: var(--uc-color-primary);
  box-shadow: var(--uc-focus-ring);
}
.uc-field--error .uc-field__input { border-color: var(--uc-color-error); }
.uc-field__error {
  font-size: var(--uc-fs-xs);
  color: var(--uc-color-error);
}
```

### Focus ring (apply globally)

```css
*:focus-visible {
  outline: none;
  box-shadow: var(--uc-focus-ring);
}
```

---
