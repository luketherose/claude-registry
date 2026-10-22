# Document structure and table catalogue

## Contents

- Mandatory frame
- Runbook profile
- Generic profile
- Table catalogue
- Adapting a catalogue table

## Mandatory frame

Every UniCredit document carries this frame, whatever its type. The checker fails a document
that misses any element marked with a table.

| Position | Element | Table |
|---|---|---|
| Page 1 | Cover: logo, title, subtitle, abstract | Version, Date, Author, Status, Classification |
| Page 2 | Document control: Revision history | Version, Date, Description |
| Page 2 | Document control: Approval | Role, Organisation, Approval scope |
| Page 2 | Document control: Conventions | bullets, no table |
| Page 3 | Contents | TOC field |
| Part I | 1. Purpose, scope and related documents, with 1.1 Purpose, 1.2 Scope, 1.3 Related documents | Document, Relationship |
| Last Part | Risks and contingencies | Risk, Mitigation, Owner |
| Last Part | Open points, the last numbered section | #, Open point, Why it matters, Owner (role) |
| Annexes | Glossary and sources, the last annex | Term, Meaning |

## Runbook profile

The reference document, with its activity generalised as `<activity>` (cutover, migration,
release, failover). Use it whole for any runbook or execution plan: drop a section only when
the activity genuinely has no such content, and say so in Conventions.

**PART I: FRAMEWORK**

1. Purpose, scope and related documents: 1.1 Purpose, 1.2 Scope, 1.3 Related documents
2. Principles: bullets with a bold lead-in, five or so
3. `<Activity>` overview: 3.1 Strategy (paragraph), 3.2 Timeline (Timeline table, then a
   `Note.`), 3.3 Constraints (Constraints table), 3.4 Success criteria (bullets)
4. Roles, responsibilities and communication: 4.1 Roles (Roles table), 4.2 RACI by phase
   (RACI table plus the legend), 4.3 Communication during the `<activity>` (bullets)
5. Entry criteria and plan gate: one paragraph on the gates, then the Entry criteria table

**PART II: EXECUTION**

6. Pre-`<activity>` activities (T-10 to T-1): one paragraph with the governing rule, then the
   Activities table
7. `<Activity>` night (T) and business tests: 7.1 Sequence at a glance (Sequence table, then a
   paragraph on timing), 7.2 Step by step (Activities table), 7.3 Business tests (paragraphs
   with a bold lead-in per option), 7.4 Hypercare and closure (bullets)
8. `<Critical coupled step>`: a paragraph on why it is atomic, the Atomic sequence table, a
   closing sentence on its rollback
9. Asset runbooks: key points: one paragraph, then the Per-asset table

**PART III: CONTROL**

10. Rollback plan: 10.1 Rollback by stage (table), 10.2 Decision authority and triggers,
    10.3 Time limits, 10.4 Point of no return (paragraphs)
11. Verification and acceptance: Verification table, then a paragraph on who tests what
12. Risks and contingencies: Risks table
13. Communication plan: Communication table
14. Open points: Open points table

**ANNEXES**

- Annex A. Calendar for T = `<date>`: Calendar table
- Annex B. Lessons applied in this runbook: Lessons table
- Annex C. Contact and escalation list (template): Contacts table, roles filled, names empty
- Annex D. Glossary and sources: Glossary table

## Generic profile

For a design document, procedure, assessment or plan. Name Part II after the document type.

**PART I: FRAMEWORK**

1. Purpose, scope and related documents (as in the frame)
2. Principles, when the document makes choices a reader must respect
3. Overview: the context and the approach in prose, with a Timeline or Constraints table
   when there are dates or limits
4. Roles and responsibilities: Roles table, and a RACI when more than three parties act

**PART II: DESIGN** (or PROCEDURE, ASSESSMENT, PLAN)

Sections as the content requires. Keep the reference habits: one table per enumerable
subject, a why column next to the what, an evidence column wherever something is checked.

**PART III: CONTROL**

- Verification and acceptance, when the document leads to an execution
- Risks and contingencies
- Open points, last

**ANNEXES**

Optional annexes first (calendar, contacts, lessons), then Glossary and sources, last.

## Table catalogue

Widths are the reference values in cm and sum to the 17.59 cm content width; pass them as
`widths_cm` for a faithful copy, or omit them and let the builder size the columns. Bold
first column is `B`.

| Table | Columns (width cm) | Size | First col |
|---|---|---|---|
| Cover metadata | Version 2.61, Date 3.12, Author 4.25, Status 3.08, Classification 4.50 | standard | regular |
| Revision history | Version 2.19, Date 2.92, Description 12.48 | standard | regular |
| Approval | Role 5.11, Organisation 3.28, Approval scope 9.20 | standard | regular |
| Related documents | Document 7.67, Relationship 9.92 | standard | regular |
| Timeline | Phase 2.74, When 4.20, Content 7.37, Owner 3.28 | standard | B |
| Constraints | Constraint 4.74, Effect on the `<activity>` 12.84 | standard | B |
| Roles | Role 5.84, Responsibility in the `<activity>` 11.75 | compact | B |
| RACI by phase | Phase 3.84, then one column per role, 1.4 to 1.9 each | compact | B, plus legend |
| Entry criteria | # 1.10, Entry criterion 5.09, Why (source) 4.59, Evidence 3.65, Owner 3.17 | compact | B |
| Activities | ID 1.39, Activity 5.38, Why it is done 4.84, Owner (role) 2.28, Exit check · evidence 3.70 | compact | B |
| Sequence at a glance | Step 1.46, Planned 3.47, Activity 9.20, Owner 3.47 | compact | B |
| Atomic sequence | # 1.28, Step 7.67, Why 8.65 | compact | B |
| Per-asset key points | Asset 2.74, Key points in the `<activity>` 8.39, Why 6.46 | compact | B |
| Rollback by stage | Stage reached 5.48, Rollback action 6.90, Complexity 5.22 | compact | B |
| Verification | Level 3.80, What is verified 6.85, By 3.28, Evidence 3.65 | compact | B |
| Risks and contingencies | Risk 6.57, Mitigation 7.73, Owner 3.28 | compact | regular |
| Communication plan | When 2.74, Message 6.94, Audience 4.93, Channel 2.99 | compact | regular |
| Open points | # 0.91, Open point 7.67, Why it matters 5.48, Owner (role) 3.54 | compact | regular |
| Calendar | Relative day 3.28, Date 4.01, Main activities 10.29 | compact | B |
| Lessons applied | Lesson 9.85, Where it is applied 7.73 | compact | regular |
| Contacts and escalation | Role 6.57, Primary 3.65, Backup 3.65, Escalation 3.72 | compact | B |
| Glossary and sources | Term 4.38, Meaning 13.21 | compact | B |

The RACI legend, under the table as a legend block:
`R responsible · A accountable · S supports · C consulted · I informed.`

## Adapting a catalogue table

Change the words in `<activity>` and nothing else in a header. When the content needs a
column the catalogue lacks, add it at the right of the closest table and shrink the widest
text column to keep the total at 17.59 cm. Five columns is the practical ceiling at compact
size; split the table beyond it. The RACI table is the one exception, because its role
columns hold a single letter.
