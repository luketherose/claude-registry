"""Prints the layout warnings of every view, tab and flow of a project.

Usage: python3 -I check.py <project_dir> [-v] [ids of views, of flows, or all for the first tab of every tabbed view]
-v adds the positions of labels, badges and zones. Exit code 1 when any warning is left.
"""
import sys
from pathlib import Path

args = [a for a in sys.argv[1:] if a != "-v"]
if not args:
    raise SystemExit(__doc__)
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(args[0]).resolve()))
import views  # noqa: E402
from doc import DOC  # noqa: E402
from render import View, apply_theme  # noqa: E402

apply_theme(DOC.get("theme", "unicredit"))
verbose = "-v" in sys.argv
only = args[1:]
runs = []
for spec in views.VIEWS:
    runs.append((spec, None))
    if spec.get("flows"):
        runs += [(spec, "all")] + [(spec, f) for f in spec["flows"]]
total = 0
for spec, flow in runs:
    overview = flow == "all"
    fid = "all" if overview else flow["id"] if flow else None
    name = spec["id"] + (f"/{fid}" if fid else "")
    if only and spec["id"] not in only and fid not in only:
        continue
    v = View(spec, None if overview else flow, overview=overview)
    v.boundary_svg()
    total += len(v.warnings)
    print("==", name, len(v.warnings))
    for w in v.warnings:
        print("  ", w)
    if verbose:
        for lb in v.labels:
            ed = spec["edges"][lb["idx"]]
            print("    lbl %-10s->%-10s at (%d,%d) w=%d h=%d" % (ed["src"], ed["dst"], lb["x"], lb["y"], lb["w"], lb["h"]))
        for bg in v.badges:
            print("    badge %d on %s at (%d,%d)" % (bg["n"], bg["src"], bg["x"], bg["y"]))
        for z in v.zones:
            print("    zone %s rect %s" % (z["id"], tuple(round(c) for c in z["rect"])))
print("TOTAL", total)
sys.exit(1 if total else 0)
