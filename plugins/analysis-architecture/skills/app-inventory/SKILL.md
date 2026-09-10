---
name: app-inventory
description: "This skill should be used when the user asks for an inventory of an unknown or poorly documented application estate before a decommissioning, a migration, a due diligence or a bid: how many files there are, of which technology, how many scripts and jobs, which applications exist inside a perimeter and where their boundaries fall. Trigger phrases: \"app inventory\", \"inventory the perimeter\", \"how many applications are in here\", \"census of this codebase\", \"application portfolio in Excel\", \"what technologies are in this estate\". Produces a formatted Excel workbook with a TOGAF-shaped portfolio catalogue, a technology and file census, and an optional 7R disposition, backed by scan artifacts that make every figure reproducible. Do not use to analyse the technical health of a single known codebase (that is tech-analyst), to reconstruct what the software does functionally (that is functional-reconstruction), or to build a call graph (that is graphify-code-graph)."
---

# Application inventory

Turn a perimeter nobody has mapped into an audit-grade inventory: an Excel workbook whose
every number can be traced back to a command, plus the scan artifacts that produced it.

The division of labour is the point. Counting files, classifying technologies and drawing
application boundaries are deterministic jobs, and they belong to `scripts/census.py`, which
reads its taxonomy from [taxonomy.json](references/taxonomy.json). Assembling the workbook
belongs to `scripts/build_inventory.py`, which holds the sheet and column schema in code.
What is left for you is the part that actually needs a reader: deciding what an ambiguous
boundary means, reading a script to say what it does, spotting an integration, and proposing
a disposition. Do not recompute in your head what a script already computed exactly.

## Prerequisites

`python3` for the census, and `openpyxl` for the workbook. Check both before promising an
`.xlsx`, because the failure arrives at the end of a long scan otherwise:

```
python3 -c "import openpyxl; print(openpyxl.__version__)"
```

Neither `cloc` nor `ripgrep` is required. The census counts lines itself and records the
method it used in the provenance sheet.

## Hard rules

1. **Read-only on the perimeter.** Never write, move, rename or execute anything inside it.
   All output goes to a directory outside the perimeter, and the census refuses to run when
   `--out` sits inside `--root`.
2. **No invented data.** Every cell is evidence or the literal `UNKNOWN`. Business capability,
   criticality, owner and cost are not in a filesystem: leave them `UNKNOWN` and say so.
3. **Nothing disappears.** Excluded files are counted by rule; pruned directories are declared.
   Run the census with `--count-excluded` when the exact figure inside them matters.
4. **No secret values.** When a file holds a credential, record its presence, its type and its
   path. Never copy the value into the workbook, the logs or your reply.
5. **Reconciliation before delivery.** `build_inventory.py` refuses to write the workbook when
   its five checks do not balance. Do not work around a failure by adjusting a number.

## Phases

### Phase 0: recon, then stop

Run the census in `--dry-run` and present: the perimeter totals, the applications the boundary
rules produced with the rule that fired for each, the top technologies, and anything you find
genuinely ambiguous.

```
python3 scripts/census.py --root <PERIMETER> --out <OUTDIR> --dry-run
```

Then stop and ask the user to confirm or correct the boundaries. A perimeter carved wrongly
produces a workbook that is internally consistent and useless, and the cost of finding out
is the whole scan.

### Phase 1: full census

```
python3 scripts/census.py --root <PERIMETER> --out <OUTDIR> --count-excluded
```

Writes `files.csv`, `apps.json` and `provenance.json`. These are the facts. Everything after
this point reads them rather than re-walking the tree.

### Phase 2: read what only a reader can

Work from `files.csv`, application by application, and write JSON into the scan directory.
Each file is a list of objects whose keys match the sheet columns documented in
[workbook.md](references/workbook.md). A file you do not write is a sheet that is omitted
rather than shipped empty, which is the honest outcome when you had nothing to put in it.

| File | What goes in it |
|---|---|
| `interfaces.json` | inbound and outbound integrations, with the endpoint sanitised |
| `database.json` | schemas, tables, procedures, packages, migration tooling |
| `disposition.json` | the 7R recommendation per application, see below |
| `gaps.json` | risks, gaps, assumptions, ambiguous boundaries, questions for the client |

Read [framework.md](references/framework.md) before writing `disposition.json`, not before.
It carries the TOGAF portfolio view and the 7R rules, and it is the only part of this skill
that needs loading late.

For the scripts sheet, fill `Purpose_Summary` and `Invocation_Method` by reading the script
headers and grepping the perimeter for each filename. An uninvoked script is a finding, not
a blank cell.

### Phase 3: build and verify

```
python3 scripts/build_inventory.py --scan <OUTDIR> --out <FILE>.xlsx --client <C> --project <P> --verify
```

`--verify` reopens the finished file and prints, per sheet, the row and column counts, the
freeze pane, the filter range, the header fill and the first rows as rendered values. Paste
that output to the user. A workbook that was written is not a workbook that reads correctly,
and the difference is exactly what a reader would see on opening it.

## Reporting

Lead with the perimeter measured and the applications found. Then the technology distribution,
then the three findings that most affect the decision the inventory exists to support. Close
with the verification output, the open questions from `gaps.json`, and what you could not
determine and what access would resolve it.

State plainly that the 7R disposition rests on technical evidence alone and needs business
validation. An inventory that hides its own blind spot is worse than one that names it.
