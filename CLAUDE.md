# CLAUDE.md — Claude Registry

Istruzioni per Claude Code quando lavora in questo repository.

---

## Regola principale: aggiorna sempre la documentazione

**Ogni volta che apporti una modifica a questo repository, aggiorna anche la documentazione.**

In pratica:

| Tipo di modifica | Cosa aggiornare |
|-----------------|----------------|
| Aggiunta di un nuovo agente (`agents/*.md`) | `README.md` (tabella capability), `claude-catalog/docs/quick-start.md` (tabella), `CHANGELOG.md` ([Unreleased]), `catalog.json` |
| Aggiunta di una nuova skill (`skills/*.md`) | `README.md` (tabella skill), `CHANGELOG.md` ([Unreleased]), `catalog.json` (entry skill + dependencies degli agenti che la usano) |
| Modifica comportamento di un agente esistente | `CHANGELOG.md` ([Unreleased] con bump versione), `catalog.json` (version) |
| Modifica a uno script (`scripts/`) | Commento in testa allo script (utilizzo), `guida-operativa.pdf` se cambia UX |
| Modifica a governance o processi | File `.md` corrispondente in `claude-catalog/` |
| Qualsiasi modifica significativa | `guida-operativa.pdf` e `pitch-claude-registry.pptx` se il contenuto diventa stale |

**Regola specifica per `CHANGELOG.md`**: ogni PR deve avere una voce sotto `[Unreleased]`
prima di essere aperta. Se la voce manca, aggiungila prima di fare push.

**Regola specifica per `catalog.json`**: il file in `claude-marketplace/catalog.json` è
il manifest autoritativo. Quando cambia una capability (versione, dipendenze, descrizione),
aggiorna anche `catalog.json`.

---

## Struttura del repository

- `claude-catalog/` — sorgente di sviluppo (agenti, skill, documenti di governance)
- `claude-marketplace/` — distribuzione (solo file approvati; non modificare direttamente)
- `guida-operativa.pdf` — guida operativa Accenture-branded (rigenerare con `document-creator`)
- `pitch-claude-registry.pptx` — pitch deck Accenture-branded (rigenerare con `presentation-creator`)

---

## Capability disponibili in questo progetto

Questo repository ha le proprie capability installate in `.claude/agents/`.
Usale quando appropriate:

- `document-creator` — per rigenerare `guida-operativa.pdf`
- `presentation-creator` — per rigenerare `pitch-claude-registry.pptx`
- `software-architect` — per decisioni architetturali sul registry stesso
- `documentation-writer` — per aggiornare `.md` di governance e guide

---

## Convenzioni

- Linguaggio: italiano per documentazione utente, inglese per system prompt delle capability
- Nomi file capability: `kebab-case`, senza versione nel nome (`developer-java-spring.md`, non `developer-java-spring-v1.md`)
- Versioning: SemVer con git tag `name@MAJOR.MINOR.PATCH`
- Skills: `model: haiku`, `tools: Read` — non aggiungere altri tool senza giustificazione in PR
