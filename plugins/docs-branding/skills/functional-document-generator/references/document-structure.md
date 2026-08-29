# Functional document structure

The standard chapter and section schema for an enterprise functional document,
used whenever the provided Word template does not fully define one.

If the template does not fully define the structure, use this standard schema for enterprise functional documents:

```
1. Title page
   - Document title
   - Version
   - Date
   - Author / Team
   - Classification (Internal / Confidential / Public)

2. Revision history
   - Table: Version | Date | Author | Change description

3. Table of contents

4. Introduction
   4.1 Purpose of the document
   4.2 Scope of application
   4.3 Intended audience

5. Glossary and Definitions
   - Table: Term | Definition

6. Context and General Description
   6.1 Business context
   6.2 System objectives
   6.3 High-level functional architecture

7. System Actors
   - Table: Actor | Type | Description | Responsibilities

8. Functional Requirements
   8.1 [Module/Feature 1]
       - RF-001: ...
       - RF-002: ...
   8.2 [Module/Feature N]

9. Main Flows
   9.1 [Flow Name 1]
       - Pre-conditions
       - Step-by-step
       - Post-conditions
       - Exceptions / Alternative cases
   9.2 [Flow Name N]

10. Use Cases
    - UC table: ID | Name | Actor | Objective | Main scenario

11. Business Rules
    - BR table: ID | Rule | Context | Violation | Source in code

12. Constraints and Limitations
    12.1 Functional constraints
    12.2 Technical constraints
    12.3 Regulatory / compliance constraints

13. Functional Dependencies Between Modules
    - Table: Module | Depends on | Dependency type | Impact

14. Assumptions and Open Questions
    14.1 Assumptions
    14.2 Open questions / To be validated

15. Appendix
    - References to related documents
    - Additional notes
```

---
