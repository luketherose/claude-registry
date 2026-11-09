"""Builds the C4 HTML deliverable of a project from its model.py, views.py and doc.py.

Usage: python3 -I build.py <project_dir> <out.html>
Exit code 1 when a view has layout warnings (run check.py for the detail).
"""
import sys
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit(__doc__)
PROJECT, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(PROJECT))
import views  # noqa: E402
from doc import DOC  # noqa: E402
from model import ELEMENTS  # noqa: E402
from render import DIM, HIGHLIGHT, STYLE, T, View, apply_theme, esc  # noqa: E402

VIEWS = views.VIEWS
apply_theme(DOC.get("theme", "unicredit"))

KIND_TEXT = {
    "person": ("Person", "A user role; grey, person shape."),
    "system": ("Software system in scope", "The system these diagrams describe; {a} border, light {a} fill."),
    "system_ext": ("External software system", "A system outside the scope, shown as a black box; grey."),
    "spa": ("Container, single-page application", "Runs in the browser; white, browser-window shape."),
    "container": ("Container", "A separately deployable application or service; white box."),
    "db": ("Container, data store", "A database, cache or object store; white cylinder."),
    "component": ("Component", "A module inside a container, not deployable on its own; light grey box."),
    "infra": ("Infrastructure node", "A network element such as a virtual IP, drawn for orientation; light grey, rounded ends."),
}
OVERVIEW_TAB = {"Container": "All containers", "Component": "All components"}

SW = '<svg width="48" height="38" viewBox="0 0 48 38" aria-hidden="true">{}</svg>'


def swatch(kind, st=None):
    st = st or STYLE[kind]
    f, s = st["fill"], st["stroke"]
    dash = f' stroke-dasharray="{st["dash"]}"' if st.get("dash") else ""
    a = f'fill="{f}" stroke="{s}" stroke-width="1.5"{dash}'
    if kind == "person":
        shape = f'<rect x="4" y="15" width="40" height="19" rx="8" {a}/><circle cx="24" cy="10" r="7" {a}/>'
    elif kind == "db":
        shape = (f'<path d="M6,9 L6,29 A18,5 0 0 0 42,29 L42,9 A18,5 0 0 0 6,9 Z" {a}/>'
                 f'<ellipse cx="24" cy="9" rx="18" ry="5" {a}/>')
    elif kind == "infra":
        shape = f'<rect x="4" y="9" width="40" height="20" rx="10" {a}/>'
    elif kind == "spa":
        shape = f'<rect x="4" y="5" width="40" height="28" rx="4" {a}/><path d="M4,12 L44,12" stroke="{s}"/>'
    else:
        shape = f'<rect x="4" y="6" width="40" height="26" rx="4" {a}/>'
    return SW.format(shape)


def li(sw, name, text):
    return f'<li>{sw}<span><b>{esc(name)}</b>. {esc(text)}</span></li>'


def arrow(color, dash=False, width=1.6):
    d = ' stroke-dasharray="6 4"' if dash else ""
    return SW.format(f'<path d="M4,19 L38,19" stroke="{color}" stroke-width="{width}"{d}/><path d="M36,14 L45,19 L36,24 z" fill="{color}"/>')


