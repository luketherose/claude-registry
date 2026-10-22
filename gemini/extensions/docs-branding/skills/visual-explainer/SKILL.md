---
name: visual-explainer
description: This skill should be used when the user asks to explain a system, workflow, architecture, pipeline or process visually and in very simple terms, as one interactive HTML page. Trigger phrases include "fammi una cosa visuale", "graficami", "spiegami con uno schema", "make me a visual explainer", "a page like this one". It ships the house template (dashed zones, clickable components, flow buttons that animate numbered steps, side panel, optional yes/no table, light and dark mode) and the rules to fill and verify it. Not for UML notation (uml-diagram-generator), slide decks (presentation-creator) or data charts.
---

# Visual explainer

One self-contained HTML page that explains how something works: a diagram of zones and components, a few flows that light up their steps in order, a side panel with the step list and the detail of the clicked component. The template is [assets/template.html](assets/template.html): fixed CSS and rendering code, placeholder data.

## 1. Before writing

- State the target path and get the user's confirmation. Suggest the docs folder of the project the page explains.
- Read the sources first: code, README, docs, run state. Every claim on the page is checked against them. No numbers or behaviours from memory.

## 2. Content rules

- The user's language, in words a non-specialist understands. Jargon is explained in the node detail, never in the title.
- Terse. Node title 1 to 3 words. At most 3 subtitle lines of about 32 characters. Node detail at most 3 short sentences. One sentence per step.
- 3 to 5 flows, each with at most 7 steps. `Panoramica` (overview) is always first: the one key idea in two lines, no steps.
- The legend categories answer the real question, for example code without AI, AI component, files, people. The four `cat` values are `det`, `ai`, `doc` and `you`; rename their labels in `TAG` and in the HTML legend together.
- When the user asked a literal question ("did we build it with skills, agents or what?"), answer it in the `qa` table: one row per option, yes or no, one sentence each. Remove the section otherwise.
- The footer says where things live, as paths.
- No em dash and no double hyphen as punctuation. Commas, colons, parentheses or the middle dot instead.

## 3. Building

1. Copy `assets/template.html` to the confirmed path.
2. Edit the header, the flow buttons (one per key of `FLOWS`), the legend, the `qa` section, the footer and the data block between `DATI` and `FINE DATI`. Leave the CSS and the rendering code alone.
3. The template's interface strings are Italian: `Panoramica`, `Flussi`, `Chiudi`, `Collegato a:`, the overview hint, the legend entries `Fase` and `Passaggio`. Translate them when the user writes in another language.
4. Geometry, in SVG units:
   - Zones left to right in reading order; a closing phase can take a bottom row.
   - Nodes on a grid, at least 40 units between boxes. Box width is at least 14 plus 6 per character of the longest subtitle line.
   - Edges are orthogonal paths (`M`, `H`, `V`) from box edge to box edge. Avoid crossings; when two paths share a gap, separate them in y rather than running them side by side.
   - Edge labels are 1 to 3 words in the gap between boxes, never on a box. The step badge `b` sits on the path, away from the label.
   - `viewBox` covers the used area with about 16 units of margin around the zones.
5. `FLOWS[k].nodes` lists the nodes that stay bright in that flow. `steps` reference edge ids in order; `null` marks a step with no edge.

## 4. Verification, before calling it done

- Render it at 1440 px and at 375 px, in light and in dark mode. Headless Chrome gives screenshots: `chrome --headless=new --screenshot=<png> --window-size=1440,1250 file://<path>` (on macOS the binary is inside `Google Chrome.app/Contents/MacOS/`). Use a browser preview with device emulation for clicks and the 375 px check.
- At 375 px `document.documentElement.scrollWidth` equals the viewport width: only the diagram scrolls, inside its card.
- Click every flow: the badges and lit edges equal the steps that have an edge. Click one node: the panel shows its detail and its links. No console errors.
- Look at the screenshots for labels over boxes, crossed edges and text running past a box edge.
- No U+2014 character in the file.
- Show the user the screenshot or the measured values, then call it done.

## 5. After

In a docs folder with an index, add the row: title, version, date, one-line summary. A new version moves the previous one to the archive.
