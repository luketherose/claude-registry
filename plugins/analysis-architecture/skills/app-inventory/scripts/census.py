#!/usr/bin/env python3
"""Deterministic file census for app-inventory. Standard library only.

Reads a perimeter, classifies every file against references/taxonomy.json,
assigns each file to exactly one application component, and writes the scan
artifacts that build_inventory.py turns into a workbook.

Read-only: it opens files for reading and writes only under --out.
"""
import argparse, csv, fnmatch, json, os, platform, subprocess, sys, time

COMMENT_PREFIX = {
    "python": ("#",), "shell": ("#",), "ruby": ("#",), "infra": ("#",),
    "java_jvm": ("//", "*"), "dotnet": ("//", "*"), "javascript": ("//", "*"),
    "typescript": ("//", "*"), "go": ("//",), "rust": ("//",), "c_cpp": ("//", "*"),
    "php": ("//", "#", "*"), "database": ("--",), "mainframe": ("*",),
}

def load_taxonomy(path):
    with open(path, encoding="utf-8") as fh:
        tx = json.load(fh)
    ext_map = {}
    for fam, spec in tx["families"].items():
        for e in spec["ext"]:
            ext_map[e] = (fam, spec["class"])
    tx["_ext_map"] = ext_map
    return tx

def excluded(rel, name, tx):
    """Return the exclusion rule that fires, or None. Nothing is dropped silently."""
    parts = rel.split(os.sep)
    for d in tx["exclusions"]["dirs"]:
        if d in parts[:-1]:
            return "dir:" + d
    if name in tx["exclusions"]["files"]:
        return "file:" + name
    for suf in tx["exclusions"]["suffixes"]:
        if name.endswith(suf):
            return "suffix:" + suf
    return None

def classify(name, rel, tx):
    ext = os.path.splitext(name)[1].lower()
    fam, cls = tx["_ext_map"].get(ext, ("other", "OTHER"))
    if name in tx["marker_files"]:
        cls = "BUILD"
        fam = tx["marker_files"][name]
    low = rel.replace(os.sep, "/").lower()
    if cls == "SOURCE":
        if any(h in low for h in tx["test_path_hints"]) or any(h.lower() in name.lower() for h in tx["test_name_hints"]):
            cls = "TEST"
    return fam, cls

def count_lines(path, fam):
    """Physical lines, blanks and best-effort comments. Method recorded in provenance."""
    prefixes = COMMENT_PREFIX.get(fam, ())
    total = blank = comment = 0
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                total += 1
                s = line.strip()
                if not s:
                    blank += 1
                elif prefixes and s.startswith(prefixes):
                    comment += 1
    except (OSError, UnicodeDecodeError):
        return 0, 0, 0
    return total, blank, comment

def find_app_roots(root, tx):
    """Rules R1 to R7, applied in order, each root recording the rule that fired."""
    cands = {}
    globs = tx["boundary_marker_globs"]
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in tx["exclusions"]["dirs"] or d == ".git"]
        rel = os.path.relpath(dirpath, root)
        rel = "" if rel == "." else rel
        if any(f in tx["boundary_markers"] for f in filenames) or \
           any(fnmatch.fnmatch(f, g) for g in globs for f in filenames):
            cands.setdefault(rel, "R1 build or deploy manifest")
        elif ".git" in dirnames and rel:
            cands.setdefault(rel, "R2 version control root")
        dirnames[:] = [d for d in dirnames if d != ".git"]
    # Shallowest wins: a nested manifest is a module of its parent, not a component.
    kept = {}
    for rel, rule in sorted(cands.items(), key=lambda kv: (kv[0].count(os.sep), kv[0])):
        if rel == "":
            kept[rel] = rule; continue
        if any(rel.startswith(k + os.sep) for k in kept if k != ""):
            continue
        kept[rel] = rule
    return kept

def owner_of(rel_dir, roots):
    """The empty root owns everything only when a real marker put it there.

    Added as the R7 fallback it owns the loose files at the perimeter root and
    nothing else, otherwise the first loose file swallows the whole perimeter
    into one component.
    """
    best, rule = None, None
    root_owns_all = roots.get("", "").startswith(("R1", "R2"))
    for r, ru in roots.items():
        if r == "":
            if (root_owns_all or rel_dir == "") and best is None:
                best, rule = r, ru
        elif rel_dir == r or rel_dir.startswith(r + os.sep):
            if best is None or len(r) > len(best):
                best, rule = r, ru
    return best, rule