def legend_html(view):
    rows = []
    for k in ["person", "system", "system_ext", "infra", "spa", "container", "db", "component"]:
        if k in view.kinds():
            name, text = KIND_TEXT[k]
            rows.append(li(swatch(k), name, text.format(a=T["accent_name"])))
    if view.spec.get("zones"):
        rows.append(li(SW.format(f'<rect x="4" y="6" width="40" height="26" rx="4" fill="none" stroke="{T["accent"]}" stroke-width="1.8" stroke-dasharray="6 4"/>'),
                       f"Dashed {T['accent_name']} area", "The boundary of the system in scope, with its name at the top."))
        rows.append(li(SW.format('<rect x="4" y="6" width="40" height="26" rx="4" fill="none" stroke="#9C9CA6" stroke-width="1.3" stroke-dasharray="5 4"/>'),
                       "Dashed grey area", "Where the elements run: a network zone, the cluster, the managed services. Its name is in its top corner."))
    if view.spec.get("boundary"):
        rows.append(li(SW.format(f'<rect x="4" y="6" width="40" height="26" rx="4" fill="none" stroke="{T["accent"]}" stroke-width="1.8" stroke-dasharray="6 4"/>'),
                       f"Dashed {T['accent_name']} boundary", "The container in scope; its name and type sit at the bottom left."))
    rows.append(li(arrow(T["body"]), "Solid arrow", "Synchronous request: the caller waits for the answer. It points from the caller to the called element."))
    if "async" in view.styles():
        rows.append(li(arrow(T["body"], dash=True), "Dashed arrow", "Asynchronous flow: a message on a queue or a batch transfer, in the direction of the data."))
    rows.append('<li><span class="lg-text">[ ]</span><span><b>Brackets</b>. On an element, its type and technology; on an arrow, the protocol or technology.</span></li>')
    return '<ul class="legend">' + "".join(rows) + "</ul>"


def flow_legend(spec):
    kind, noun = spec["kind"], spec.get("flow_noun", "use case")
    badge = SW.format(f'<circle cx="24" cy="19" r="13" fill="{T["accent_text"]}" stroke="#fff" stroke-width="2"/><text x="24" y="24" text-anchor="middle" font-family="Arial" font-size="14" font-weight="700" fill="#fff">1</text>')
    rows = [
        li(swatch("container", HIGHLIGHT), "Highlighted element", f"Takes part in this {noun}; {T['accent_name']} border, light {T['accent_name']} fill."),
        li(swatch("container", DIM), "Dimmed element", f"The rest of the {kind} diagram, kept for orientation; dashed grey."),
        li(arrow(T["accent"], width=3), f"{T['accent_name'].capitalize()} arrow", f"A call of this {noun}; dashed when asynchronous."),
        li(badge, "Numbered badge", "The step the call belongs to, as listed beside the diagram."),
    ]
    return '<ul class="legend compact">' + "".join(rows) + "</ul>"


def catalogue_html(eids):
    rows = []
    for eid in eids:
        e = ELEMENTS[eid]
        rows.append(f"<tr><td><b>{esc(e['name'])}</b></td><td>{esc(KIND_TEXT[e['kind']][0])}</td><td>{esc(e.get('tech', ''))}</td><td>{esc(e['desc'])}</td></tr>")
    return ('<div class="tbl"><table><thead><tr><th>Element</th><th>Type</th><th>Technology</th><th>Responsibility</th></tr></thead><tbody>'
            + "".join(rows) + "</tbody></table></div>")


def relations_html(view):
    rows = []
    for i, ed in enumerate(view.edges, 1):
        a, b = ELEMENTS[ed["src"]]["name"], ELEMENTS[ed["dst"]]["name"]
        kind = "Asynchronous" if ed["style"] == "async" else "Synchronous"
        flag = ' <span class="flag">assumption</span>' if ed.get("assumption") else ""
        rows.append(f"<tr><td>{i}</td><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(ed['label'])}{flag}</td><td>{esc(ed['tech'])}</td><td>{kind}</td></tr>")
    return ('<div class="tbl"><table><thead><tr><th>#</th><th>From</th><th>To</th><th>Intent</th><th>Technology</th><th>Style</th></tr></thead><tbody>'
            + "".join(rows) + "</tbody></table></div>")


def q(x):
    return x.replace('"', "'")


