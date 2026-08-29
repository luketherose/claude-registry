# Output templates — developer-frontend

> Reference doc for `developer-frontend`. Read when producing files to apply
> the per-framework file family rules and the per-file output envelope.

---

## Per-file output envelope

For each file produced or modified:

```
### {filename}.{ts|tsx|vue|html|scss|spec.ts}

[Complete file content — all imports, all types, no placeholder comments]

**Why**: {One sentence on the key decisions made}
**Tests**: {What to test and with which testing tool}
```

If the task requires multiple files (component + styles + test), produce all of
them before summarizing — do not stop after the first file.

---

## Per-framework file expectations (do not deliver fewer)

| Framework | Files per component |
|---|---|
| **Angular** | `.component.ts` + `.component.html` + `.component.scss` + `.component.spec.ts` (4 files, always) |
| React (TSX) | `.tsx` + `.module.scss` (or styled equivalent) + `.test.tsx` |
| Vue 3 | `.vue` (SFC — template/script/style co-located) + `.spec.ts` |
| Qwik | `.tsx` + `.css` (if styles) + `.spec.tsx` |
| Vanilla | `.ts` + `.css` (if styles) + `.spec.ts` |

For Angular specifically: inline `template:` / `styles:` literals are forbidden
(see Angular invariants in `per-framework-conventions.md`). A reply that
delivers an Angular component as a single `.ts` with an inline template fails
the quality self-check.
