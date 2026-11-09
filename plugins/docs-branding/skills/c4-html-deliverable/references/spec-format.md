# Project files: format and layout tuning

A project is a folder with three Python files. The engine imports them; they hold data only. The worked example in `assets/template/` uses every field below.

## Contents

1. model.py: elements and relationships
2. views.py: static views
3. views.py: tabs and flows
4. doc.py: the text around the diagrams
5. Reading the check output
6. Tuning a layout

## 1. model.py: elements and relationships

`ELEMENTS` maps a short id to one element. Prefix ids by kind so views stay readable: `p_` person, `s_` system in scope, `x_` external system, `c_` container, a short letter per container for its components.

| Key | Meaning |
|---|---|
| `kind` | `person`, `system`, `system_ext`, `container`, `spa` (application running in the browser), `db` (data store), `component`, `infra` (a network element such as a virtual IP) |
| `name` | Name shown in the box |
| `tech` | Technology; required for `container`, `spa`, `db`, `component` and `infra`, shown as `[Container: <tech>]`, `[Component: <tech>]` or `[Infrastructure: <tech>]` |
| `desc` | Responsibility in one line; shown in the detailed diagram, left out in the tabs |

`R(src, dst, label, tech="", ...)` builds one relationship. Keep it in `model.py` and import it in `views.py`.

| Parameter | Meaning |
|---|---|
| `label` | Intent, as a verb phrase: "Reads and writes orders" |
| `tech` | Protocol or technology when the call crosses a process boundary: "JSON/HTTPS", "JDBC", "Kafka" |
| `style` | `sync` (solid) or `async` (dashed) |
| `via` | Waypoints `[(x, y), ...]` in the static view, to route around a box |
| `t` | Position of the label along the path, 0 to 1 |
| `dx`, `dy` | Extra offset of the label, in canvas units |
| `shift` | Parallel offset, for two arrows between the same pair (use `-14` on both) |
| `wc` | Label wrap width in characters |
| `assumption` | `True` marks the relationship as an assumption in the list of relationships |
| `key` | Name the flow steps use; default `"src>dst"`. Set it when two relationships share the same pair |
| `bt` | Position of the step badge along the path, when it must differ from `t` |

## 2. views.py: static views

Each view is a `dict`. `VIEWS` lists them in page order.

| Key | Meaning |
|---|---|
| `id` | Anchor of the section: `l1`, `l2`, `l3-api` |
| `level`, `kind` | "Level 2", "Container"; shown in the title bar and the Diagram type line |
| `nav` | Short name in the contents bar |
| `title`, `scope` | Diagram title and one-sentence scope |
| `size` | Canvas `(width, height)` in SVG units |
| `nodes` | `{id: (centre x, centre y, box width)}`; height follows the text |
| `edges` | List of `R(...)` |
| `zones` | Dashed areas, listed inner first (below) |
| `boundary` | Level 3 only: `dict(eid=<container id>, members=[component ids])` |
| `notes` | Short sentences under the diagram |
| `flows`, `flow_layout` | A tab menu on this view (section 3) |
| `overview_tab` | Label of the first tab; default "All containers" or "All components" by `kind` |
| `overview_lead`, `flows_lead` | The sentence under the first tab's title, and the one above the menu |
| `flows_name`, `flow_noun` | Heading of the list beside the first tab and the word for one flow; default "Use cases" and "use case", for example "Internal paths" and "path" at Level 3 |

A zone is `dict(id, label, members, pad=28)` plus, optionally:

- `sub`: a second line under the label, for the system boundary ("[Software System] in the corporate cloud");
- `kind="system"` with `eid=<system id>`: the dashed accent boundary of the system in scope;
- `anchor="right"`: label at the top right, when the left corner is busy with arrows;
- `members` may name other zones: list the inner zones first, then the zone that wraps them.

## 3. views.py: tabs and flows

