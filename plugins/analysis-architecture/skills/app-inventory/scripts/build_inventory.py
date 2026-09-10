#!/usr/bin/env python3
"""Build the app inventory workbook from the census artifacts. Needs openpyxl.

The sheet and column schema lives here, in code, not in the prompt: a column
list an agent has to remember is a column list an agent can paraphrase away.
Enrichment that only a reader can supply (interfaces, database objects,
disposition) is picked up from optional JSON files in the scan directory, and a
sheet is omitted rather than shipped empty when its file is absent.
"""
import argparse, csv, json, os, sys
from collections import defaultdict

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
except ImportError:
    sys.exit("ERROR: openpyxl is not installed. Run: pip install openpyxl")

HEADER_FILL = PatternFill(start_color="1F3864", end_color="1F3864", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF")
WRAP = Alignment(wrap_text=True, vertical="top")
WIDE = {"Notes", "Rationale", "Description", "Evidence_Path", "Purpose_Summary",
        "Key_Risks", "Question_For_Client", "Covers_Summary", "Command"}

ENRICHMENT = {
    "08_Interfaces": ("interfaces.json", ["Interface_ID", "App_ID", "Direction", "Interface_Type",
        "Protocol", "Endpoint_Sanitized", "Counterpart_System", "Data_Format", "Defined_In_File",
        "Evidence_Path", "Confidence"]),
    "09_Database_Objects": ("database.json", ["DB_Object_ID", "App_ID", "DB_Engine", "Schema_Name",
        "Object_Type", "Object_Name", "Defined_In_File", "Migration_Tool", "Evidence_Path", "Confidence"]),
    "10_Disposition_7R": ("disposition.json", ["App_ID", "Application_Name", "Recommended_R",
        "Alternative_R", "Rationale", "Technical_Complexity", "Integration_Fan_Out", "Effort_Band",
        "Suggested_Wave", "Key_Risks", "Confidence"]),
    "11_Risks_Gaps": ("gaps.json", ["ID", "Type", "Scope", "App_ID", "Description",
        "Impact_On_Completeness", "Evidence_Path", "Question_For_Client"]),
}

def sheet(wb, title, headers, rows, freeze="B2"):
    ws = wb.create_sheet(title)
    ws.append(headers)
    for c in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=c)
        cell.fill, cell.font = HEADER_FILL, HEADER_FONT
        cell.alignment = Alignment(vertical="center")
    for r in rows:
        ws.append(r)
    ws.freeze_panes = freeze
    if rows:
        ws.auto_filter.ref = "A1:%s%d" % (get_column_letter(len(headers)), len(rows) + 1)
    for i, h in enumerate(headers, 1):
        width = 60 if h in WIDE else max(11, min(34, len(h) + 4))
        ws.column_dimensions[get_column_letter(i)].width = width
        if h in WIDE:
            for r in range(2, len(rows) + 2):
                ws.cell(row=r, column=i).alignment = WRAP
    return ws

