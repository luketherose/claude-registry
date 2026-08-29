# Method details — `io-catalog-analyst`

> Reference doc for `io-catalog-analyst`. Read at runtime when first building
> the inputs / outputs / transformations catalogs. Holds the category lists,
> Streamlit-specific rules, and validation-metadata rules that the agent body
> compresses into one-liners.

---

## 1. Inputs catalog — categories

An **input** is any data the application receives that is functionally
meaningful (not infrastructure). Categories:

- **User-supplied at the UI**:
  - Streamlit: widget values (`st.text_input`, `st.selectbox`,
    `st.file_uploader`, `st.number_input`, `st.date_input`, ...) — every
    widget with a `key` is a discrete input
  - Generic web: form fields, query parameters, route parameters
  - CLI: arguments, options, flags
- **File uploads**: explicit `st.file_uploader`, multipart form, file
  drop zones
- **External system pushes**: webhooks received, message queue consumers
- **Scheduled-trigger inputs**: cron-fed parameters, batch input feeds
- **Configuration as functional input**: feature flags, business
  parameters in config (NOT infra config like DB host — that is
  infrastructure)

Do NOT catalog as functional inputs:
- DB queries (those are internal data access — see `data-flow-analyst`'s
  output, not yours)
- HTTP outbound calls to external APIs (these are part of transformations,
  not user inputs)
- Logging configuration, language settings, color palettes

---

## 2. Outputs catalog — categories

An **output** is any data the application emits that is functionally
meaningful. Categories:

- **Rendered to UI**:
  - Streamlit: `st.write`, `st.dataframe`, `st.metric`, `st.chart`,
    `st.markdown`, `st.json`, `st.code`, `st.image`, `st.audio`,
    `st.video`, `st.map`
  - Web: rendered templates, JSON responses
  - CLI: stdout/stderr text, formatted tables, generated files
- **File downloads**: `st.download_button`, file generation endpoints,
  exported reports (CSV, Excel, PDF, image)
- **External system writes**: outbound webhooks, message queue produces,
  API calls TO third-party systems where the call body carries
  application data (not just lookups)
- **Notifications**: email, Slack, SMS, dashboards updated

Do NOT catalog as functional outputs:
- DB writes (infrastructure-level; in transformations they are an
  intermediate step but not the user-facing output)
- Internal logging
- Cache writes

---

## 3. Transformation matrix — what to capture

A **transformation** is a documented mapping from one or more inputs to
one or more outputs. For each transformation, capture:

- **Trigger**: what causes it to happen (button click, file upload,
  scheduled job, request received)
- **Inputs consumed**: list of IN-IDs
- **Outputs produced**: list of OUT-IDs
- **Business rules applied** (high-level): "validates email format",
  "converts currency to EUR", "aggregates by month" — reference
  `.indexing-kb/07-business-logic/business-rules.md` where possible
- **Side effects** (mention but do not detail): "writes to DB",
  "sends email" — these are noted because they affect the user's
  observation of output completion

Common patterns:
- 1 input → 1 output (simple form submit)
- N inputs → 1 output (report aggregating filters)
- 1 input → N outputs (file upload that updates UI metric AND triggers
  download AND writes audit log)

---

## 4. Streamlit-specific I/O rules

If stack mode is `streamlit`:
- Every widget is a discrete input (one IN-ID per widget per screen).
  Do NOT collapse multiple widgets into a single "form input" unless
  they are inside `st.form` and submitted atomically.
- `st.cache_data`-decorated functions: their **arguments** are inputs to
  the cached transformation; their **return value** is an output (often
  re-rendered downstream).
- `st.session_state` is **not an input or output by itself** — it is
  internal state. But session_state keys that are SET from widget inputs
  on one screen and READ as inputs to transformations on another screen
  represent a **cross-screen input flow**: capture this in the
  transformation matrix as a multi-step transformation.

---

## 5. Validation as input metadata

For each input, capture validation constraints **as metadata**, not as
separate items (they belong in the input row):
- type (text / number / date / file / enum)
- required / optional
- range / min / max
- enum values
- regex / format
- file size / type constraints

These come from:
- Streamlit widget params (`min_value`, `max_value`, `format`, `options`,
  `accept`, `type`)
- `.indexing-kb/07-business-logic/validation-rules.md`
- field constraints in module docs

If validation is **embedded in code logic** (not in widget params),
flag it for `implicit-logic-analyst` rather than capturing all the
detail here. Just note "see implicit-logic.md IL-NN".
