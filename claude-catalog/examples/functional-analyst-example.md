# Example: functional-analyst

## Scenario 1: Extract requirements from existing code

**Setup**: A Python codebase with no formal requirements documentation. The team is preparing for a migration and needs to know what the system actually does.

**User prompt**:
> We have this Streamlit app and no docs. Reconstruct the functional requirements before we plan the migration.

**What the subagent does**:
1. Loads `analysis/functional-reconstruction` skill for the methodology
2. Walks the codebase: pages, services, business logic
3. Produces structured artifacts in `docs/functional/`:
   - **Feature inventory**: every distinct feature the system supports, with the entry point and the user-facing outcome
   - **User flows**: step-by-step traces of how a user accomplishes each feature
   - **Business rules**: extracted from conditional branches and validation code
   - **Actors and boundaries**: who triggers what, what external systems are touched
4. Flags ambiguities (functions with unclear purpose, branches with magic numbers and no comment)

**What the subagent does NOT do**:
- Make architecture recommendations (delegates to `software-architect`)
- Write replacement code (delegates to developer subagents)
- Invent requirements not supported by the source

---

## Scenario 2: Acceptance criteria from a user story

**User prompt**:
> "As a customer, I want to download my invoice as PDF." Write acceptance criteria.

**What the subagent does**:
1. Asks one clarifying question if any precondition is unclear (e.g., authenticated user only? guest access?)
2. Produces criteria in Given-When-Then format
3. Covers: happy path, edge cases (invoice doesn't exist, customer doesn't own invoice), failure modes (PDF generation fails)
4. Notes non-functional implications (PDF size limits, generation timeout, audit trail)
5. Tags each criterion with priority (must-have / should-have / could-have)

**Expected output**:
```
Given an authenticated customer with at least one invoice
When the customer requests download for invoice <id> they own
Then a PDF is returned with HTTP 200
And the PDF contains: invoice number, customer details, line items, totals, footer

Given an authenticated customer
When the customer requests download for an invoice they do not own
Then HTTP 403 is returned
And no PDF is produced
```

---

## Scenario 3: CRUD matrix and traceability

**User prompt**:
> Build a CRUD matrix mapping our entities (Customer, Invoice, Allocation) to user roles (Admin, AccountManager, Customer).

**What the subagent does**:
1. Reads the codebase to identify entities and existing access checks
2. Produces a CRUD matrix table: entity × role × operation (C/R/U/D)
3. Annotates cells with the source of the rule (controller annotation, service guard, missing → flagged as gap)
4. Flags inconsistencies (e.g., Admin can read Customer but not delete; check whether intentional)
5. Provides traceability: each matrix cell links back to the source file:line where the rule is enforced