def main():
    ap = argparse.ArgumentParser(description="Deterministic file census.")
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--taxonomy", default=os.path.join(os.path.dirname(__file__), "..", "references", "taxonomy.json"))
    ap.add_argument("--dry-run", action="store_true", help="boundaries and totals only, no per-file artifacts")
    ap.add_argument("--count-excluded", action="store_true", help="walk pruned directories to count what they hold")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    out = os.path.abspath(args.out)
    if out.startswith(root + os.sep):
        sys.exit("ERROR: --out is inside --root. The scan would inventory its own output.")
    os.makedirs(out, exist_ok=True)
    tx = load_taxonomy(os.path.abspath(args.taxonomy))
    no_loc = set(tx.get("no_loc_ext", []))
    t0 = time.time()

    roots = find_app_roots(root, tx)
    if not roots:
        roots = {"": "R7 perimeter root, no marker found"}
    apps, rows = {}, []
    seen = excl = 0
    excl_by_rule = {}
    pruned_files = {}

    pruned = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for d in list(dirnames):
            if d in tx["exclusions"]["dirs"]:
                key = "dir:" + d
                pruned[key] = pruned.get(key, 0) + 1
                if args.count_excluded:
                    n = sum(len(fs) for _, _, fs in os.walk(os.path.join(dirpath, d)))
                    pruned_files[key] = pruned_files.get(key, 0) + n
        dirnames[:] = sorted(d for d in dirnames if d not in tx["exclusions"]["dirs"])
        rel_dir = os.path.relpath(dirpath, root)
        rel_dir = "" if rel_dir == "." else rel_dir
        for name in sorted(filenames):
            seen += 1
            rel = os.path.join(rel_dir, name) if rel_dir else name
            rule = excluded(rel, name, tx)
            full = os.path.join(dirpath, name)
            if rule:
                excl += 1
                excl_by_rule[rule] = excl_by_rule.get(rule, 0) + 1
                continue
            app_root, brule = owner_of(rel_dir, roots)
            if app_root is None:
                app_root = rel_dir.split(os.sep)[0] if rel_dir else ""
                brule = "R6 leftover top-level directory" if app_root else "R7 loose file at perimeter root"
                roots.setdefault(app_root, brule)
            fam, cls = classify(name, rel, tx)
            try:
                st = os.lstat(full)
                size, mtime = st.st_size, time.strftime("%Y-%m-%d", time.gmtime(st.st_mtime))
            except OSError:
                size, mtime = 0, ""
            if cls in ("BINARY", "ARCHIVE") or os.path.splitext(name)[1].lower() in no_loc or args.dry_run:
                tot = bl = cm = 0
            else:
                tot, bl, cm = count_lines(full, fam)
            a = apps.setdefault(app_root, {"app_root": app_root, "boundary_rule": brule,
                                           "files": 0, "loc": 0, "bytes": 0, "families": {}, "classes": {}})
            a["files"] += 1; a["bytes"] += size; a["loc"] += max(tot - bl - cm, 0)
            a["families"][fam] = a["families"].get(fam, 0) + 1
            a["classes"][cls] = a["classes"].get(cls, 0) + 1
            rows.append([rel.replace(os.sep, "/"), app_root.replace(os.sep, "/") or "(root)",
                         os.path.splitext(name)[1].lower(), fam, cls, size,
                         max(tot - bl - cm, 0), cm, bl, mtime])

    for i, key in enumerate(sorted(apps), 1):
        apps[key]["app_id"] = "APP-%03d" % i
        apps[key]["name"] = os.path.basename(key) or os.path.basename(root)

    if not args.dry_run:
        with open(os.path.join(out, "files.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["path", "app_root", "ext", "family", "asset_class",
                        "bytes", "code_loc", "comment_loc", "blank_loc", "mtime"])
            w.writerows(rows)
        with open(os.path.join(out, "apps.json"), "w", encoding="utf-8") as fh:
            json.dump(sorted(apps.values(), key=lambda a: a["app_id"]), fh, indent=2)

    prov = {"root": root, "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "host_os": platform.platform(), "python": platform.python_version(),
            "taxonomy_version": tx["version"], "loc_method": "physical lines, stdlib reader",
            "files_seen": seen, "files_excluded": excl, "files_in_scope": len(rows),
            "exclusions": excl_by_rule, "pruned_directories": pruned,
            "pruned_directory_files": pruned_files if pruned_files else
                "not counted, rerun with --count-excluded for exact figures",
            "apps": len(apps), "duration_sec": round(time.time() - t0, 2)}
    with open(os.path.join(out, "provenance.json"), "w", encoding="utf-8") as fh:
        json.dump(prov, fh, indent=2)

    assert seen == len(rows) + excl, "reconciliation failed: seen != in_scope + excluded"
    print("perimeter      %s" % root)
    print("files seen     %d  (in scope %d, excluded %d)" % (seen, len(rows), excl))
    if pruned:
        detail = ", ".join("%s x%d" % (k, v) for k, v in sorted(pruned.items())[:6])
        print("dirs pruned    %d  (%s)" % (sum(pruned.values()), detail))
        if not pruned_files:
            print("               their contents are NOT counted; --count-excluded for exact figures")
    print("applications   %d" % len(apps))
    for a in sorted(apps.values(), key=lambda a: a["app_id"]):
        top = sorted(a["families"].items(), key=lambda kv: -kv[1])[:2]
        print("  %s  %-34s %5d file  %7d loc  %s  [%s]" %
              (a["app_id"], (a["app_root"] or "(root)")[:34], a["files"], a["loc"],
               ", ".join("%s:%d" % t for t in top), a["boundary_rule"].split()[0]))
    print("artifacts      %s" % (out if not args.dry_run else "(dry run, none written)"))

if __name__ == "__main__":
    main()
