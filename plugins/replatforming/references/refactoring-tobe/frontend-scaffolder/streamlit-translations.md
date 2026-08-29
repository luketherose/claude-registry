# Streamlit-to-Angular translations

> Reference doc for `frontend-scaffolder`. Read at runtime when the AS-IS
> codebase is Streamlit-based and Method step 7 (Streamlit-specific
> translations) applies.

Phase 1 likely identified Streamlit-only patterns. In TO-BE Angular:

| AS-IS Streamlit | TO-BE Angular |
|---|---|
| `st.session_state['x']` | service-level signal (or NgRx store slice) |
| `st.cache_data` | RxJS `shareReplay(1)` or in-memory cache service |
| `st.rerun()` | reactive change-detection (signals trigger automatically) |
| `st.file_uploader` | `<input type="file">` + multipart POST to API |
| `st.dataframe` | shared `DataTableComponent` |
| `st.chart` / Plotly | Chart.js / D3 / ngx-charts (per ADR-002 if specified) |
| widget callbacks | template events (`(click)`, `(change)`) |
| top-level script execution | component lifecycle (`ngOnInit`) |

These mappings are the canonical translation reference. Each component
that replaces a Streamlit page documents the AS-IS source ref.
