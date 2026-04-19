# Claude Registry — Business Case

**Documento per**: Capo di Sezione
**Preparato da**: Team Engineering
**Data**: Aprile 2026

---

## Sintesi Esecutiva

I nostri team usano Claude Code ogni giorno per sviluppo, analisi e revisione.
Oggi ogni sviluppatore costruisce i propri prompt da zero, producendo risultati
di qualità variabile e senza che la conoscenza acquisita si accumuli nel tempo.

**Claude Registry** è l'infrastruttura che trasforma questo scenario: le capability
migliori del team vengono definite, approvate, versionate e rese disponibili a tutti —
esattamente come una libreria di codice condivisa, ma per il comportamento di Claude.

**In tre punti:**

- **Produttività**: uno sviluppatore usa una capability già pronta invece di costruirla;
  la stessa qualità è disponibile a tutti i livelli di seniority.
- **Qualità e governance**: ogni capability passa da review approvata prima di essere
  pubblicata; il comportamento di Claude è prevedibile e tracciabile.
- **Asset aziendale**: la conoscenza di dominio e le best practice del team diventano
  un patrimonio versionato, non si perdono con il turnover.

---

## Il Problema Attuale

Quando un team adotta Claude Code senza struttura condivisa, si creano pattern ricorrenti
che limitano il valore dello strumento:

| Scenario | Conseguenza |
|---|---|
| Ogni sviluppatore scrive il proprio prompt per la code review | Output diversi, nessuno standard di qualità condiviso |
| Un senior definisce un ottimo prompt per l'analisi architetturale | La conoscenza rimane nella sua testa o in un file personale |
| Un nuovo collega inizia a usare Claude Code | Ricomincia da zero, senza capitalizzare l'esperienza del team |
| Claude produce risultati inaspettati su un progetto critico | Nessun modo di capire quale istruzione ha generato il comportamento |
| Il team cambia approccio su un tema (es. standard di logging) | Ogni sviluppatore aggiorna il proprio prompt in modo inconsistente |

**Il costo non è nel tool — è nella mancanza di struttura intorno al tool.**

---

## La Soluzione: Capability Condivise

Una **capability** è una specializzazione di Claude per un ruolo specifico:
*Software Architect*, *Functional Analyst*, *Developer Java/Spring*, *Code Reviewer*, ecc.

Ogni capability:
- Definisce **esattamente** come Claude deve comportarsi in quel ruolo
- Specifica il **formato di output** atteso (ADR, report strutturato, codice con test, ecc.)
- Impone gli **standard del team** (naming conventions, error handling, logging, sicurezza)
- È **aggiornabile** — miglioramenti al prompt vengono distribuiti a tutto il team

Le capability vivono nel **Claude Registry**: un repository Git con due livelli —
*catalog* (sviluppo e revisione interna) e *marketplace* (distribuzione ai team).

---

## I Benefici Chiave

### 1. La seniority diventa scalabile

Oggi la differenza di output tra uno sviluppatore senior e uno junior usando Claude
dipende principalmente da come sanno istruire il tool. Con le capability condivise,
le istruzioni del senior diventano lo standard per tutti.

> Un junior che usa la capability `developer-java-spring` produce codice con
> la stessa struttura architetturale, gli stessi pattern di error handling e
> la stessa copertura di test che produrrebbe un senior che segue le nostre linee guida.

### 2. Onboarding accelerato

Un nuovo membro del team deve solo:
1. Clonare il registry
2. Eseguire uno script di setup
3. Aprire Claude Code

Ha subito a disposizione tutte le capability del team, con gli standard e le convenzioni
già incorporati. Non c'è una settimana di allineamento su "come usiamo Claude qui da noi".

### 3. Qualità consistente e verificabile

Ogni capability pubblicata:
- È passata da una **Pull Request con review** da parte di almeno un membro del team
- Ha superato una **validazione automatica** (GitHub Actions) che verifica struttura,
  completezza e correttezza
- È **versionata** con SemVer: si sa esattamente cosa è cambiato e quando

Se una capability produce output non soddisfacente, si apre una PR, si corregge,
si ripubblica. Tutto il team beneficia del miglioramento.

### 4. Governance e controllo reale

Il branch `main` è protetto: nessuna modifica alle capability arriva in produzione
senza revisione e approvazione esplicita. Il team ha visibilità completa su:

