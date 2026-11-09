"""Texts of the page around the diagrams. `theme` picks the palette: "unicredit" or "accenture"."""

DOC = dict(
    theme="unicredit",
    eyebrow="Example Group  |  Order management",
    title="C4 model of the Order Management Platform",
    subtitle="Levels 1 to 3: System Context, Containers with the main use cases, and Components",
    meta=("<span><b>Version</b> 0.1, draft</span><span><b>Date</b> 1 January 2027</span>"
          "<span><b>Prepared by</b> Architecture team</span><span><b>Classification</b> Internal</span>"),
    footer="Draft. Diagrams follow the C4 model by Simon Brown (<a href=\"https://c4model.com\">c4model.com</a>).",
    toc_before=[("about", "About this model")],
    toc_after=[("decisions", "Open decisions"), ("conformance", "C4 conformance")],
    intro="""
<section id="about">
  <h2>About this model</h2>
  <p>This set describes the <b>Order Management Platform</b>: who uses it, what it is made of and how its main use cases run.</p>
  <div class="box"><p><b>Status.</b> Draft. See <a href="#decisions">Open decisions</a>.</p></div>
  <div class="cards">
    <div class="card"><h4>Level 1, System Context</h4><p>The platform as one box, its users and the systems it depends on.</p></div>
    <div class="card"><h4>Level 2, Containers and use cases</h4><p>The deployable parts, grouped by where they run, then each main use case step by step.</p></div>
    <div class="card"><h4>Level 3, Components</h4><p>Inside the Order API.</p></div>
  </div>
</section>
""",
    outro="""
<section id="decisions">
  <h2>Open decisions</h2>
  <div class="tbl"><table>
    <thead><tr><th>#</th><th>Topic</th><th>Proposal in this model</th><th>Alternative</th><th>Diagrams affected</th></tr></thead>
    <tbody>
      <tr><td>1</td><td>ERP interface</td><td>REST call from the fulfilment worker (an assumption in this model)</td><td>File drop read by the ERP</td><td>L2, use case 2</td></tr>
    </tbody>
  </table></div>
</section>

<section id="conformance">
  <h2>C4 conformance</h2>
  <ul class="notes">
    <li>Every diagram has a title with its type and scope, and its own key.</li>
    <li>Every element states its name, type, technology and responsibility; every arrow its intent and protocol.</li>
    <li>The use cases are dynamic diagrams drawn on the Container layout.</li>
  </ul>
</section>
""",
)
