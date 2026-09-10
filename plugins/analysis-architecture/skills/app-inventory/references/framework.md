# The portfolio view and the 7R disposition

Read this before writing `disposition.json`, not before starting the scan.

## Contents

- [Two layers, kept reconciled](#two-layers-kept-reconciled)
- [What TOGAF expects and a filesystem cannot give](#what-togaf-expects-and-a-filesystem-cannot-give)
- [The seven dispositions](#the-seven-dispositions)
- [Scoring, and where the numbers come from](#scoring-and-where-the-numbers-come-from)
- [The honesty clause](#the-honesty-clause)

## Two layers, kept reconciled

**Layer A, the technical census.** Physical truth from the filesystem: counts, bytes, lines,
asset classes, technologies, boundaries, timestamps. Produced by `census.py`, never by reading.

**Layer B, the portfolio view.** The TOGAF Phase C artifacts, restricted to what the evidence
supports: an Application Portfolio Catalogue (one row per component, in `02_Application_Portfolio`),
an Application Interaction view (`08_Interfaces`), an application to data relationship
(`09_Database_Objects`), and a Technology Portfolio Catalogue (`03_Technology_Stack`).

The two must agree. Every App_ID in an enrichment file exists in the portfolio sheet, and the
counts in the portfolio come from the census rather than from your reading.

## What TOGAF expects and a filesystem cannot give

Business capability, business process, criticality, owner, cost and lifecycle status are inputs
from the business, not properties of a directory. They stay `UNKNOWN`, and each one becomes a
question in `gaps.json` addressed to whoever can answer it. Inventing a criticality because an
application looks important is the single most damaging thing this skill can do: it is the field
a steering committee will read first and challenge last.

## The seven dispositions

Pick one `Recommended_R` and one `Alternative_R` per application, from technical signals only.

| R | The technical signal that argues for it |
|---|---|
| Retire | no activity, no inbound interface, functionality duplicated by another component |
| Retain | recent activity, healthy stack, no portability blocker, and no reason to move |
| Rehost | portable runtime, few environment assumptions, the estate is moving underneath it |
| Replatform | one blocking dependency (an ancient runtime, a proprietary app server, a local filesystem contract) that is replaceable without touching the domain logic |
| Refactor | the blockers are structural: no tests, no boundaries, framework long past support |
| Repurchase | thin custom code around a commodity capability that a product already covers |
| Relocate | the component moves as a whole with its host, typically a virtualised estate |

Where the evidence does not distinguish two options, say so in `Rationale` and set `Confidence`
to `Low` rather than picking the more impressive one.

## Scoring, and where the numbers come from

Each score is 1 to 5, and each has a stated input so a reader can recompute it:

- `Technical_Complexity`: LOC, count of technology families, depth of the boundary tree.
- `Integration_Fan_Out`: rows in `08_Interfaces` for that App_ID, inbound plus outbound.
- `Data_Gravity`: rows in `09_Database_Objects`, plus data files by bytes.
- `Portability_Blockers`: named blockers, each with an evidence path. Zero blockers is a 1.
- `Activity_Level`: newest and oldest file dates from the portfolio sheet.

`Effort_Band` is S, M, L or XL, derived from complexity and fan-out together, and stated as a
band rather than a number of days: a day estimate from a filesystem scan is a guess wearing a
suit. `Suggested_Wave` orders the work so that no application moves before something it depends
on, which makes `Prerequisite_Apps` the field that actually decides the sequence.

## The honesty clause

Close every disposition report with the same statement: the recommendation rests on technical
evidence alone, the business layer was not available, and the sequence needs validation by
someone who knows what the applications are worth. An inventory that presents a 7R table
without that sentence will be read as a decision rather than as an input.
