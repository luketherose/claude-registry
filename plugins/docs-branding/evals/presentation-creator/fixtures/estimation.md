# Progetto Atlas, sintesi per lo steering committee

Versione 0.3, 12 giugno 2026.

## Effort e timeline

| Workstream | Giorni uomo | Finestra |
|---|---|---|
| Analisi AS-IS (funzionale + tecnica) | 43 | settimane 1-6 |
| Backend Spring Boot 3 | 120 | settimane 5-22 |
| Frontend Angular 17 | 95 | settimane 8-24 |
| Migrazione dati | 30 | settimane 20-26 |
| Test e collaudo | 45 | settimane 22-30 |
| **Totale** | **333** | **30 settimane** |

## Problema

Il motore di calcolo Streamlit gira su una singola VM, non ha test e le regole
di pricing esistono solo nel codice. Ogni modifica richiede 3 settimane.

## Soluzione proposta

Riscrittura incrementale su Java 21 / Spring Boot 3.2 con frontend Angular 17,
database su Amazon RDS for PostgreSQL 16, batch su AWS Batch.

## Rischi

| Rischio | Impatto | Probabilità |
|---|---|---|
| Regole di pricing non documentate | Alto | Alta |
| Finestra di fermo produzione limitata a 4 ore | Alto | Media |

## Dati non disponibili

Costi cloud ricorrenti, dimensionamento infrastrutturale, piano di formazione.