- Chi ha proposto ogni modifica (git history)
- Cosa è cambiato esattamente (diff)
- Quando è stato approvato e da chi (PR history)
- Quale versione ogni progetto sta usando (git tag + catalog.json)

Questo è il livello di governance che ci si aspetta da qualsiasi asset software critico.

### 5. Conoscenza che non si perde

Quando un collega esperto lascia il team o cambia progetto, le sue best practice
restano nel registry. La conoscenza è nell'organizzazione, non nelle persone.

---

## Come Funziona in Pratica

```
Autore scrive capability
        ↓
Pull Request su GitHub
        ↓
GitHub Actions valida automaticamente (struttura, naming, completezza)
        ↓
Review manuale del maintainer
        ↓
Pubblicazione nel marketplace (stable o beta)
        ↓
Il team installa con un comando:
  ./setup-capabilities.sh /path/to/progetto
```

Per un developer che vuole **usare** una capability: copia un file `.md` in
`.claude/agents/` del proprio progetto. Claude Code la riconosce automaticamente.

Per un developer che vuole **contribuire**: crea un branch, esegue lo script di
scaffolding, scrive il prompt, apre una PR. GitHub Actions commenta subito con
eventuali problemi da correggere.

---

## Investimento vs. Ritorno

### Costo di setup (già sostenuto)

Il repository è operativo, le prime 10 capability sono disponibili, la pipeline
di governance è configurata. Non ci sono costi di infrastruttura aggiuntivi:
GitHub (già in uso), Claude Code (già in uso).

### Costo di mantenimento

| Attività | Frequenza | Effort stimato |
|---|---|---|
| Review PR per nuova capability | A richiesta | 30–60 min per PR |
| Aggiornamento capability esistente | Mensile ca. | 20–30 min per aggiornamento |
| Onboarding nuovo membro al registry | Una tantum | 30 min |

### Ritorno atteso

| Scenario | Saving stimato |
|---|---|
| Developer usa capability esistente invece di costruire prompt da zero | 20–40 min per task |
| Eliminazione rework per output di bassa qualità | 1–2h per sprint per developer |
| Onboarding nuovo membro su standard Claude | 1–2 giorni lavorativi |
| Identificazione rapida di regressioni nel comportamento di Claude | Variabile — evita escalation |

Per un team di 5 developer, con 2 capability usate per task al giorno,
il saving stimato è nell'ordine di **2–4 ore/settimana per persona**.

---

## Stato Attuale e Roadmap

### Disponibile oggi

| Capability | Tier | Descrizione |
|---|---|---|
| `software-architect` | Stable | Analisi architetturale, ADR, trade-off |
| `functional-analyst` | Stable | Requisiti, use case, processi di business |
| `developer-java-spring` | Stable | Sviluppo Java/Spring Boot enterprise |
| `technical-analyst` | Beta | Analisi tecnica, debito, sicurezza |
| `developer-python` | Beta | Sviluppo Python/FastAPI |
| `code-reviewer` | Beta | Code review strutturata |
| `test-writer` | Beta | Scrittura test JUnit/pytest |
| `debugger` | Beta | Diagnosi bug |
| `api-designer` | Beta | Design e review API REST/OpenAPI |
| `documentation-writer` | Beta | Documentazione tecnica |

### Prossimi passi proposti

1. **Adozione team**: distribuire le capability ai progetti attivi correnti
2. **Feedback loop**: raccogliere feedback dai developer dopo 2–4 settimane di utilizzo
3. **Promozione beta → stable**: stabilizzare le capability beta sulla base del feedback
4. **Capability di dominio**: sviluppare capability specializzate per i nostri domini
   applicativi specifici (es. `developer-payments`, `analyst-compliance`, ecc.)
5. **Metriche di utilizzo**: aggiungere telemetria leggera per capire quali capability
   vengono usate di più e dove ci sono gap

---

## In Sintesi

Claude Registry non è un progetto sperimentale — è l'infrastruttura di governance
per un tool che il team sta già usando. La domanda non è "vale la pena farlo?"
ma "vogliamo che il valore di Claude Code rimanga frammentato per sviluppatore
o diventi un asset condiviso dell'organizzazione?"

Il registry risponde a questa domanda con concretezza: repository Git, PR reviews,
versioning, automazione. Gli stessi standard che applichiamo al codice, applicati
al comportamento dell'AI che aiuta a produrlo.

---

*Per dettagli tecnici, documentazione operativa e accesso al repository:
`github.com/luketherose/claude-registry`*