def main():
    ap = argparse.ArgumentParser(description="Assemble the inventory workbook.")
    ap.add_argument("--scan", required=True, help="directory written by census.py")
    ap.add_argument("--out", required=True, help="path of the .xlsx to write")
    ap.add_argument("--client", default="UNKNOWN")
    ap.add_argument("--project", default="UNKNOWN")
    ap.add_argument("--max-raw-rows", type=int, default=200000)
    ap.add_argument("--verify", action="store_true", help="reopen the finished file and print evidence")
    args = ap.parse_args()

    scan = os.path.abspath(args.scan)
    apps = json.load(open(os.path.join(scan, "apps.json"), encoding="utf-8"))
    prov = json.load(open(os.path.join(scan, "provenance.json"), encoding="utf-8"))
    with open(os.path.join(scan, "files.csv"), encoding="utf-8") as fh:
        files = list(csv.DictReader(fh))

    by_root = {a["app_root"]: a for a in apps}
    def app_id(root):
        return by_root.get(root if root != "(root)" else "", {}).get("app_id", "UNASSIGNED")

    fam_agg, inv_agg, mtimes = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0, 0, 0, 0]), defaultdict(list)
    scripts, total_loc = [], 0
    for f in files:
        loc, size = int(f["code_loc"]), int(f["bytes"])
        total_loc += loc
        aid = app_id(f["app_root"])
        fam_agg[(aid, f["family"])][0] += 1
        fam_agg[(aid, f["family"])][1] += loc
        k = (aid, f["ext"] or "(none)", f["family"], f["asset_class"])
        inv_agg[k][0] += 1; inv_agg[k][1] += loc
        inv_agg[k][2] += int(f["comment_loc"]); inv_agg[k][3] += int(f["blank_loc"]); inv_agg[k][4] += size
        if f["mtime"]:
            mtimes[aid].append(f["mtime"])
        if f["asset_class"] == "SCRIPT":
            scripts.append([("SCR-%04d" % (len(scripts) + 1)), aid, f["path"], f["family"],
                            "", "", loc, f["mtime"], f["path"], "Low"])

    wb = Workbook(); wb.remove(wb.active)

    sheet(wb, "00_Methodology", ["Topic", "Statement"], [
        ["Framework", "TOGAF application portfolio catalogue for identity, plus a 7R disposition derived from technical evidence only."],
        ["Business layer", "Business capability, criticality, owner and cost are not derivable from a filesystem. They are UNKNOWN here and require business validation."],
        ["Boundary rules", "R1 build or deploy manifest, R2 version control root, R6 leftover top-level directory, R7 loose files at the perimeter root. The rule that fired is recorded per application."],
        ["LOC method", prov.get("loc_method", "UNKNOWN") + ". Code lines are physical lines minus blank and comment lines."],
        ["Document binaries", "PDF, Office and data binaries are counted as files and bytes and never line counted."],
        ["Pruned directories", "Directory exclusions are reported by rule in 07_Scan_Provenance. Their contents are counted only when the census ran with --count-excluded."],
        ["Enrichment sheets", "Interfaces, database objects, disposition and gaps come from JSON written during the reading phase. A sheet whose file is absent is omitted rather than shipped empty."],
        ["Taxonomy version", str(prov.get("taxonomy_version", "UNKNOWN"))],
    ], freeze="A2")

    classes = sorted({f["asset_class"] for f in files})
    summary = [["Applications identified", len(apps), "count", "boundary rules in 00_Methodology"],
               ["Files seen", prov["files_seen"], "count", "in scope plus excluded"],
               ["Files in scope", prov["files_in_scope"], "count", ""],
               ["Files excluded", prov["files_excluded"], "count", "by rule, see 07_Scan_Provenance"],
               ["Code lines in scope", total_loc, "lines", prov.get("loc_method", "")],
               ["Bytes in scope", sum(int(f["bytes"]) for f in files), "bytes", ""],
               ["Distinct technologies", len({f["family"] for f in files}), "count", ""],
               ["Scripts", len(scripts), "count", "asset class SCRIPT"]]
    for c in classes:
        summary.append(["Files of class %s" % c, sum(1 for f in files if f["asset_class"] == c), "count", ""])
    sheet(wb, "01_Executive_Summary", ["Metric", "Value", "Unit", "Notes"], summary, freeze="A2")

    portfolio = []
    for a in apps:
        aid = a["app_id"]
        prim = max(a["families"].items(), key=lambda kv: kv[1])[0] if a["families"] else "UNKNOWN"
        sec = ", ".join(k for k, _ in sorted(a["families"].items(), key=lambda kv: -kv[1])[1:4])
        ts = sorted(mtimes.get(aid, []))
        portfolio.append([aid, a["name"], a["app_root"] or "(perimeter root)", a["boundary_rule"],
                          prim, sec, "UNKNOWN", "UNKNOWN", "UNKNOWN", a["files"], a["loc"], a["bytes"],
                          a["classes"].get("SOURCE", 0), a["classes"].get("SCRIPT", 0),
                          a["classes"].get("CONFIG", 0), a["classes"].get("TEST", 0),
                          a["classes"].get("DOC", 0), a["classes"].get("DB", 0),
                          "Y" if a["classes"].get("TEST") else "N",
                          ts[0] if ts else "", ts[-1] if ts else ""])
    sheet(wb, "02_Application_Portfolio", ["App_ID", "Application_Name", "Root_Path", "Boundary_Rule",
        "Primary_Technology", "Secondary_Technologies", "Business_Capability", "Business_Criticality",
        "Owner", "Total_Files", "Total_LOC", "Total_Bytes", "Source_Files", "Script_Files",
        "Config_Files", "Test_Files", "Doc_Files", "DB_Files", "Has_Tests",
        "Oldest_File_Date", "Newest_File_Date"], portfolio, freeze="C2")

    app_loc = {a["app_id"]: a["loc"] for a in apps}
    tech = []
    for (aid, fam), (n, loc) in sorted(fam_agg.items()):
        share = round(100.0 * loc / app_loc[aid], 1) if app_loc.get(aid) else 0.0
        tech.append([aid, fam, "UNKNOWN", "UNKNOWN", n, loc, share])
    sheet(wb, "03_Technology_Stack", ["App_ID", "Technology_Family", "Detected_Version",
        "Support_Status", "File_Count", "Code_LOC", "Share_Of_App_LOC_Pct"], tech)

    inv = [[a, e, f, c, v[0], v[1], v[2], v[3], v[4]] for (a, e, f, c), v in sorted(inv_agg.items())]
    sheet(wb, "04_File_Inventory", ["App_ID", "File_Extension", "Technology_Family", "Asset_Class",
        "File_Count", "Code_LOC", "Comment_LOC", "Blank_LOC", "Total_Bytes"], inv)

    if scripts:
        sheet(wb, "05_Scripts", ["Script_ID", "App_ID", "File_Path", "Script_Type", "Purpose_Summary",
            "Invocation_Method", "Code_LOC", "Last_Modified", "Evidence_Path", "Confidence"], scripts)

    omitted = []
    for title, (fname, headers) in sorted(ENRICHMENT.items()):
        path = os.path.join(scan, fname)
        if os.path.isfile(path):
            data = json.load(open(path, encoding="utf-8"))
            sheet(wb, title, headers, [[row.get(h, "") for h in headers] for row in data])
        else:
            omitted.append("%s (no %s)" % (title, fname))

    raw = [[f["path"], app_id(f["app_root"]), f["ext"], f["family"], f["asset_class"],
            int(f["bytes"]), int(f["code_loc"]), f["mtime"]] for f in files[:args.max_raw_rows]]
    sheet(wb, "06_Raw_File_Index", ["File_Path", "App_ID", "Extension", "Technology_Family",
        "Asset_Class", "Bytes", "Code_LOC", "Mtime"], raw)

    pv = [["root", prov["root"]], ["generated_utc", prov["generated_utc"]],
          ["host_os", prov["host_os"]], ["python", prov["python"]],
          ["duration_sec", prov["duration_sec"]], ["client", args.client], ["project", args.project]]
    for k, v in sorted(prov.get("exclusions", {}).items()):
        pv.append(["excluded by %s" % k, v])
    for k, v in sorted(prov.get("pruned_directories", {}).items()):
        pv.append(["pruned directories %s" % k, v])
    pf = prov.get("pruned_directory_files")
    if isinstance(pf, dict):
        for k, v in sorted(pf.items()):
            pv.append(["files inside pruned %s" % k, v])
    else:
        pv.append(["files inside pruned directories", str(pf)])
    if omitted:
        pv.append(["sheets omitted", "; ".join(omitted)])
    if len(files) > args.max_raw_rows:
        pv.append(["raw index truncated", "%d of %d rows" % (args.max_raw_rows, len(files))])
    sheet(wb, "07_Scan_Provenance", ["Item", "Value"], pv, freeze="A2")

    checks = []
    checks.append(("R1 in scope equals rows in raw index",
                   prov["files_in_scope"], len(files)))
    checks.append(("R2 seen equals in scope plus excluded",
                   prov["files_seen"], prov["files_in_scope"] + prov["files_excluded"]))
    checks.append(("R3 portfolio files equal files in scope",
                   sum(a["files"] for a in apps), prov["files_in_scope"]))
    checks.append(("R4 portfolio LOC equals inventory LOC",
                   sum(a["loc"] for a in apps), total_loc))
    checks.append(("R5 every file has a known App_ID",
                   0, sum(1 for f in files if app_id(f["app_root"]) == "UNASSIGNED")))
    failed = [c for c in checks if c[1] != c[2]]
    for name, a, b in checks:
        print("%-46s %s  (%s vs %s)" % (name, "PASS" if a == b else "FAIL", a, b))
    if failed:
        sys.exit("ERROR: %d reconciliation check(s) failed; the workbook was not written." % len(failed))

    wb.save(args.out)
    print("written %s (%d bytes)" % (args.out, os.path.getsize(args.out)))
    if args.verify:
        verify(args.out)

def verify(path):
    wb = load_workbook(path)
    print("\n=== VERIFICATION, reopened from disk ===")
    for ws in wb.worksheets:
        rows = ws.max_row - 1
        print("\n--- %s: %d data rows x %d cols | freeze=%s | filter=%s ---"
              % (ws.title, rows, ws.max_column, ws.freeze_panes, ws.auto_filter.ref))
        if rows < 1:
            print("    EMPTY SHEET")
            continue
        fill = ws.cell(row=1, column=1).fill.start_color.rgb
        print("    header fill A1 = %s" % fill)
        for r in ws.iter_rows(min_row=1, max_row=min(11, ws.max_row), max_col=min(15, ws.max_column),
                              values_only=True):
            cells = ["" if v is None else str(v) for v in r]
            print("    | " + " | ".join(c[:22] for c in cells))

if __name__ == "__main__":
    main()
