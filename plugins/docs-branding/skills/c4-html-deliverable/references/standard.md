# House standard for C4 architecture pages in HTML

The rules every C4 deliverable built with this skill follows: one page layout, one notation, one set of checks before delivery. The engine in `scripts/` implements them; this file says what they are and why.

## Contents

1. Principles
2. Page structure
3. The tab menu of a chapter
4. Use-case panels
5. Zones and boundaries
6. Themes, palette and type
7. Modelling rules
8. Checks before delivery
9. Versions and filing

## 1. Principles

- **One model, many views.** Elements and their texts live once, in `model.py`. Every diagram takes them from there, so an element keeps its name, colour and shape on every level. The HTML file is generated and never edited by hand.
- **C4 notation** as published on c4model.com (the `c4-architecture` skill of the `analysis-architecture` plugin covers it in depth): a title stating type and scope, a key on every diagram, name, type, technology and responsibility on every element, one-directional arrows labelled with intent and protocol, acronyms explained.
- **A little at a time.** The full Container diagram stays, but the reading goes through the use cases: each lights up only the elements and calls it uses.
- **Colour is never the only signal.** Highlighted also means a thicker border and numbered calls; dimmed also means a dashed border and grey text.

## 2. Page structure

1. **Header**: a bar in the theme colour, a client and programme line (eyebrow), the title, a subtitle naming the levels, then version, date, author and classification.
2. **Contents bar**, sticky at the top. On a phone it is one row that scrolls sideways.
3. **About this model**: scope, baseline sources, what changed from the previous version, status, one card per level, what stays out of scope.
4. **Level 1**, System Context.
5. **Level 2**, Container, with its use cases in a tab menu (section 3).
6. **Level 3**, Component: one diagram per container that needs it, with its internal paths in a tab menu when they help. A container that does one job stays described at Level 2, and the About section says so.
7. **Open decisions**: a table with the proposal drawn in the model, the alternative and the diagrams it affects.
8. **C4 conformance**: how the notation rules are applied, acronyms, sources.

Every static view carries: title, a "Diagram type / Scope" line, the diagram, its key, notes, the list of elements, the list of relationships (an assumption is marked as such) and the source as Mermaid C4 code in a collapsed block.

## 3. The tab menu of a chapter

- The Container chapter always carries one, for the main use cases. A Component chapter carries one when its container has paths a reader needs to follow (a call becoming an event, a timer firing); its tabs are called internal paths.
- Under the chapter title sits one lead sentence, then a horizontal tab menu: the first tab (`All containers` or `All components`), then one tab per use case or path, numbered, with a short name of two or three words.
- **Every tab shows the same picture**: the compact layout of the chapter's view. The first tab draws every element and relationship in its normal style, with the list of use cases or paths beside it, each linking to its tab; the use-case tabs light up their part of it. Switching tabs changes what is lit, never the picture.
- The compact picture carries names and types only. The first tab keeps the detailed Container diagram, with responsibilities and arrow labels, collapsed below it, then the key, the notes, the lists and the Mermaid source.
- Choosing a tab shows its panel only. The address bar takes the panel id (`#l2-all`, `#uc1`, `#cm2`, ...), so a link opens the page on that tab. Each chapter's menu is independent.
- Keyboard: arrow keys move between tabs, Home and End jump to the first and last. The markup follows the ARIA tabs pattern (`tablist`, `tab`, `tabpanel`, `aria-selected`).
- On a narrow screen the row scrolls sideways and the chosen tab is brought into view.
- Without JavaScript every panel is shown one after the other; in print every panel prints, each on a new page, and the menu is hidden.
- Inactive panels stay laid out, collapsed and invisible, never `display:none`: Safari draws an SVG wrongly when it is first laid out hidden and shown later.
- Three to five tabs after the first. Fewer makes the menu pointless; more means the diagram is doing too much.

## 4. Use-case panels

Each use case is a C4 dynamic diagram drawn on the Container layout, so the reader keeps the same map. The internal paths of a Component chapter follow the same rules on its own layout.