def decl(eid, indent="  "):
    e = ELEMENTS[eid]
    k, n, d, t = e["kind"], q(e["name"]), q(e["desc"]), q(e.get("tech", ""))
    if k == "person":
        return f'{indent}Person({eid}, "{n}", "{d}")'
    if k == "system":
        return f'{indent}System({eid}, "{n}", "{d}")'
    if k == "system_ext":
        return f'{indent}System_Ext({eid}, "{n}", "{d}")'
    if k == "db":
        return f'{indent}ContainerDb({eid}, "{n}", "{t}", "{d}")'
    if k in ("container", "spa"):
        return f'{indent}Container({eid}, "{n}", "{t}", "{d}")'
    if k == "infra":
        return f'{indent}Container_Ext({eid}, "{n}", "Infrastructure: {t}", "{d}")'
    return f'{indent}Component({eid}, "{n}", "{t}", "{d}")'


def mermaid(spec, flow=None):
    head = "C4Dynamic" if flow else {"System Context": "C4Context", "Container": "C4Container", "Component": "C4Component"}[spec["kind"]]
    lines = [head, f'  title {flow["title"] if flow else spec["title"]}', ""]
    eids = [e for e in spec["nodes"] if not flow or e in flow["hi"]]
    if spec.get("boundary"):
        bid, members = spec["boundary"]["eid"], set(spec["boundary"]["members"])
        fn = "Container_Boundary"
    elif any(z.get("kind") == "system" for z in spec.get("zones", [])):
        bid = next(z["eid"] for z in spec["zones"] if z.get("kind") == "system")
        fn = "System_Boundary"
        members = {e for e in eids if ELEMENTS[e]["kind"] in ("container", "spa", "db")}
    else:
        bid, members, fn = None, set(), None
    for eid in eids:
        if eid not in members:
            lines.append(decl(eid))
    if bid and members:
        lines += ["", f'  {fn}({bid}_b, "{q(ELEMENTS[bid]["name"])}") {{']
        lines += [decl(eid, "    ") for eid in eids if eid in members]
        lines.append("  }")
    lines.append("")
    by_key = {ed["key"]: ed for ed in spec["edges"]}
    if flow:
        for n, st in enumerate(flow["steps"], 1):
            for k in st["calls"]:
                if k.startswith("@"):
                    continue
                ed = by_key[k]
                lines.append(f'  RelIndex({n}, {ed["src"]}, {ed["dst"]}, "{q(ed["label"])}", "{q(ed["tech"])}")')
    else:
        for ed in spec["edges"]:
            tech = f', "{q(ed["tech"])}"' if ed["tech"] else ""
            lines.append(f'  Rel({ed["src"]}, {ed["dst"]}, "{q(ed["label"])}"{tech})')
    return "\n".join(lines)