Any view gets a tab menu when it has `flows`: the Container view for the main use cases, a Component view for the paths inside its container. Set them after the dict, in tab order: `L2["flows"] = [...]`. Flow ids are page anchors, so they are unique across the page (`uc1` at Level 2, `cm1` at Level 3).

| Key | Meaning |
|---|---|
| `id` | Panel id and deep link: `uc1`, `uc2`, `cm1` |
| `short` | Tab label, two or three words |
| `title` | `Use case N: <verb> <object>`, or `Path N: ...` at Level 3 |
| `lead` | One sentence: what happens and for whom |
| `hi` | Ids of the elements that stay bright |
| `steps` | List of `dict(text=..., calls=[...])` |

Each step's `calls` names relationships by key (`"c_api>c_db"`, or the `key` given in `R`). `"@x_erp"` marks a step that is the element's own work: the badge goes on the element. A call used in two steps gets two badges.

`flow_layout` on a view with `flows` holds the compact arrangement drawn by every tab, the first one included: `size`, `nodes` (same ids, narrower boxes, about 0.7 of the static canvas) and, optionally, `via` as `{key: [(x, y), ...]}` to route one call around a box in the compact layout only; `k` scales `shift` there (default 1). Static `via` values are not reused there, because the coordinates differ.

## 4. doc.py: the text around the diagrams

| Key | Meaning |
|---|---|
| `theme` | `"unicredit"` or `"accenture"` |
| `eyebrow`, `title`, `subtitle` | Header lines |
| `meta` | HTML: `<span><b>Version</b> 0.1</span>` and so on for date, author, classification |
| `footer` | HTML footer line |
| `intro` | HTML sections before Level 1; the default contents bar links to `<section id="about">` |
| `outro` | HTML sections after the last view: `decisions`, `conformance` |
| `toc_before`, `toc_after` | `[(anchor, label)]` around the generated view links in the contents bar; `[]` when `intro` or `outro` is empty |
| `pages` | Extra pages after the model, in a page menu under the header: `dict(id, label, html=...)` or `dict(id, label, file=...)`, the file read from the project folder. The id is the deep link and must not clash with a view or flow id |
| `model_page` | Label of the first tab of the page menu; default "C4 model" |

`intro`, `outro` and the pages are trusted HTML written by the author: they reuse the page classes `view`, `lvl`, `diagram`, `legend`, `box`, `cards`/`card`, `tbl`, `notes` and `scope`. Everything else is escaped. A page diagram wider than the screen sets its own `min-width` on the `svg`, so it stays readable and scrolls inside its frame.

## 5. Reading the check output

`check.py <project_dir> [-v] [ids]` prints `== <view, view/all or view/flow> <count>` and one line per warning. `-v` adds the coordinates of every label, badge and zone; ids restrict the run, and `all` names the first tab of every tabbed view (`l2/all`, `l3-cm/all`).

| Warning | Usual fix |
|---|---|
| `edge a->b crosses c` | Add `via` waypoints, or move `c` out of the line |
| `label a->b overlaps c` | Change `t`, or nudge with `dx`, `dy`; lower `wc` to make it taller and narrower |
| `label a->b overlaps label c->d` | Move one along its path (`t` 0.3 or 0.7) |
| `label ... overlaps zone label z` | `anchor="right"` on the zone, or move the label |
| `badge n on a->b overlaps ...` | `bt` on that relationship, or a `via` in `flow_layout` |
| `node a overlaps b`, `node a overlaps zone z` | Spread the centres; a zone wraps its members only |
| `zone z overlaps zone y` | Smaller `pad`, or more space between the groups |
| `... outside canvas` | Larger `size`, or move the element in |

## 6. Tuning a layout

- Start from a grid: columns about 380 units apart, rows about 330 apart in a static view.
- Place external systems on the edge of the side they talk to, persons on the left, data stores at the bottom.
- Fix one view at a time with `check.py <dir> <id>`, then run the whole project.
- When a compact layout keeps failing, shrink box widths before moving boxes, and route only the offending call with `flow_layout["via"]`.
- Look at the result anyway: the check finds geometric collisions, not a confusing picture.
