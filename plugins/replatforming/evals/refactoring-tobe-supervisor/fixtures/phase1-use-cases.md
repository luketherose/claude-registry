---
phase: 1
artefact: use-cases
source: docs/analysis/01-functional/06-use-cases/
status: complete
---

# Use cases (AS-IS)

## UC-01 Place order

- status: confirmed
- actors: Customer
- evidence_ids: [EV-0012, EV-0031]
- screens: orders.py

## UC-02 Issue invoice

- status: confirmed
- actors: Billing clerk
- evidence_ids: [EV-0044]
- screens: billing.py

## UC-03 Run monthly report

- status: confirmed
- actors: Analyst
- evidence_ids: [EV-0058, EV-0061]
- screens: reporting.py

## UC-04 Export ledger for the tax authority

- status: candidate_not_confirmed
- actors: Administrator
- evidence_ids: []
- screens: legacy_export.py
- entry: `?admin=true` query parameter
