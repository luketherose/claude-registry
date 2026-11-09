"""Renders the C4 views of a project's model.py as inline SVG, with a geometric collision check.

Three modes. A static view draws every element with its description and every arrow with
its label. A use-case view (a C4 dynamic diagram) draws the compact layout of the view:
the elements and calls of the use case are highlighted, the others are dimmed, and each
highlighted call carries the number of its step. An overview draws the same compact layout
with every element and call in its normal style, so the first tab and the use-case tabs
show one picture.
"""
import html
import math

from model import ELEMENTS  # the project's model.py, on sys.path

FONT = "Arial, Helvetica, sans-serif"

# Themes. `accent` draws lines, borders and the system boundary; `accent_text` is the
# accessible variant for text and step badges (AA on white); `tint` fills highlighted elements.
THEMES = {
    "unicredit": dict(  # tokens of the unicredit-design-system skill; no blue, no purple
        accent="#E30613", accent_text="#B00010", tint="#FCE6E8", accent_name="red",
        ink="#0E0E12", body="#3F3F46", sub="#55555E", muted="#7B7B85",
        line="#C5C5CC", soft="#EDEDEF", n50="#F7F7F8", white="#FFFFFF",
        dim_line="#D6D6DC", dim_text="#A3A3AD", code_bg="#1A1A2E",
        font='"UniCredit", "Dax", "FS Joey", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    ),
    "accenture": dict(  # tokens of the accenture-branding skill
        accent="#A100FF", accent_text="#7500C0", tint="#F4F0FF", accent_name="purple",
        ink="#000000", body="#333333", sub="#5A5A54", muted="#6E6E66",
        line="#D2D2C8", soft="#E6E6DC", n50="#F7F7F3", white="#FFFFFF",
        dim_line="#DADAD2", dim_text="#A8A8A0", code_bg="#460073",
        font='"Graphik", Arial, Helvetica, sans-serif',
    ),
}

T, STYLE, HIGHLIGHT, DIM = {}, {}, {}, {}


def apply_theme(name):
    """Switch every colour in place, so modules that imported T and STYLE see the change."""
    if name not in THEMES:
        raise SystemExit(f"unknown theme {name!r}; known: {', '.join(THEMES)}")
    T.clear()
    T.update(THEMES[name])
    plain = dict(fill=T["white"], stroke=T["body"], width=1.6, text=T["ink"], sub=T["sub"])
    STYLE.clear()
    STYLE.update({
        "person": dict(fill=T["soft"], stroke=T["muted"], width=1.5, text=T["ink"], sub=T["sub"]),
        "system": dict(fill=T["tint"], stroke=T["accent"], width=2.2, text=T["ink"], sub=T["accent_text"]),
        "system_ext": dict(fill=T["soft"], stroke=T["muted"], width=1.5, text=T["ink"], sub=T["sub"]),
        "container": dict(plain), "spa": dict(plain), "db": dict(plain),
        "component": dict(fill=T["n50"], stroke=T["body"], width=1.4, text=T["ink"], sub=T["sub"]),
        "infra": dict(fill=T["n50"], stroke=T["muted"], width=1.2, text=T["ink"], sub=T["sub"]),
    })
    HIGHLIGHT.clear()
    HIGHLIGHT.update(fill=T["tint"], stroke=T["accent"], width=2.4, text=T["ink"], sub=T["accent_text"])
    DIM.clear()
    DIM.update(fill=T["white"], stroke=T["dim_line"], width=1.2, text=T["dim_text"], sub=T["dim_text"], dash="5 4")


apply_theme("unicredit")
BADGE_R = 14


def esc(s):
    return html.escape(s, quote=True)


def wrap(text, maxc):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= maxc:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def type_label(e):
    k = e["kind"]
    if k == "person":
        return "[Person]"
    if k in ("system", "system_ext"):
        return "[Software System]"
    if k in ("container", "spa", "db"):
        return f"[Container: {e['tech']}]"
    if k == "infra":
        return f"[Infrastructure: {e['tech']}]"
    return f"[Component: {e['tech']}]"


class Node:
    def __init__(self, eid, cx, cy, w, compact=False, state="normal"):
        self.eid, self.cx, self.cy, self.w = eid, cx, cy, w
        e = ELEMENTS[eid]
        self.e, self.kind, self.state = e, e["kind"], state
        inner = w - 22
        # compact (use-case views): bigger name and type, no description
        self.fs_name, self.fs_type = (18, 13) if compact else (14, 11)
        self.lh_name, self.lh_type = (21, 16) if compact else (15, 14)
        self.name_l = wrap(e["name"], max(10, int(inner / (self.fs_name * 0.57))))
        self.type_l = wrap(type_label(e), max(10, int(inner / (self.fs_type * 0.53))))
        self.desc_l = [] if compact else wrap(e["desc"], max(10, int(inner / 6.3)))
        body = 12 + (self.lh_name + 2) * len(self.name_l) + self.lh_type * len(self.type_l) + (6 + 15 * len(self.desc_l) if self.desc_l else 0) + 10
        self.top = {"spa": 18, "db": 14, "person": 40}.get(self.kind, 0)
        self.bottom = 8 if self.kind == "db" else 0
        self.h = self.top + body + self.bottom
        self.x0, self.y0 = cx - w / 2, cy - self.h / 2
        self.x1, self.y1 = cx + w / 2, cy + self.h / 2

    def rect(self, pad=0):
        return (self.x0 - pad, self.y0 - pad, self.x1 + pad, self.y1 + pad)

    def style(self):
        if self.state == "hi":
            return HIGHLIGHT
        if self.state == "dim":
            d = dict(DIM)
            if self.kind in ("person", "system_ext"):
                d["fill"] = T["n50"]
            return d
        return STYLE[self.kind]

    def svg(self):
        st = self.style()
        x0, y0, w, h = self.x0, self.y0, self.w, self.h
        f, s, sw = st["fill"], st["stroke"], st["width"]
        dash = f' stroke-dasharray="{st["dash"]}"' if st.get("dash") else ""
        a = f'fill="{f}" stroke="{s}" stroke-width="{sw}"{dash}'
        out = []
        if self.kind == "person":
            r = 24
            out.append(f'<rect x="{x0}" y="{y0 + 36}" width="{w}" height="{h - 36}" rx="26" {a}/>')
            out.append(f'<circle cx="{self.cx}" cy="{y0 + r}" r="{r}" {a}/>')
        elif self.kind == "db":
            ry = 11
            out.append(f'<path d="M{x0},{y0 + ry} L{x0},{y0 + h - ry} A{w / 2},{ry} 0 0 0 {x0 + w},{y0 + h - ry} '
                       f'L{x0 + w},{y0 + ry} A{w / 2},{ry} 0 0 0 {x0},{y0 + ry} Z" {a}/>')
            out.append(f'<ellipse cx="{self.cx}" cy="{y0 + ry}" rx="{w / 2}" ry="{ry}" {a}/>')
        elif self.kind == "spa":
            out.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="6" {a}/>')
            out.append(f'<path d="M{x0},{y0 + 18} L{x0 + w},{y0 + 18}" stroke="{s}" stroke-width="1"{dash}/>')
            for i in range(3):
                out.append(f'<circle cx="{x0 + 12 + i * 10}" cy="{y0 + 9}" r="3" fill="{s}"/>')
        else:
            # an infrastructure node (a virtual IP, a load balancer) is a pill, so it never reads as a container
            rx = min(h / 2, 22) if self.kind == "infra" else 6
            out.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="{rx}" {a}/>')
        y = y0 + self.top + 12
        for ln in self.name_l:
            y += self.lh_name
            out.append(f'<text x="{self.cx}" y="{y}" text-anchor="middle" font-family="{FONT}" font-size="{self.fs_name}" font-weight="700" fill="{st["text"]}">{esc(ln)}</text>')
        y += 2
        for ln in self.type_l:
            y += self.lh_type
            out.append(f'<text x="{self.cx}" y="{y}" text-anchor="middle" font-family="{FONT}" font-size="{self.fs_type}" fill="{st["sub"]}">{esc(ln)}</text>')
        if self.desc_l:
            y += 6
        for ln in self.desc_l:
            y += 15
            out.append(f'<text x="{self.cx}" y="{y}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{st["text"]}">{esc(ln)}</text>')
        return "\n".join(out)


def exit_point(rect, px, py, qx, qy):
    """Point where the ray from p (inside rect) towards q leaves rect."""
    dx, dy = qx - px, qy - py
    ts = []
    if dx > 0:
        ts.append((rect[2] - px) / dx)
    elif dx < 0:
        ts.append((rect[0] - px) / dx)
    if dy > 0:
        ts.append((rect[3] - py) / dy)
    elif dy < 0:
        ts.append((rect[1] - py) / dy)
    t = min(ts) if ts else 0
    return px + dx * t, py + dy * t


def seg_hits_rect(p, q, r):
    """Liang-Barsky: does segment pq intersect rect r."""
    x0, y0, x1, y1 = r
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pv, qv in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if pv == 0:
            if qv < 0:
                return False
        else:
            t = qv / pv
            if pv < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return True


def rects_overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def contains(outer, inner):
    return outer[0] <= inner[0] and outer[1] <= inner[1] and outer[2] >= inner[2] and outer[3] >= inner[3]


def point_at(pts, frac):
    segs = list(zip(pts, pts[1:]))
    lens = [math.dist(p, q) for p, q in segs]
    target = sum(lens) * frac
    acc = 0
    for (p, q), L in zip(segs, lens):
        if acc + L >= target:
            f = (target - acc) / L if L else 0
            return p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f
        acc += L
    return pts[-1]


class View:
    """A static view, or with `flow` a use-case view of the same layout."""

    def __init__(self, spec, flow=None, overview=False):
        self.spec, self.flow, self.overview = spec, flow, overview
        self.sid = spec["id"] + (f"-{flow['id']}" if flow else "-ov" if overview else "")
        self.compact = compact = flow is not None or overview
        hi = set(flow["hi"]) if flow else set()
        self.nodes = {}
        # use cases and the overview use the compact layout of the spec: same arrangement, smaller boxes
        lay = spec["flow_layout"] if compact else spec
        self.k = lay.get("k", 1.0) if compact else 1.0
        self.size = lay["size"]
        for eid, (cx, cy, w) in lay["nodes"].items():
            state = "normal" if not flow else ("hi" if eid in hi else "dim")
            self.nodes[eid] = Node(eid, cx, cy, w, compact=compact, state=state)
        self.edges = spec["edges"]
        self.step_of = {}
        self.node_steps = {}
        if flow:
            keys = {ed["key"] for ed in self.edges}
            for n, st in enumerate(flow["steps"], 1):
                for k in st["calls"]:
                    if k.startswith("@"):
                        self.node_steps.setdefault(k[1:], []).append(n)
                    else:
                        assert k in keys, f"{self.sid}: unknown call {k}"
                        self.step_of.setdefault(k, []).append(n)
        self.warnings = []
        self.paths, self.labels, self.badges = [], [], []
        self._layout_edges()
        self._layout_zones()
        self._check()

    # edges, labels and badges
    def _layout_edges(self):
        for i, ed in enumerate(self.edges):
            a, b = self.nodes[ed["src"]], self.nodes[ed["dst"]]
            ac, bc = (a.cx, a.cy), (b.cx, b.cy)
            if ed["shift"] and not (ed["via"] and not self.compact):
                dx, dy = bc[0] - ac[0], bc[1] - ac[1]
                n = math.hypot(dx, dy)
                nx, ny = -dy / n * ed["shift"] * self.k, dx / n * ed["shift"] * self.k
                ac, bc = (ac[0] + nx, ac[1] + ny), (bc[0] + nx, bc[1] + ny)
            via = self.spec["flow_layout"].get("via", {}).get(ed["key"]) if self.compact else None
            via = via if via is not None else ([] if self.compact else ed["via"])
            pts = [ac] + [tuple(v) for v in via] + [bc]
            start = exit_point(a.rect(), *ac, *pts[1])
            end = exit_point(b.rect(), *bc, *pts[-2])
            pts = [start] + pts[1:-1] + [end]
            self.paths.append(pts)
            if self.compact:
                nums = self.step_of.get(ed["key"], [])
                if nums:
                    bx, by = point_at(pts, ed["bt"] if ed["bt"] is not None else ed["t"])
                    for j, n in enumerate(nums):
                        off = (j - (len(nums) - 1) / 2) * (2 * BADGE_R + 4)
                        self.badges.append(dict(x=bx + off, y=by, n=n, src=f"{ed['src']}->{ed['dst']}"))
                continue
            lx, ly = point_at(pts, ed["t"])
            lx += ed["dx"]
            ly += ed["dy"]
            lab = wrap(ed["label"], ed["wc"])
            tech = wrap(f"[{ed['tech']}]", max(ed["wc"], 20)) if ed["tech"] else []
            wpx = max([len(s) * 6.0 for s in lab] + [len(s) * 5.5 for s in tech]) + 12
            hpx = 14 * len(lab) + 13 * len(tech) + 8
            self.labels.append(dict(x=lx, y=ly, w=wpx, h=hpx, lab=lab, tech=tech, idx=i))
        for eid, nums in self.node_steps.items():
            nd = self.nodes[eid]
            for j, n in enumerate(nums):
                self.badges.append(dict(x=nd.x1 - 4 - j * (2 * BADGE_R + 4), y=nd.y0 - 4, n=n, src=f"@{eid}", on_node=eid))

    # zones: dashed areas around groups of nodes or other zones
    def _layout_zones(self):
        self.zones = []
        rects = {}
        for z in self.spec.get("zones", []):
            boxes, nodes_in = [], set()
            for m in z["members"]:
                if m in rects:
                    boxes.append(rects[m])
                    nodes_in |= next(zz["nodes"] for zz in self.zones if zz["id"] == m)
                else:
                    boxes.append(self.nodes[m].rect())
                    nodes_in.add(m)
            pad = round(z.get("pad", 28) * (0.75 if self.compact else 1))
            lab_h = 24 if not z.get("sub") else 40
            r = (min(b[0] for b in boxes) - pad, min(b[1] for b in boxes) - pad - lab_h,
                 max(b[2] for b in boxes) + pad, max(b[3] for b in boxes) + pad)
            rects[z["id"]] = r
            lab_w = max(len(z["label"]) * 8.2, len(z.get("sub", "")) * 6.4) + 16
            lx = r[2] - lab_w if z.get("anchor") == "right" else r[0]
            self.zones.append(dict(z, rect=r, nodes=nodes_in, lab_rect=(lx, r[1], lx + lab_w, r[1] + lab_h)))

    def _check(self):
        W, H = self.size
        for ed, pts in zip(self.edges, self.paths):
            for p, q in zip(pts, pts[1:]):
                for eid, nd in self.nodes.items():
                    if eid in (ed["src"], ed["dst"]):
                        continue
                    if seg_hits_rect(p, q, nd.rect(pad=6)):
                        self.warnings.append(f"edge {ed['src']}->{ed['dst']} crosses {eid}")
        for lb in self.labels:
            r = (lb["x"] - lb["w"] / 2, lb["y"] - lb["h"] / 2, lb["x"] + lb["w"] / 2, lb["y"] + lb["h"] / 2)
            lb["rect"] = r
            ed = self.edges[lb["idx"]]
            for eid, nd in self.nodes.items():
                if rects_overlap(r, nd.rect(pad=3)):
                    self.warnings.append(f"label {ed['src']}->{ed['dst']} overlaps {eid}")
            for z in self.zones:
                if rects_overlap(r, z["lab_rect"]):
                    self.warnings.append(f"label {ed['src']}->{ed['dst']} overlaps zone label {z['id']}")
            if r[0] < 0 or r[1] < 0 or r[2] > W or r[3] > H:
                self.warnings.append(f"label {ed['src']}->{ed['dst']} outside canvas")
        for i, a in enumerate(self.labels):
            for b in self.labels[i + 1:]:
                if rects_overlap(a["rect"], b["rect"]):
                    ea, eb = self.edges[a["idx"]], self.edges[b["idx"]]
                    self.warnings.append(f"label {ea['src']}->{ea['dst']} overlaps label {eb['src']}->{eb['dst']}")
        for bg in self.badges:
            r = (bg["x"] - BADGE_R, bg["y"] - BADGE_R, bg["x"] + BADGE_R, bg["y"] + BADGE_R)
            bg["rect"] = r
            for eid, nd in self.nodes.items():
                if eid != bg.get("on_node") and rects_overlap(r, nd.rect(pad=2)):
                    self.warnings.append(f"badge {bg['n']} on {bg['src']} overlaps {eid}")
            for z in self.zones:
                if rects_overlap(r, z["lab_rect"]):
                    self.warnings.append(f"badge {bg['n']} on {bg['src']} overlaps zone label {z['id']}")
            if r[0] < 0 or r[1] < 0 or r[2] > W or r[3] > H:
                self.warnings.append(f"badge {bg['n']} outside canvas")
        for i, a in enumerate(self.badges):
            for b in self.badges[i + 1:]:
                if rects_overlap(a["rect"], b["rect"]):
                    self.warnings.append(f"badge {a['n']} on {a['src']} overlaps badge {b['n']} on {b['src']}")
        for eid, nd in self.nodes.items():
            if nd.x0 < 0 or nd.y0 < 0 or nd.x1 > W or nd.y1 > H:
                self.warnings.append(f"node {eid} outside canvas")
        names = list(self.nodes)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                if rects_overlap(self.nodes[a].rect(pad=8), self.nodes[b].rect(pad=8)):
                    self.warnings.append(f"node {a} overlaps {b}")
        for i, z in enumerate(self.zones):
            r = z["rect"]
            if r[0] < 0 or r[1] < 0 or r[2] > W or r[3] > H:
                self.warnings.append(f"zone {z['id']} outside canvas")
            for eid, nd in self.nodes.items():
                if eid not in z["nodes"] and rects_overlap(r, nd.rect(pad=4)):
                    self.warnings.append(f"node {eid} overlaps zone {z['id']}")
            for o in self.zones[i + 1:]:
                ro = o["rect"]
                if rects_overlap(r, ro) and not contains(r, ro) and not contains(ro, r):
                    self.warnings.append(f"zone {z['id']} overlaps zone {o['id']}")

    def boundary_svg(self):
        """C4 boundary of the container in scope (Level 3): dashed, name and type bottom left."""
        bd = self.spec.get("boundary")
        if not bd:
            return "", None
        mem = [self.nodes[m] for m in bd["members"]]
        pad = bd.get("pad", 34)
        x0 = min(n.x0 for n in mem) - pad
        y0 = min(n.y0 for n in mem) - pad
        x1 = max(n.x1 for n in mem) + pad
        y1 = max(n.y1 for n in mem) + pad + 34
        e = ELEMENTS[bd["eid"]]
        out = [
            f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="8" fill="none" stroke="{T["accent"]}" stroke-width="1.8" stroke-dasharray="10 6"/>',
            f'<text x="{x0 + 14}" y="{y1 - 24}" font-family="{FONT}" font-size="15" font-weight="700" fill="{T["accent_text"]}">{esc(e["name"])}</text>',
            f'<text x="{x0 + 14}" y="{y1 - 9}" font-family="{FONT}" font-size="11.5" fill="{T["sub"]}">{esc(type_label(e))}</text>',
        ]
        rect = (x0, y0, x1, y1)
        W, H = self.size
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            self.warnings.append("boundary outside canvas")
        for eid in self.nodes:
            if eid not in bd["members"] and rects_overlap(rect, self.nodes[eid].rect()):
                self.warnings.append(f"outside node {eid} overlaps the boundary")
        return "\n".join(out), rect

    def zones_svg(self):
        out = []
        for z in self.zones:
            x0, y0, x1, y1 = z["rect"]
            if z.get("kind") == "system":
                stroke, sw, dash, col = T["accent"], 2, "10 6", T["accent_text"]
            else:
                stroke, sw, dash, col = "#9C9CA6", 1.3, "6 5", T["body"]
            out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="6" fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-dasharray="{dash}"/>')
            if z.get("anchor") == "right":
                tx, anchor = x1 - 12, "end"
            else:
                tx, anchor = x0 + 12, "start"
            out.append(f'<text x="{tx:.1f}" y="{y0 + 18:.1f}" text-anchor="{anchor}" font-family="{FONT}" font-size="13" font-weight="700" fill="{col}">{esc(z["label"])}</text>')
            if z.get("sub"):
                out.append(f'<text x="{tx:.1f}" y="{y0 + 33:.1f}" text-anchor="{anchor}" font-family="{FONT}" font-size="11" fill="{T["sub"]}">{esc(z["sub"])}</text>')
        return "\n".join(out)

    def svg(self):
        W, H = self.size
        sid = self.sid
        title = self.flow["title"] if self.flow else self.spec["title"]
        out = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="{sid}-t">',
            f'<title id="{sid}-t">{esc(title)}</title>',
            "<defs>",
            f'<marker id="{sid}-arr" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{T["body"]}"/></marker>',
            f'<marker id="{sid}-dim" viewBox="0 0 10 10" refX="9.5" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{T["dim_line"]}"/></marker>',
            f'<marker id="{sid}-hi" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{T["accent"]}"/></marker>',
            "</defs>",
            f'<rect x="0" y="0" width="{W}" height="{H}" fill="#FFFFFF"/>',
        ]
        out.append(self.zones_svg())
        bsvg, _ = self.boundary_svg()
        out.append(bsvg)
        lit = []
        for ed, pts in zip(self.edges, self.paths):
            d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            if self.flow and ed["key"] in self.step_of:
                dash = ' stroke-dasharray="9 6"' if ed["style"] == "async" else ""
                lit.append(f'<path d="{d}" fill="none" stroke="{T["accent"]}" stroke-width="3"{dash} marker-end="url(#{sid}-hi)"/>')
            elif self.flow:
                dash = ' stroke-dasharray="5 4"' if ed["style"] == "async" else ""
                out.append(f'<path d="{d}" fill="none" stroke="{T["dim_line"]}" stroke-width="1.3"{dash} marker-end="url(#{sid}-dim)"/>')
            else:
                dash = ' stroke-dasharray="7 5"' if ed["style"] == "async" else ""
                out.append(f'<path d="{d}" fill="none" stroke="{T["body"]}" stroke-width="1.5"{dash} marker-end="url(#{sid}-arr)"/>')
        out += lit
        for nd in sorted(self.nodes.values(), key=lambda n: n.state == "hi"):
            out.append(nd.svg())
        for lb in self.labels:
            x0, y0 = lb["x"] - lb["w"] / 2, lb["y"] - lb["h"] / 2
            out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{lb["w"]:.1f}" height="{lb["h"]:.1f}" rx="4" fill="#FFFFFF" fill-opacity="0.95" stroke="{T["line"]}" stroke-width="0.8"/>')
            y = y0 + 4
            for s in lb["lab"]:
                y += 13
                out.append(f'<text x="{lb["x"]:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" font-size="11.5" fill="{T["ink"]}">{esc(s)}</text>')
            for s in lb["tech"]:
                y += 13
                out.append(f'<text x="{lb["x"]:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" font-size="10.5" font-style="italic" fill="{T["sub"]}">{esc(s)}</text>')
        for bg in self.badges:
            out.append(f'<circle cx="{bg["x"]:.1f}" cy="{bg["y"]:.1f}" r="{BADGE_R}" fill="{T["accent_text"]}" stroke="#FFFFFF" stroke-width="2.5"/>')
            out.append(f'<text x="{bg["x"]:.1f}" y="{bg["y"] + 5:.1f}" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="700" fill="#FFFFFF">{bg["n"]}</text>')
        out.append("</svg>")
        return "\n".join(out)

    def kinds(self):
        return {ELEMENTS[e]["kind"] for e in self.nodes}

    def styles(self):
        return {ed["style"] for ed in self.edges}