CSS_BODY = """
*{box-sizing:border-box}
html{color-scheme:light}
body{margin:0;font-family:var(--font);color:var(--body);background:#fff;line-height:1.5;font-size:15px}
a{color:var(--accent-text)}
header.top{border-top:6px solid var(--accent);padding:26px 32px 22px;border-bottom:1px solid var(--soft)}
header.top .eyebrow{color:var(--muted);font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;margin:0 0 8px;font-weight:700}
header.top h1{margin:0 0 6px;font-size:30px;line-height:1.2;color:var(--ink)}
header.top p{margin:0;font-size:16px}
.meta{display:flex;flex-wrap:wrap;gap:6px 24px;margin-top:14px;font-size:13px;color:var(--muted)}
.meta b{color:var(--ink);font-weight:700}
nav.toc{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid var(--soft);padding:10px 32px;display:flex;flex-wrap:wrap;gap:6px 18px;font-size:14px}
nav.toc a{color:var(--accent-text);text-decoration:none;white-space:nowrap}
nav.toc a:hover{text-decoration:underline}
main{max-width:1560px;margin:0 auto;padding:8px 32px 48px}
section[id]{scroll-margin-top:96px}
h2{font-size:26px;line-height:1.25;margin:48px 0 6px;color:var(--ink)}
h2::after{content:"";display:block;width:72px;height:4px;background:var(--accent);margin-top:10px}
h3{font-size:16px;margin:22px 0 8px;color:var(--ink)}
.lvl{display:inline-block;font-size:12px;font-weight:700;color:#fff;background:var(--accent-text);border-radius:3px;padding:2px 8px;margin-right:10px;vertical-align:4px;letter-spacing:.02em}
.lead{font-size:17px;color:var(--ink);margin:10px 0 4px}
.scope{color:var(--muted);margin:4px 0 14px}
.diagram{border:1px solid var(--soft);border-radius:6px;overflow:auto;background:#fff;-webkit-overflow-scrolling:touch}
.diagram svg{display:block;width:100%;height:auto;min-width:880px}
.hint{font-size:12.5px;color:var(--muted);margin:6px 0 0}
.tabs-lead{margin:6px 0 0}
.tabs{display:flex;gap:2px;border-bottom:2px solid var(--soft);margin:14px 0 0;overflow-x:auto;-webkit-overflow-scrolling:touch}
.tabs [role=tab]{font:inherit;font-size:14.5px;font-weight:700;color:var(--body);background:none;border:0;border-bottom:3px solid transparent;margin-bottom:-2px;padding:10px 14px;cursor:pointer;white-space:nowrap;display:flex;align-items:center;gap:8px}
.tabs [role=tab]:hover{color:var(--ink);background:var(--n50)}
.tabs [role=tab][aria-selected=true]{color:var(--accent-text);border-bottom-color:var(--accent)}
.tabs [role=tab]:focus-visible{outline:2px solid var(--accent-text);outline-offset:-2px}
.tabs .num{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:50%;background:var(--soft);color:var(--ink);font-size:12px}
.tabs [aria-selected=true] .num{background:var(--accent-text);color:#fff}
.tabpanel{padding-top:10px}
.uc-title{font-size:19px;margin:8px 0 2px}
/* Safari draws an SVG wrongly when it is first laid out inside display:none and shown later,
   so inactive panels stay laid out: collapsed, clipped and invisible, never display:none. */
section.view{position:relative}
.js .tabpanel:not(.active){position:absolute;left:0;right:0;top:0;height:0;overflow:hidden;visibility:hidden}
html:not(.js) .tabs,html:not(.js) .tabs-lead{display:none}
.flow-grid{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:22px;align-items:start;margin-top:12px}
.flow-grid>*{min-width:0}
.steps{background:var(--n50);border-left:4px solid var(--accent);border-radius:0 6px 6px 0;padding:18px 20px}
.steps h3{margin:0 0 10px}
.steps ol{list-style:none;margin:0;padding:0;counter-reset:s}
.steps li{counter-increment:s;display:grid;grid-template-columns:34px 1fr;gap:10px;margin:0 0 14px;font-size:15px;color:var(--ink)}
.steps li::before{content:counter(s);width:30px;height:30px;border-radius:50%;background:var(--accent-text);color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:15px}
.note{font-size:13px;color:var(--muted);margin:8px 0 0}
ul.legend{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:8px 22px}
ul.legend li{display:flex;gap:10px;align-items:flex-start;font-size:13.5px}
ul.legend svg{flex:none}
ul.legend.compact{grid-template-columns:repeat(auto-fill,minmax(260px,1fr));margin-top:12px}
.lg-text{flex:none;width:48px;text-align:center;font-weight:700;color:var(--muted);font-size:15px;padding-top:8px}
ul.notes{margin:0;padding-left:20px;font-size:14px}
ul.notes li{margin:4px 0}
details{margin:12px 0;border:1px solid var(--soft);border-radius:6px;padding:0 14px;background:var(--n50)}
details[open]{background:#fff}
summary{cursor:pointer;padding:10px 0;font-weight:700;font-size:14.5px;color:var(--ink)}
.tbl{overflow-x:auto;margin-bottom:12px}
table{border-collapse:collapse;width:100%;font-size:13.5px;min-width:640px}
th{background:var(--body);color:#fff;text-align:left;padding:7px 9px;font-weight:700}
td{border-bottom:1px solid var(--soft);padding:6px 9px;vertical-align:top}
tr:nth-child(even) td{background:var(--n50)}
pre{background:var(--code);color:#EDEDEF;padding:14px;border-radius:6px;overflow:auto;font-size:12.5px;line-height:1.45}
.flag{display:inline-block;font-size:11px;font-weight:700;color:#7A4B00;background:#FFF1D6;border:1px solid #F0C978;border-radius:3px;padding:0 5px;margin-left:4px}
.box{border-left:4px solid var(--accent);background:var(--n50);padding:12px 16px;margin:14px 0;border-radius:0 6px 6px 0}
.box p{margin:4px 0}
.box ul{margin:6px 0;padding-left:20px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin:12px 0}
.card{border:1px solid var(--soft);border-top:3px solid var(--accent);border-radius:6px;padding:12px 14px}
.card h4{margin:0 0 6px;font-size:15px;color:var(--ink)}
.card p{margin:0;font-size:14px}
footer{border-top:1px solid var(--soft);color:var(--muted);font-size:12.5px;padding:16px 32px}
@media (max-width:1100px){.flow-grid{grid-template-columns:minmax(0,1fr)}}
@media (max-width:700px){header.top{padding:20px 18px}header.top h1{font-size:23px}h2{font-size:21px}nav.toc{padding:8px 18px;flex-wrap:nowrap;overflow-x:auto;font-size:13px;-webkit-overflow-scrolling:touch}main{padding:4px 16px 32px}.diagram svg{min-width:760px}}
@media print{nav.toc{display:none}.tabs,.tabs-lead{display:none}.js .tabpanel:not(.active){position:static;height:auto;overflow:visible;visibility:visible}.tabpanel+.tabpanel{break-before:page}section.view{break-before:page}.diagram svg{min-width:0}.flow-grid{grid-template-columns:minmax(0,1fr) 300px}details{display:block}details>*{display:block}header.top,th,.lvl,.steps li::before{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
@page{size:A3 landscape;margin:12mm}
"""


