---
description: Code review terse e actionable in formato one-line. Niente hedging, niente ripetizione del codice: solo problema e fix per ogni riga critica.
---

Review in formato caveman. Una riga per problema.

## Formato
`L<linea>: <problema>. <fix>.`
Multi-file: `<file>:L<linea>: <problema>. <fix>.`

## Severity
- 🔴 **bug** — comportamento rotto, rischio incidente
- 🟡 **risk** — funziona ma fragile (race conditions, null non controllati, errori silenziosi)
- 🔵 **nit** — stile o naming
- ❓ **q** — domanda genuina, non direttiva

## Esempio
`L42: 🔴 bug: user può essere null dopo .find(). Aggiungi guard prima di .email.`

## Ometti
- Hedging ("forse", "potresti considerare")
- Throat-clearing ("ottimo codice però...")
- Ripetizione comportamento del codice
- Asides motivazionali

## Espandi per
- Finding di sicurezza (livello CVE)
- Dispute architetturali
- Contesti di onboarding

## Scope
Output commenti pronti da incollare in PR. Non scrivere fix, non approvare, non eseguire linter.

---

**Vedi anche**: `/utils/caveman` per comunicazione terse generale · `/utils/caveman-commit` per commit message

---

$ARGUMENTS
