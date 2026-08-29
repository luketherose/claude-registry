# Progetto Atlas, stima di massima

Versione 0.3, 12 giugno 2026. Fonte: workshop con il team applicativo.

## Effort

| Workstream | Giorni uomo | Note |
|---|---|---|
| Analisi funzionale AS-IS | 25 | include 3 workshop |
| Analisi tecnica AS-IS | 18 | |
| Backend Spring Boot 3 | 120 | 14 moduli |
| Frontend Angular 17 | 95 | 22 schermate |
| Migrazione dati | 30 | Oracle verso Amazon RDS for PostgreSQL |
| Test e collaudo | 45 | |
| **Totale** | **333** | |

## Componenti

| Componente | Tecnologia AS-IS | Tecnologia TO-BE |
|---|---|---|
| UI operatore | Streamlit 1.28 | Angular 17 |
| Motore di calcolo | Python 3.9 | Java 21, Spring Boot 3.2 |
| Database | Oracle 12c | Amazon RDS for PostgreSQL 16 |
| Batch notturno | cron + shell | AWS Batch |

## Rischi noti

| Rischio | Impatto | Probabilità |
|---|---|---|
| Regole di pricing non documentate | Alto | Alta |
| Finestra di fermo produzione limitata a 4 ore | Alto | Media |