def css():
    root = (f":root{{--accent:{T['accent']};--accent-text:{T['accent_text']};--tint:{T['tint']};--ink:{T['ink']};"
            f"--body:{T['body']};--muted:{T['muted']};--line:{T['line']};--soft:{T['soft']};--n50:{T['n50']};"
            f"--code:{T['code_bg']};--font:{T['font']}}}")
    return "\n" + root + CSS_BODY


def section(view):
    s = view.spec
    return f"""
<section class="view" id="{s['id']}">
  <h2><span class="lvl">{esc(s['level'])}</span>{esc(s['title'])}</h2>
  <p class="scope"><b>Diagram type:</b> {esc(s['kind'])}. <b>Scope:</b> {esc(s['scope'])}</p>{view_body(view)}
</section>"""


def view_body(view):
    return f"""
  <div class="diagram">{view.svg()}</div>
  <p class="hint">On a small screen, scroll the diagram sideways or zoom in; the tables below carry the same content as text.</p>{view_extras(view)}"""


def view_extras(view, detailed=""):
    """Key, notes and the collapsed lists of a static view; `detailed` goes between the notes and the lists."""
    s = view.spec
    notes = "".join(f"<li>{esc(n)}</li>" for n in s.get("notes", []))
    return f"""
  <h3>Key</h3>
  {legend_html(view)}
  {'<h3>Notes</h3><ul class="notes">' + notes + '</ul>' if notes else ''}{detailed}
  <details><summary>Elements ({len(s['nodes'])})</summary>{catalogue_html(list(s['nodes']))}</details>
  <details><summary>Relationships ({len(s['edges'])})</summary>{relations_html(view)}</details>
  <details><summary>Diagram as code (Mermaid C4)</summary><pre>{esc(mermaid(s))}</pre></details>"""


