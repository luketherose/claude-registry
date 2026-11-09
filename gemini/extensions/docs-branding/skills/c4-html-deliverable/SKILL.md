---
name: c4-html-deliverable
description: "This skill should be used when producing or updating a C4 architecture deliverable as one self-contained HTML page: System Context, Container and Component diagrams generated from one Python model, the main use cases as dynamic diagrams in a tab menu that lights up the elements and numbered calls of each, and for every view its key, element and relationship lists and Mermaid source. Ships the engine (SVG renderer with a collision check, page builder), a worked example and the house standard, with UniCredit and Accenture themes. Trigger phrases: \"C4 in HTML\", \"pagina C4 per il cliente\", \"diagrams with the use cases highlighted\", \"rigenera il C4\", \"diagrammi di architettura stile UniCredit\". Not for C4 notation questions or Mermaid diagrams in a repository (c4-architecture), simple visual explainers (visual-explainer), UML (uml-diagram-generator), slide decks (presentation-creator), PDF or Word documents (document-creator, unicredit-document-template) or architecture decisions (software-architect)."
---

# C4 HTML deliverable

One HTML page, readable offline, that presents a system with the C4 model: Level 1 System Context, Level 2 Container with three to five use cases in a tab menu, Level 3 Component for the containers that need it, with their internal paths in the same kind of menu, then the open decisions and a conformance section. Every diagram is drawn as inline SVG from one model, so an element keeps its name, colour and shape on every level, and every layout passes a geometric collision check before the page is written.

The house rules are in [references/standard.md](references/standard.md). The format of the project files and the fixes for each check warning are in [references/spec-format.md](references/spec-format.md). A complete worked example (a fictional order platform) is in `assets/template/`.

## What is in the skill

| Path | Role |
|---|---|
| `scripts/render.py` | Draws a view, its compact overview or one of its flows as SVG, lays out zones, labels and badges, reports collisions; holds the themes |
| `scripts/check.py` | Prints the warnings of every view, tab and flow of a project; exit 1 while any is left |
| `scripts/build.py` | Writes the page: header, contents bar, sections, tab menu, keys, lists, Mermaid source; exit 1 with warnings |
| `assets/template/` | `model.py`, `views.py`, `doc.py` of the worked example, the starting point of every project |

The engine never changes per project. A project is the three data files only.

## 1. Before building

- State the target path of the HTML and get the user's confirmation. The project files go in a folder beside it (for example `<name>_sorgenti/`), so the next version starts from the model.
- Read the sources first: architecture documents, code, plans, decisions already taken. Every element and every call must be traceable to one of them. What the sources do not say is an assumption: mark it (`assumption=True`) and list it in the open decisions.
- Agree the scope with the user when it is not given: the system in scope, which containers get a Level 3 diagram, and the three to five use cases worth a tab. Use cases are the journeys a reader asks about, named with a verb and an object.
- Pick the theme: the client's for a client deliverable (`unicredit`), `accenture` for an internal one. A client page never mixes in another brand's colours.
- Client material stays with the client deliverable: never copy a project's model into this registry or into another shared repository.

## 2. Set up the project

Copy the three template files into the project folder, then replace the example content:

```bash
mkdir -p <project_dir> && cp assets/template/*.py <project_dir>/
```

Run every command from this skill's directory, with `python3 -I` and absolute paths for the project and the output. Isolated mode keeps a stray module in the current directory or in `PYTHONPATH` from being imported in place of the project's files; the scripts add their own directory and the project directory to the path themselves.

## 3. Write the model

Work in this order, checking each view as it is written (the field-by-field format is in [references/spec-format.md](references/spec-format.md)):

1. `model.py`: every person, system, container and component once, with kind, name, technology and responsibility. Relationships are built with `R(...)` in the views.
2. Level 1 in `views.py`: the system as one box, its users, the external systems. Group them in zones only when where they run matters to the reader.
3. Level 2: containers grouped by where they run (dashed grey zones), the system boundary as a zone of kind `system`, external systems as black boxes, every arrow with intent and protocol.
4. The use cases: a `flow_layout` on L2 (the compact arrangement every tab draws), then `L2["flows"]`, each with the elements to light up and one sentence per step naming the calls it uses.
5. Level 3: one view per container that needs it, with a `boundary` around its components and the neighbours it talks to outside. When a reader needs to follow its internal paths, give it a `flow_layout` and `flows` too, with `flows_name="Internal paths"` and `flow_noun="path"`.
6. `doc.py`: theme, header lines, version and date, the About section with "What changed", the open decisions table and the conformance section.

Keep fewer than 20 elements per diagram, and keep shared libraries in the notes, not in the boxes.

## 4. Check and build

```bash
python3 -I scripts/check.py <project_dir>
python3 -I scripts/check.py <project_dir> -v l2 uc3
python3 -I scripts/build.py <project_dir> <out.html>
```

- `check.py` must end with `TOTAL 0`. Fix one view at a time; `-v` prints the coordinates of labels, badges and zones, and the ids after it restrict the run. The table in [references/spec-format.md](references/spec-format.md) maps each warning to its usual fix (`t`, `dx`, `dy`, `via`, `anchor`, `bt`, `size`).
- `build.py` prints the size, the number of views and flows, and any warning left; with a warning it exits 1, and the page is not deliverable.
- Never edit the generated HTML. Every change goes into the project files and through the build again.

## 5. Verify the page

The check finds geometric collisions, not a confusing picture. Open the page in a browser preview and look:

- At 1440 px: every diagram reads at a glance, labels sit on their own arrow, zone names are not covered.
- Click every tab of every chapter with a menu: only its panel shows, the picture stays the same, the address takes its id, the lit elements are the ones in `hi`, and the badges equal the step calls. Then reload with a use-case id in the address and confirm it opens there.
- At 375 px: `document.documentElement.scrollWidth` equals the viewport width (only the diagrams scroll, inside their frame), the tab row scrolls sideways and the chosen tab is visible.
- No errors in the browser console.
- No U+2014 character in the page, and no internal names or tracker codes in a client deliverable.

Show the user a screenshot or the measured values, then call it done.

## 6. Deliver

- File name with the version (`<Name>_C4_Model_v2.html`), the `Version` and the date in `DOC["meta"]`, the "What changed" box rewritten for the new version.
- The project folder beside the HTML, without `__pycache__`.
- In a folder with an index, update its row (title, version, date, one-line summary) and move the superseded version out.

## Easy to miss

- A view with `flows` needs a `flow_layout`: every tab, the first one included, draws that compact picture, because the static coordinates are too wide for the larger type. The static diagram stays, collapsed under the first tab.
- Two relationships between the same pair need a `key` each, or the steps cannot tell them apart; draw them apart with `shift=-14` on both.
- Static `via` waypoints are not used in the tabs; route a call there with `flow_layout["via"]`.
- Virtual IPs and load balancers are `infra` nodes, drawn outside the system boundary only when the entry path matters to the reader; the rest of the network goes in a deployment view.
- Diagrams are drawn in Arial whatever the page font, because the collision check measures text by character count.
- A theme is a dict in `THEMES` in `scripts/render.py`. A new client gets a new entry built from its design tokens, not a hand-edited page.
- Print shows every tab panel on its own page and hides the menu; without JavaScript every panel is shown in sequence.
