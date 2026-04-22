---
description: Genera commit message terse e focalizzati sull'intento in formato Conventional Commits. Nessun emoji, nessuna auto-referenzialità, solo sostanza.
---

Genera commit message in formato Conventional Commits.

## Formato
`<type>(<scope>): <imperativo>` — max 50 char, hard cap 72

## Tipi ammessi
feat, fix, refactor, perf, docs, test, chore, build, ci, style, revert

## Regole
- Solo imperativi nel subject
- Body solo se "il perché non è ovvio"
- Priorità al ragionamento, non alla descrizione
- Niente emoji, niente attribuzioni, niente nomi file ripetuti
- Niente frasi auto-referenziali ("This commit does..."), prima persona, crediti AI

## Body obbligatorio per
- Breaking changes
- Fix di sicurezza
- Data migrations
- Reversioni
- Ragionamento non ovvio

## Output
Solo il testo del messaggio in un blocco codice. Non eseguire git, non fare staging.

---

**Vedi anche**: `/utils/caveman` per comunicazione terse generale · `/utils/caveman-review` per code review one-line

---

$ARGUMENTS