- Title `Use case N: <verb> <object>`, then one sentence saying what happens and for whom.
- On the left, the diagram in compact form: boxes carry name and type only, in larger type. On the right, the **Steps** panel: one sentence per step, five or six steps at most.
- Elements in the use case: accent border and light accent fill. The rest: dashed grey border and grey text, kept for orientation.
- Calls in the use case: a thick accent arrow with the step badge. A call used in two steps carries two badges. A step with no call (an external system doing its own work) puts its badge on the element.
- Below: the note "Highlighted: the elements and calls of this use case. Badges match the step numbers.", the use-case key, and the Mermaid `C4Dynamic` source with `RelIndex`.
- Below 1100 px the Steps panel moves under the diagram.

## 5. Zones and boundaries

- **Dashed grey area**: where a group of elements runs (corporate network, cluster, managed services, the client's external systems). Its name sits at the top, left or right.
- **Dashed accent area**: the boundary of the system in scope, with its name and type at the top.
- At Level 3 the container in scope is a dashed accent boundary with its name and type at the bottom left.
- Network detail (virtual IPs, ingress, private access) belongs to a deployment view, not to these diagrams.

## 6. Themes, palette and type

`DOC["theme"]` picks the palette. Use the client's theme for a client deliverable and the Accenture theme for an internal one. A client theme never mixes in another brand's colours: no blue and no purple in a UniCredit page.

| Role | `unicredit` | `accenture` |
|---|---|---|
| Lines, borders, top bar, system boundary, highlighted arrows | `#E30613` | `#A100FF` |
| Accent text, step badges, level labels (AA on white) | `#B00010` | `#7500C0` |
| Fill of a highlighted element or of the system in scope | `#FCE6E8` | `#F4F0FF` |
| Headings / body / secondary text | `#0E0E12` / `#3F3F46` / `#7B7B85` | `#000000` / `#333333` / `#6E6E66` |
| Persons and external systems | fill `#EDEDEF`, border `#7B7B85` | fill `#E6E6DC`, border `#6E6E66` |
| Dimmed elements | dashed `#D6D6DC`, text `#A3A3AD` | dashed `#DADAD2`, text `#A8A8A0` |
| Page font | UniCredit, Dax, FS Joey, Inter, system fonts | Graphik, Arial |

The UniCredit tokens come from the `unicredit-design-system` skill, the Accenture ones from `accenture-branding`. Diagrams use Arial in both themes, so text widths stay predictable for the collision check.

Shapes: person; software system (rectangle); container (white rectangle); application running in the browser (window with a title bar, kind `spa`); data store (cylinder, kind `db`); component (light grey rectangle); infrastructure node such as a virtual IP (light grey pill, kind `infra`).

A new theme is a new entry in `THEMES` in `scripts/render.py` with the same keys, taken from the client's design tokens.

## 7. Modelling rules

- Containers are deployable units, or the application that runs in the browser. Components are not.
- Shared libraries are not containers: they go in the notes. The exception is Level 3, for a library on the path of every call (tenant context, security): draw it as the components it adds to the container, with the library named in their technology.
- External systems are black boxes.
- Network entry points (virtual IPs, load balancers) are infrastructure, not containers. Draw them, as `infra` nodes outside the system boundary, only when the reader needs the entry path; their detail (ingress, internal load balancers, namespaces) belongs to a deployment view.
- Fewer than 20 elements per diagram.
- Decisions are not drawn as diagram text: they go in the Open decisions table.
- An assumption of the model is marked `assumption=True` on its relationship and also appears among the open decisions.

## 8. Checks before delivery

1. `python3 -I scripts/check.py <project_dir>` ends with `TOTAL 0`. It reports arrows crossing a box, labels and badges overlapping each other, a box or a zone label, zones overlapping, and anything off the canvas, for every view and every use case.
2. `python3 -I scripts/build.py <project_dir> <out.html>` exits 0. It refuses to finish quietly with warnings left.
3. Preview at 1440 px and at 375 px. At 375 px `document.documentElement.scrollWidth` equals the viewport width: only the diagrams scroll, inside their frame. Every tab shows its own panel and the same picture; the badges equal the step calls.
4. No em dash and no double hyphen as punctuation in the texts; no internal names or tracker codes in a client deliverable.
5. Show the user the screenshots or the measured values before calling it done.

## 9. Versions and filing

- A new version is a new file name (`_v2`, `_v3`) and a new `Version` in `DOC["meta"]`, with the "What changed" box rewritten.
- Keep the project folder (`model.py`, `views.py`, `doc.py`) next to the HTML, so the next version starts from the model, not from the page.
- In a folder with an index, update its row (title, version, date, one-line summary) and move the superseded version out.
