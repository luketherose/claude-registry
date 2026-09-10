# The workbook, sheet by sheet

## Contents

- [Sheets built from the census](#sheets-built-from-the-census)
- [Sheets built from your reading](#sheets-built-from-your-reading)
- [Why the schema lives in code](#why-the-schema-lives-in-code)
- [The reconciliation rules](#the-reconciliation-rules)

## Sheets built from the census

Deterministic, produced from `files.csv`, `apps.json` and `provenance.json` with no reading.

| Sheet | One row per |
|---|---|
| `00_Methodology` | statement about how the inventory was produced |
| `01_Executive_Summary` | metric, with its unit and a note |
| `02_Application_Portfolio` | application component |
| `03_Technology_Stack` | application and technology family pair |
| `04_File_Inventory` | application, extension, family and asset class combination |
| `05_Scripts` | file of asset class SCRIPT |
| `06_Raw_File_Index` | file in scope, capped by `--max-raw-rows` |
| `07_Scan_Provenance` | fact about the run, including every exclusion by rule |

## Sheets built from your reading

Written as JSON into the scan directory during phase 2. Each file is a list of objects; the keys
below are exact, and a key that does not match is dropped silently into an empty cell.

`interfaces.json`: `Interface_ID`, `App_ID`, `Direction`, `Interface_Type`, `Protocol`,
`Endpoint_Sanitized`, `Counterpart_System`, `Data_Format`, `Defined_In_File`, `Evidence_Path`,
`Confidence`.

`database.json`: `DB_Object_ID`, `App_ID`, `DB_Engine`, `Schema_Name`, `Object_Type`,
`Object_Name`, `Defined_In_File`, `Migration_Tool`, `Evidence_Path`, `Confidence`.

`disposition.json`: `App_ID`, `Application_Name`, `Recommended_R`, `Alternative_R`, `Rationale`,
`Technical_Complexity`, `Integration_Fan_Out`, `Effort_Band`, `Suggested_Wave`, `Key_Risks`,
`Confidence`.

`gaps.json`: `ID`, `Type`, `Scope`, `App_ID`, `Description`, `Impact_On_Completeness`,
`Evidence_Path`, `Question_For_Client`.

An absent file omits its sheet and records the omission in `07_Scan_Provenance`. That is
deliberate: an empty sheet with a header row reads as "we looked and found nothing", which is a
different claim from "we did not look".

## Why the schema lives in code

The column lists are in `build_inventory.py` rather than in a configuration file or in the skill
body. A schema an agent has to hold in context is a schema an agent can paraphrase, reorder or
drop a column from, and nothing errors when it does. In code the schema is executable, and the
reconciliation checks below run against it every time.

## The reconciliation rules

The builder refuses to write the workbook when any of these fails, and prints both numbers:

1. Files in scope equals the row count of the raw index.
2. Files seen equals files in scope plus files excluded.
3. The sum of per-application file counts equals files in scope.
4. The sum of per-application code lines equals the inventory total.
5. Every file in scope resolves to a known App_ID.

A failure means the census and the workbook disagree about the perimeter. Fix the cause; never
adjust a number to make a check pass.
