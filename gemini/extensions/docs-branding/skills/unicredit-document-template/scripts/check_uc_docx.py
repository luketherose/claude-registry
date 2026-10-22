#!/usr/bin/env python3
"""Check a DOCX against the UniCredit document template and print what a reader would see.

Prints a rendering summary (page setup, outline, tables), then one line per finding.
ERROR breaks the template; WARN is a deviation to justify.

Exit codes: 0 no ERROR, 1 at least one ERROR, 2 usage or I/O error.
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOKENS = json.loads((HERE.parent / "assets" / "doc-tokens.json").read_text(encoding="utf-8"))
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
FONT = TOKENS["font"]["family"]
COL = TOKENS["colors"]
EM_DASH = chr(0x2014)

REQUIRED_TABLES = {
    "cover metadata": ["Version", "Date", "Author", "Status", "Classification"],
    "revision history": ["Version", "Date", "Description"],
    "approval": ["Role", "Organisation", "Approval scope"],
    "related documents": ["Document", "Relationship"],
    "risks": ["Risk", "Mitigation", "Owner"],
    "open points": ["#", "Open point", "Why it matters", "Owner (role)"],
    "glossary": ["Term", "Meaning"],
}


def load(path):
    from xml.etree import ElementTree as ET
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        doc = ET.fromstring(z.read("word/document.xml"))
        styles = ET.fromstring(z.read("word/styles.xml")) if "word/styles.xml" in names else None
        settings = ET.fromstring(z.read("word/settings.xml")) if "word/settings.xml" in names else None
    return doc, styles, settings


def text_of(el):
    return "".join(t.text or "" for t in el.iter(W + "t"))


def pstyle(p):
    ppr = p.find(W + "pPr")
    if ppr is not None and ppr.find(W + "pStyle") is not None:
        return ppr.find(W + "pStyle").get(W + "val")
    return ""


def style_names(styles):
    out = {}
    if styles is None:
        return out
    for s in styles.iter(W + "style"):
        name = s.find(W + "name")
        out[s.get(W + "styleId")] = name.get(W + "val") if name is not None else s.get(W + "styleId")
    return out


def check(path):
    doc, styles, settings = load(path)
    body = doc.find(W + "body")
    names = style_names(styles)
    errors, warns, view = [], [], []

    # page setup
    sect = body.find(W + "sectPr")
    pg, mar = sect.find(W + "pgSz"), sect.find(W + "pgMar")
    page = TOKENS["page"]
    cm = lambda tw: f"{int(tw) / 567:.2f} cm"
    view.append(f"page {cm(pg.get(W + 'w'))} x {cm(pg.get(W + 'h'))}, margins top {cm(mar.get(W + 'top'))} "
                f"right {cm(mar.get(W + 'right'))} bottom {cm(mar.get(W + 'bottom'))} left {cm(mar.get(W + 'left'))}")
    if (int(pg.get(W + "w")), int(pg.get(W + "h"))) != (page["width"], page["height"]):
        warns.append("page size differs from the template")
    for side in ("top", "bottom", "left", "right"):
        if int(mar.get(W + side)) != page[f"margin_{side}"]:
            errors.append(f"margin {side} is {cm(mar.get(W + side))}, template wants {cm(page['margin_' + side])}")

    # fonts: every explicit Latin font in the body, in the styles the body uses and in the
    # document defaults must be the template font. Unused styles are not rendered, so they are skipped.
    scopes = [(doc, "document")]
    if styles is not None:
        by_id = {s.get(W + "styleId"): s for s in styles.iter(W + "style")}
        used = {e.get(W + "val") for tag in ("pStyle", "rStyle", "tblStyle") for e in doc.iter(W + tag)}
        used |= {s.get(W + "styleId") for s in by_id.values() if s.get(W + "default") == "1"}
        chain = set()
        while used:
            sid = used.pop()
            if sid in chain or sid not in by_id:
                continue
            chain.add(sid)
            for rel in ("basedOn", "link"):
                e = by_id[sid].find(W + rel)
                if e is not None:
                    used.add(e.get(W + "val"))
        scopes += [(by_id[sid], f"style {sid}") for sid in sorted(chain)]
        dd = styles.find(W + "docDefaults")
        if dd is not None:
            scopes.append((dd, "document defaults"))
    for root, where in scopes:
        bad = set()
        for rf in root.iter(W + "rFonts"):
            for attr in ("ascii", "hAnsi"):
                v = rf.get(W + attr)
                if v and v != FONT:
                    bad.add(v)
            if rf.get(W + "asciiTheme") or rf.get(W + "hAnsiTheme"):
                bad.add("theme font")
        if bad:
            errors.append(f"{where}: fonts other than {FONT}: {sorted(bad)}")

    # colours, fills, borders
    allowed_text = {COL["text"], COL["secondary"], COL["accent"], "auto"}
    used = {c.get(W + "val") for c in doc.iter(W + "color")}
    if used - allowed_text:
        errors.append(f"text colours outside the palette: {sorted(used - allowed_text)}")
    fills = {s.get(W + "fill") for s in doc.iter(W + "shd")} - {None, "auto"}
    if fills - {COL["table_header_fill"]}:
        errors.append(f"fills outside the palette: {sorted(fills - {COL['table_header_fill']})}")
    bcols = set()
    for tag in ("top", "bottom", "left", "right", "insideH", "insideV"):
        for b in doc.iter(W + tag):
            if b.get(W + "color"):
                bcols.add(b.get(W + "color"))
    if bcols - {COL["table_border"], COL["accent"], "auto"}:
        errors.append(f"border colours outside the palette: {sorted(bcols - {COL['table_border'], COL['accent'], 'auto'})}")
    sizes = {int(s.get(W + "val")) / 2 for s in doc.iter(W + "sz")}
    odd = sorted(sizes - set(TOKENS["allowed_font_sizes_pt"]))
    if odd:
        warns.append(f"font sizes outside the scale: {odd}")

    # text rules
    alltext = text_of(body)
    if EM_DASH in alltext:
        errors.append(f"em dash used as punctuation: {alltext.count(EM_DASH)} occurrence(s)")
    if "--" in alltext:
        warns.append("double hyphen in text")

    paras = [el for el in body if el.tag == W + "p"]
    tables = [el for el in body if el.tag == W + "tbl"]

    # cover
    first = paras[0] if paras else None
    if first is None or first.find(".//" + W + "drawing") is None:
        warns.append("cover does not open on the logo image")

    # TOC
    instr = " ".join(i.text or "" for i in doc.iter(W + "instrText"))
    if "TOC" not in instr:
        errors.append("no table of contents field")
    if settings is None or settings.find(W + "updateFields") is None:
        warns.append("settings do not ask Word to update fields on open, the TOC may show stale entries")

    # outline and numbering
    h1n, outline = 0, []
    annex = None
    for p in paras:
        sty = names.get(pstyle(p), pstyle(p))
        t = text_of(p).strip()
        if sty == "heading 1" or sty == "Heading 1":
            outline.append(t)
            m = re.match(r"^(\d+)\. ", t)
            a = re.match(r"^Annex ([A-Z])\. ", t)
            if m:
                h1n += 1
                if int(m.group(1)) != h1n:
                    errors.append(f"section numbering breaks at {t!r}, expected {h1n}.")
            elif a:
                annex = a.group(1)
            else:
                errors.append(f"Heading 1 without a number or annex letter: {t!r}")
        elif sty == "heading 2" or sty == "Heading 2":
            outline.append("    " + t)
            parent = annex if annex else str(h1n)
            if not re.match(rf"^{parent}\.\d+ ", t):
                errors.append(f"Heading 2 {t!r} does not carry its parent number {parent}.")
    numbered = [o for o in outline if re.match(r"^\d+\. ", o)]
    annexes = [o for o in outline if o.startswith("Annex ")]
    if numbered and not numbered[-1].endswith(" Open points"):
        warns.append(f"the last numbered section is {numbered[-1]!r}, the template ends on Open points")
    if annexes and not annexes[-1].endswith(" Glossary and sources"):
        warns.append(f"the last annex is {annexes[-1]!r}, the template ends on Glossary and sources")
    view.append("outline:")
    view.extend("  " + o for o in outline)

    parts = [text_of(p).strip() for p in paras if re.match(r"^PART [IVX]+: ", text_of(p).strip())]
    view.append(f"parts: {parts}")
    if not parts:
        errors.append("no PART label (PART I: ..., PART II: ...)")
    if annex and not any(text_of(p).strip() == "ANNEXES" for p in paras):
        errors.append("annex headings present without the ANNEXES label")
    if not any(text_of(p).strip() == "Document control" for p in paras):
        errors.append("no Document control page")
    for want in ("1.1 Purpose", "1.2 Scope", "1.3 Related documents"):
        if not any(o.strip() == want for o in outline):
            errors.append(f"section 1 misses {want!r}")

    # tables
    headers = []
    for i, t in enumerate(tables, 1):
        rows = t.findall(W + "tr")
        hdr = [text_of(c).strip() for c in rows[0].findall(W + "tc")]
        headers.append(hdr)
        view.append(f"table {i}: {len(rows) - 1} rows | {' | '.join(hdr)}")
        trpr = rows[0].find(W + "trPr")
        if trpr is None or trpr.find(W + "tblHeader") is None:
            errors.append(f"table {i} header row does not repeat across pages")
        for c in rows[0].findall(W + "tc"):
            shd = c.find(f"{W}tcPr/{W}shd")
            if shd is None or shd.get(W + "fill") != COL["table_header_fill"]:
                errors.append(f"table {i} header cell {text_of(c).strip()!r} is not filled {COL['table_header_fill']}")
                break
    for label, cols in REQUIRED_TABLES.items():
        if cols not in headers:
            errors.append(f"missing {label} table: {' | '.join(cols)}")
    if tables and headers[0] != REQUIRED_TABLES["cover metadata"]:
        errors.append("the first table is not the cover metadata table")

    tbc = alltext.count("[TBC]")
    view.append(f"tags: [TBC] x{tbc}, [Proposed] x{alltext.count('[Proposed]')}")
    if tbc and REQUIRED_TABLES["open points"] not in headers:
        errors.append("[TBC] used but no open points table lists them")
    return view, errors, warns


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("docx")
    args = ap.parse_args()
    try:
        view, errors, warns = check(args.docx)
    except (OSError, KeyError, zipfile.BadZipFile) as e:
        print(f"error: cannot read {args.docx}: {e}", file=sys.stderr)
        return 2
    print("\n".join(view))
    print()
    for e in errors:
        print(f"ERROR {e}")
    for w in warns:
        print(f"WARN  {w}")
    print(f"\n{len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
