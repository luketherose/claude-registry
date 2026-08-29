# functional-analyst: lower-frequency output templates

Read this when the task calls for a business process map, a CRUD matrix, or a
traceability matrix. The two templates used on most runs, the Functional
Requirements Catalog and the Use Case Specification, stay in the agent body.

---

## Business Process Map

Use for end-to-end process documentation.

```
## Process: {Process Name}

**Purpose**: {One sentence, what business outcome this process achieves}
**Scope**: {Start event → End event}
**Process Owner**: {Role responsible for this process}

### Participants
| Role | Responsibility in this process |
|------|-------------------------------|
| ... | ... |

### Process Flow

| Step | Participant | Activity | Input | Output | Business Rules |
|------|-------------|----------|-------|--------|----------------|
| 1 | {Role} | {Verb + noun activity} | {What is needed} | {What is produced} | {BR-NNN} |

### Exception Handling
{Describe what happens when the process cannot continue normally}

### KPIs / Success Metrics
{If known — what the business measures to evaluate this process}
```

## CRUD Matrix

Use when mapping which features interact with which data entities.

```
## CRUD Matrix: {Module Name}

| Feature / Use Case | Entity A | Entity B | Entity C |
|--------------------|----------|----------|----------|
| UC-001: {Name} | C R | R U | - |
| UC-002: {Name} | R | - | C R U D |

Legend: C=Create, R=Read, U=Update, D=Delete, -=No interaction
```

## Traceability Matrix

Use when linking requirements to implementation artifacts.

```
## Traceability Matrix

| Requirement | Use Case | Component / Class | Test Case |
|-------------|----------|-------------------|-----------|
| FR-001 | UC-001 | UserService.resetPassword() | TC-001 |
```
