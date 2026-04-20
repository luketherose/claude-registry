# Claude Registry

Infrastruttura di governance per le capability condivise di Claude Code del team.

Il registry permette di definire, revisionare, versionare e distribuire subagent
specializzati — esattamente come una libreria di codice condivisa, ma per il
comportamento di Claude.

---

## Leggi prima la guida operativa

Tutto quello che ti serve per usare o contribuire al registry è nella guida:

```
guida-operativa.pdf   (nella root di questo repository)
```

La guida copre:
- **Parte 1 — Usare le capability**: prerequisiti, installazione con script, verifica, aggiornamento
- **Parte 2 — Contribuire**: creare una nuova capability, scrivere il system prompt, testare, aprire una PR, gestire la review, pubblicare

Se vuoi solo installare le capability nel tuo progetto senza leggere tutto:

```bash
./claude-catalog/scripts/setup-capabilities.sh /path/to/tuo-progetto
```

---

## Struttura del repository

```
claude-registry/
  claude-catalog/          ← sorgente (sviluppo e review)
    agents/                  subagent .md con YAML frontmatter
    skills/                  knowledge provider riutilizzabili (condivisi tra agenti)
    examples/                invocazioni di esempio per capability
    evals/                   scenari di validazione
    hooks/                   script e configurazioni per hook Claude Code
    settings/                reference settings.json per i progetti
    mcp/                     esempi di configurazione MCP server
    policies/                convenzioni residue (non ancora migrate a skill)
    templates/               template di output (ADR, report, API contract)
    docs/                    documentazione interna per i contributori
    scripts/
      setup-capabilities.sh  installa capability in un progetto (risolve dipendenze)
      new-capability.sh      scaffolda una nuova capability o skill
    how-to-write-a-capability.md
    CONTRIBUTING.md
    GOVERNANCE.md
    CHANGELOG.md

  claude-marketplace/      ← distribuzione (solo capability approvate)
    stable/                  capability production-ready
    beta/                    capability nuove o sperimentali
    skills/                  skill condivise (installate automaticamente come dipendenze)
    catalog.json             manifest con versioni, metadati e dipendenze

  guida-operativa.pdf      ← leggi qui
  pitch-claude-registry.pptx
```

---

## Capability disponibili

### Agenti (12)

| Nome | Tier | Descrizione |
|------|------|-------------|
| `software-architect` | stable | Analisi architetturale, ADR, trade-off |
| `functional-analyst` | stable | Requisiti, use case, processi di business |
| `developer-java-spring` | stable | Sviluppo Java/Spring Boot enterprise |
| `technical-analyst` | beta | Debito tecnico, sicurezza, dipendenze vulnerabili |
| `developer-python` | beta | Sviluppo Python/FastAPI |
| `code-reviewer` | beta | Code review strutturata su PR o file modificati |
| `test-writer` | beta | Test JUnit 5, Mockito, Testcontainers, pytest |
| `debugger` | beta | Diagnosi bug da stack trace, log e codice |
| `api-designer` | beta | Design e review API REST, spec OpenAPI |
| `documentation-writer` | beta | README, runbook, guide architetturali |
| `presentation-creator` | beta | Slide Accenture-branded (.pptx) da documenti di progetto |
| `document-creator` | beta | Documenti Accenture-branded (PDF/DOCX) da documenti di progetto |

### Skill (4)

Le skill sono knowledge provider atomici condivisi tra più agenti. Non sono agenti
autonomi: vengono invocati dagli agenti per recuperare standard e convenzioni.
Lo script `setup-capabilities.sh` le installa automaticamente come dipendenze.

| Nome | Usata da | Contenuto |
|------|----------|-----------|
| `java-spring-standards` | developer-java-spring, code-reviewer, test-writer | Struttura pacchetti, layering, testing, error handling, logging, security, Micrometer |
| `testing-standards` | developer-java-spring, test-writer, code-reviewer, developer-python | Principi, tassonomia scenari, naming, JUnit 5 / pytest / Jest template |
| `rest-api-standards` | developer-java-spring, api-designer, code-reviewer | Modellazione risorse, HTTP methods, status code, RFC 7807, OpenAPI 3.1 |
| `accenture-branding` | presentation-creator, document-creator | Palette colori, costanti python-pptx, CSS template PDF, tipografia |

---

## Governance

- Il branch `main` è protetto: ogni modifica passa da Pull Request con review
- GitHub Actions valida struttura e completezza di ogni capability
- Versioning SemVer: PATCH = fix, MINOR = nuovi comportamenti, MAJOR = breaking change
- La promozione da `beta` a `stable` richiede utilizzo in almeno due progetti e 30 giorni senza issue critiche

Dettagli in [`claude-catalog/GOVERNANCE.md`](claude-catalog/GOVERNANCE.md).

---

## Link utili

| Risorsa | Percorso |
|---------|----------|
| Guida operativa (PDF) | [`guida-operativa.pdf`](guida-operativa.pdf) |
| Come scrivere una capability | [`claude-catalog/how-to-write-a-capability.md`](claude-catalog/how-to-write-a-capability.md) |
| Checklist review PR | [`claude-catalog/review-checklist.md`](claude-catalog/review-checklist.md) |
| Processo di release | [`claude-catalog/release-process.md`](claude-catalog/release-process.md) |
| Changelog | [`claude-catalog/CHANGELOG.md`](claude-catalog/CHANGELOG.md) |
| Pitch per il team (PPTX) | [`pitch-claude-registry.pptx`](pitch-claude-registry.pptx) |
