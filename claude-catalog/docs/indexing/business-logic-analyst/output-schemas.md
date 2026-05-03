# Business-logic analyst — output schemas

> Reference doc for `business-logic-analyst`. Read at runtime when about to
> emit one of the three output files under `.indexing-kb/07-business-logic/`.

The agent body owns when to write each file and what content qualifies.
This doc is the on-disk shape only — frontmatter and section skeletons to
copy into the `Write` call.

All three files share the frontmatter convention:

```yaml
---
agent: business-logic-analyst
generated: <ISO-8601>
source_files: ["<files inspected>"]
confidence: <high|medium|low>
status: complete
---
```

---

## File 1 — `.indexing-kb/07-business-logic/domain-concepts.md`

```markdown
---
agent: business-logic-analyst
generated: <ISO-8601>
source_files: ["<package paths>"]
confidence: <high|medium|low>
status: complete
---

# Domain concepts

## Glossary
| Concept | Defined in | Key attributes | Description (1 line) |
|---|---|---|---|
| Invoice | billing/models.py:Invoice | id, customer_id, amount, status, issued_at | Issued bill to a customer |
| Allocation | billing/models.py:Allocation | invoice_id, account_id, amount | Maps invoice line to account |

## Concept relationships
<text or mermaid diagram showing how concepts relate>

Example:
- Customer (1) ─── (N) Invoice
- Invoice (1) ─── (N) Allocation
- Allocation (N) ─── (1) Account

## Open questions
- <Concepts referenced but never defined>
- <Multiple definitions of the same name in different packages>
```

---

## File 2 — `.indexing-kb/07-business-logic/validation-rules.md`

```markdown
---
agent: business-logic-analyst
generated: <ISO-8601>
source_files: ["<files with validation>"]
confidence: <high|medium|low>
status: complete
---

# Validation rules

| Entity / Function | Rule | Source | Error message |
|---|---|---|---|
| Invoice | amount > 0 | billing/models.py:23 | "Amount must be positive" |
| Customer | email matches regex | customers/models.py:45 | "Invalid email" |

## Open questions
- <Conditions with no error message>
- <Validators that depend on external state>
```

---

## File 3 — `.indexing-kb/07-business-logic/business-rules.md`

```markdown
---
agent: business-logic-analyst
generated: <ISO-8601>
source_files: ["<files with business logic>"]
confidence: <high|medium|low>
status: complete
---

# Business rules

## Conditional logic with business meaning
| Rule | Source | Condition | Effect |
|---|---|---|---|
| Premium discount | billing/pricing.py:45 | `tier == "premium"` | discount=0.10 |
| Large-order approval | orders/service.py:78 | `amount > 100_000` | requires manager approval |

## State machines

### `Order.status`
| From | To | Trigger | File:line |
|---|---|---|---|
| DRAFT | PENDING | submit() | orders/service.py:120 |
| PENDING | APPROVED | approve() | orders/service.py:140 |
| PENDING | REJECTED | reject() | orders/service.py:155 |
| APPROVED | FULFILLED | fulfill() | orders/service.py:170 |

### `Invoice.status`
...

## Workflows

### `process_payment(invoice_id, amount)`
- File: billing/service.py:200
- Inputs: invoice_id (int), amount (Decimal)
- Steps:
  1. Load invoice from DB
  2. Validate amount matches invoice.amount
  3. Create Payment record
  4. Update Invoice.status to PAID
  5. Send notification to customer
- Outputs: Payment record (returned)

### `apply_pricing_rules(order)`
...

## Magic numbers / hardcoded constants flagged
| Constant | Used as | File:line | Meaning (inferred) |
|---|---|---|---|
| 10_000 | threshold | orders/service.py:78 | Large-order threshold |
| 0.10 | discount | billing/pricing.py:45 | Premium discount rate |

## Open questions
- <Branches with magic numbers and no comment>
- <State transitions that exist as code but no enum value>
- <Workflows with implicit error-handling branches>
```