def tabbed_section(view, overview, flows):
    """The view the use cases are drawn on: one tab for the whole diagram, one tab per use case.

    The first tab draws the same compact layout as the use cases, so switching tabs changes
    what is lit, never the picture; the detailed static diagram sits collapsed below it.
    """
    s = view.spec
    oid = f"{s['id']}-all"
    tabs = [f'<button type="button" role="tab" id="tab-{oid}" aria-controls="{oid}" aria-selected="true">'
            f'{esc(overview_tab(s))}</button>']
    for n, fv in enumerate(flows, 1):
        f = fv.flow
        tabs.append(f'<button type="button" role="tab" id="tab-{f["id"]}" aria-controls="{f["id"]}" aria-selected="false" tabindex="-1">'
                    f'<span class="num">{n}</span>{esc(f["short"])}</button>')
    lead = s.get("flows_lead", f"Choose a view. Every tab shows the same picture: {overview_tab(s)} draws every element and "
                               "relationship, each of the others lights up the elements and calls it uses, numbers them in order "
                               "and lists the steps beside it.")
    panels = [overview_panel(overview, view, flows)] + [flow_panel(fv) for fv in flows]
    return f"""
<section class="view" id="{s['id']}">
  <h2><span class="lvl">{esc(s['level'])}</span>{esc(s['title'])}</h2>
  <p class="scope"><b>Diagram type:</b> {esc(s['kind'])}, with its use cases as dynamic diagrams. <b>Scope:</b> {esc(s['scope'])}</p>
  <p class="tabs-lead">{esc(lead)}</p>
  <div class="tabs" role="tablist" aria-label="Views of the {esc(s['kind'])} diagram">{''.join(tabs)}</div>
  {''.join(panels)}
</section>"""


def overview_panel(view, static, flows):
    s = view.spec
    oid = f"{s['id']}-all"
    ucs = "".join(f'<li><span><a href="#{fv.flow["id"]}"><b>{esc(fv.flow["short"])}</b></a>. {esc(fv.flow["lead"])}</span></li>'
                  for fv in flows)
    lead = s.get("overview_lead", f"Every element and relationship of the {s['kind']} diagram, on the map the other tabs light up.")
    detailed = ('\n  <details><summary>Detailed diagram, with responsibilities and arrow labels</summary>'
                f'<div class="diagram">{static.svg()}</div></details>')
    return f"""
<div class="tabpanel active" role="tabpanel" id="{oid}" aria-labelledby="tab-{oid}">
  <h3 class="uc-title">{esc(overview_tab(s))}</h3>
  <p class="lead">{esc(lead)}</p>
  <p class="scope"><b>Diagram type:</b> {esc(s['kind'])}. <b>Elements:</b> {len(view.nodes)}. <b>Relationships:</b> {len(s['edges'])}.</p>
  <div class="flow-grid">
    <div>
      <div class="diagram">{view.svg()}</div>
      <p class="note">Names and types only. Responsibilities and arrow labels are in the detailed diagram and in the lists below.</p>
    </div>
    <aside class="steps" aria-label="{esc(s.get('flows_name', 'Use cases'))}"><h3>{esc(s.get('flows_name', 'Use cases'))}</h3><ol>{ucs}</ol></aside>
  </div>{view_extras(static, detailed)}
</div>"""


def overview_tab(spec):
    return spec.get("overview_tab", OVERVIEW_TAB.get(spec["kind"], "Everything"))


def flow_panel(view):
    f, s = view.flow, view.spec
    steps = "".join(f"<li><span>{esc(st['text'])}</span></li>" for st in f["steps"])
    return f"""
<div class="tabpanel" role="tabpanel" id="{f['id']}" aria-labelledby="tab-{f['id']}">
  <h3 class="uc-title">{esc(f['title'])}</h3>
  <p class="lead">{esc(f['lead'])}</p>
  <p class="scope"><b>Diagram type:</b> Dynamic, on the {esc(s['kind'])} diagram. <b>Elements involved:</b> {len(f['hi'])} of {len(view.nodes)}.</p>
  <div class="flow-grid">
    <div>
      <div class="diagram">{view.svg()}</div>
      <p class="note">Highlighted: the elements and calls of this {esc(s.get('flow_noun', 'use case'))}. Badges match the step numbers.</p>
    </div>
    <aside class="steps" aria-label="Steps of {esc(f['title'])}"><h3>Steps</h3><ol>{steps}</ol></aside>
  </div>
  {flow_legend(s)}
  <details><summary>Diagram as code (Mermaid C4 dynamic)</summary><pre>{esc(mermaid(s, f))}</pre></details>
</div>"""


