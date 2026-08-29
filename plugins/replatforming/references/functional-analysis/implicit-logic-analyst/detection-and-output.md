# Detection patterns and output schema — `implicit-logic-analyst`

> Reference doc for `implicit-logic-analyst`. Read at runtime when scanning
> for implicit logic and when writing `12-implicit-logic.md`. Holds the
> seven-category detection catalogue, the source-descent rules, and the
> output schema that the agent body compresses into one-liners.

---

## Detection-pattern catalogue (seven categories)

### 1. Validation embedded in widgets (Streamlit mode)

Scan `.indexing-kb/05-streamlit/ui-patterns.md` and per-screen files for
widget parameters that encode validation:

- `st.number_input(min_value=, max_value=, step=, format=)`
- `st.text_input(max_chars=, placeholder=, type='password')`
- `st.selectbox(options=...)` — implicit "must be one of"
- `st.date_input(min_value=, max_value=)`
- `st.file_uploader(type=[...], accept_multiple_files=)`
- `st.slider(min_value=, max_value=, step=)`

For each constraint, capture:

- the input it constrains (link to IN-NN)
- the rule in business language
- whether it is **silent** (no user-facing error message) or **explicit**
  (Streamlit shows an error)

Cross-check `.indexing-kb/07-business-logic/validation-rules.md`:

- if the rule is already there, do NOT re-document — just reference it
- if it's missing, capture it as new implicit logic

### 2. Conditional rendering branches

Look for branches that gate UI based on state:

- `if st.session_state.X: render_thing_a() else: render_thing_b()`
- `if user_role == "admin": show_admin_panel()`
- `if df.empty: st.warning(...) else: render(df)`

Each branch is a **rule-in-disguise**. Capture as IL-NN with:

- the gating condition
- the consequence (which features / outputs become visible)
- the actor implications (e.g., admin-only feature)

### 3. State-driven behaviors

Identify session_state keys that act as **flags or state machines**:

- step counters (`st.session_state.step`)
- mode toggles (`st.session_state.mode = 'edit' | 'view'`)
- "has run once" flags
- caching keys that gate expensive computation

For each, document the implicit state machine:

- states (possible values)
- transitions (what mutates the key)
- behaviors gated by each state

### 4. Callback chains and reactive cascades

Look for `on_change` and `on_click` parameters that mutate state and
trigger downstream effects on rerun. Document the chain:

- widget A's on_change sets state X
- next rerun, code reads state X and conditionally invokes function F
- function F mutates state Y
- next rerun, state Y triggers a different render

This is implicit logic because the cascade is not visible in any single
function — it emerges from the rerun model.

### 5. Magic numbers and hardcoded thresholds

Grep for numeric literals in transformation/business code:

- thresholds (`> 100`, `< 0.5`, `if count >= 1000`)
- timeouts and TTLs (cache TTL, session timeout)
- pagination defaults (`limit=50`, `page_size=20`)
- retry counts and backoff values

For each, capture:

- the constant value
- where it is (file:line)
- the apparent business meaning (or "unknown — see Open questions")

### 6. Silent fallbacks and defaults

Look for `or`, `||`, `.get(key, default)`, `try/except` swallowing:

- `name = data.get("name") or "Unknown"` — silent default
- `try: convert(); except: pass` — silent failure
- `value = config.get("rate", 0.05)` — implicit business default

Each is an implicit decision point with business meaning that the user
never sees.

### 7. Cross-screen state mutations changing UC behavior

From `.indexing-kb/05-streamlit/session-state.md`, identify keys read
in one screen and written in another. For each:

- which UC writes it (Wave 2 output, when available)
- which UC reads it
- how the read UC's behavior changes based on the value

These are the highest-cost implicit dependencies in the codebase.

---

## Source-code descent rules

You MAY read source code directly when:

- a KB reference is too coarse to surface a specific implicit rule
- a callback handler's body is needed to understand a cascade
- a magic number's surrounding context is needed for business interpretation

You MAY NOT:

- re-do work already in `.indexing-kb/07-business-logic/`
- read whole modules — only narrowly scoped grep + targeted Read of
  specific lines
- write source code, modify files, or refactor

When you read source, cite `<repo>/<path>:<line>` in `sources:`.

---

## Output schema — `docs/analysis/01-functional/12-implicit-logic.md`

```markdown
---
agent: implicit-logic-analyst
generated: <ISO-8601>
sources:
  - .indexing-kb/05-streamlit/session-state.md
  - .indexing-kb/05-streamlit/ui-patterns.md
  - .indexing-kb/07-business-logic/business-rules.md
  - <repo>/src/<file>.py:<line>     # only if descended into source
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# Implicit logic catalog

Behavior that shapes outcomes but is not stated as an explicit business
rule. Complementary to `.indexing-kb/07-business-logic/`, which captures
explicit rules. Items here are EMBEDDED in UI, state, callbacks, or code
constants and easily missed in a casual read of the codebase.

## Summary
- Total items: <N>
- Validation embedded in widgets: <N>
- Conditional rendering branches: <N>
- State-driven behaviors: <N>
- Callback chains: <N>
- Magic numbers / thresholds: <N>
- Silent fallbacks / defaults: <N>
- Cross-screen state mutations: <N>

## Catalog

### IL-01 — <Short business-language name>
- **Category**: validation | rendering | state-machine | cascade | constant | fallback | cross-state
- **Description**: <1-2 sentences in plain business language>
- **Where**: <screen S-NN> / <file:line> / <widget id>
- **Trigger / condition**: <when this rule applies>
- **Consequence**: <what changes — feature visibility, output value, validation error>
- **Related**:
  - inputs: IN-04
  - outputs: OUT-02
  - transformations: TR-01
  - use cases: UC-02
- **Sources**:
  - .indexing-kb/05-streamlit/ui-patterns.md
  - <repo>/src/reports.py:142   (only if source-descent was used)
- **Confidence**: high | medium | low
- **Notes**: <anything ambiguous>

### IL-02 — ...

## High-impact items (deserve human review)

Items with broad impact on functional behavior:
- IL-03 — controls visibility of an entire feature
- IL-08 — silent fallback that changes monetary computation outcome
- IL-12 — cross-screen state machine driving the wizard flow

## Magic numbers index

| Constant | Where | Apparent meaning | IL-ID |
|---|---|---|---|
| `100` | reports.py:42 | max rows in preview | IL-04 |
| `0.05` | tax.py:18 | default tax rate | IL-09 |
| `30` | session.py:12 | session timeout (minutes) | IL-15 |

## Cross-screen state machines

For each session_state key acting as a state machine:

### `current_step` (used by S-03 wizard)
- States: `select`, `validate`, `confirm`, `done`
- Transitions:
  - `select → validate`: button "Next" on S-03
  - `validate → confirm`: validation passes (see IL-04)
  - `validate → select`: validation fails
  - `confirm → done`: button "Submit"
- Reset: navigation away from S-03 sets back to `select`

## Open questions
- <e.g., "IL-08 — fallback to default tax rate of 0.05 when config is
  missing; is this a documented business decision or accidental
  behavior?">
```