TABS_JS = """
(function () {
  function activate(tab, focus) {
    var list = tab.closest("[role=tablist]");
    list.querySelectorAll("[role=tab]").forEach(function (t) {
      var on = t === tab;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute("aria-controls")).classList.toggle("active", on);
    });
    // On a narrow screen the row scrolls: bring the chosen tab into view without moving the page.
    var lr = list.getBoundingClientRect(), tr = tab.getBoundingClientRect();
    if (tr.left < lr.left) list.scrollLeft -= lr.left - tr.left + 16;
    else if (tr.right > lr.right) list.scrollLeft += tr.right - lr.right + 16;
    if (focus) tab.focus();
  }
  document.querySelectorAll("[role=tablist]").forEach(function (list) {
    var tabs = Array.prototype.slice.call(list.querySelectorAll("[role=tab]"));
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () {
        activate(t);
        history.replaceState(null, "", "#" + t.getAttribute("aria-controls"));
      });
      t.addEventListener("keydown", function (e) {
        var j = {ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1}[e.key];
        if (j === undefined) return;
        e.preventDefault();
        activate(tabs[(j + tabs.length) % tabs.length], true);
      });
    });
  });
  function fromHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    var tab = document.querySelector('[role=tab][aria-controls="' + id.replace(/"/g, "") + '"]');
    if (tab) { activate(tab); tab.closest("section").scrollIntoView(); }
  }
  window.addEventListener("hashchange", fromHash);
  fromHash();
})();
"""


def links(pairs):
    return "".join(f'<a href="#{a}">{esc(t)}</a>' for a, t in pairs)


def build():
    views = [View(v) for v in VIEWS]
    # a view with `flows` gets a tab menu: an overview on its compact layout, then one tab per flow
    tabbed = {v["id"]: (View(v, overview=True), [View(v, f) for f in v["flows"]]) for v in VIEWS if v.get("flows")}
    problems = []
    for v in views + [t for ov, fl in tabbed.values() for t in [ov] + fl]:
        v.boundary_svg()
        problems += [f"{v.sid}: {w}" for w in v.warnings]
    toc = []
    body = [DOC["intro"]]
    for v in views:
        toc.append(f'<a href="#{v.spec["id"]}">{esc(v.spec["level"])}: {esc(v.spec["nav"])}</a>')
        body.append(tabbed_section(v, *tabbed[v.spec["id"]]) if v.spec["id"] in tabbed else section(v))
    body.append(DOC["outro"])
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(DOC['title'])}</title>
<style>{css()}</style>
<script>document.documentElement.classList.add("js")</script>
</head>
<body>
<header class="top">
  <p class="eyebrow">{esc(DOC['eyebrow'])}</p>
  <h1>{esc(DOC['title'])}</h1>
  <p>{esc(DOC['subtitle'])}</p>
  <div class="meta">{DOC['meta']}</div>
</header>
<nav class="toc" aria-label="Contents">{links(DOC.get("toc_before", [("about", "About this model")]))}{''.join(toc)}{links(DOC.get("toc_after", [("decisions", "Open decisions"), ("conformance", "C4 conformance")]))}</nav>
<main>
{''.join(body)}
</main>
<footer>{DOC['footer']}</footer>
<script>{TABS_JS}</script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"written {OUT} ({len(page)} bytes), {len(views)} views, {sum(len(fl) for _, fl in tabbed.values())} flows "
          f"in {len(tabbed)} tabbed views")
    for p in problems:
        print("WARN", p)
    return problems


if __name__ == "__main__":
    sys.exit(1 if build() else 0)
