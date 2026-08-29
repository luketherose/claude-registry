# Usecase test module — template & Streamlit patterns

> Reference doc for `usecase-test-writer`. Read at runtime when writing the
> per-UC pytest module (Method §4 and §6).

## Goal

Provide the canonical shape of `tests/baseline/test_uc_<NN>_<slug>.py` and the
Streamlit-specific interaction patterns the writer must follow.

## Module template

```python
"""
Baseline test for UC-NN — <human title>.

Covers:
- UC-NN: <human title>
- Screens involved: S-NN (<name>), S-NN (<name>)
- I/O: IN-NN, IN-NN -> OUT-NN, OUT-NN (transformations: TR-NN)

Sources:
- docs/analysis/01-functional/06-use-cases/UC-NN-<slug>.md
- docs/analysis/01-functional/07-user-flows.md
- docs/analysis/02-technical/<relevant>.md

Determinism (inherited from conftest.py): seed=42, time frozen,
network blocked. See conftest module docstring for opt-out markers.

AS-IS contract: this test exercises the AS-IS codebase as-is. If the
test fails, the AS-IS code may have a latent bug. Report via the
baseline-runner; never modify the AS-IS source.
"""

import pytest

# import the AS-IS modules under test (read-only)
# from <repo_pkg>.<module> import <function>


@pytest.mark.streamlit  # only if Streamlit-driven
def test_uc_NN_happy_path(app_test, minimal_orders):
    """Happy path of UC-NN: <one-line>.

    Steps:
    1. <interaction 1>
    2. <interaction 2>
    3. <assertion>
    """
    # Streamlit example:
    # app_test.text_input("query").set_value("foo").run()
    # assert app_test.dataframe[0].value.shape == (3, 4)
    # assert app_test.session_state["status"] == "ok"
    pass


def test_uc_NN_alternative_<flow>(realistic_orders):
    """Alternative flow: <one-line description>."""
    pass


def test_uc_NN_edge_<case>(edge_orders):
    """Edge: <one-line description>.

    Risk reference: RISK-NN (severity=<sev>) from Phase 2.
    """
    pass


# Use snapshot assertions for richer outputs:
def test_uc_NN_snapshot_dataframe(realistic_orders, dataframe_regression):
    result = ... # invoke AS-IS
    dataframe_regression.check(result)
```

## Streamlit-specific patterns (stack mode = `streamlit`)

```python
from streamlit.testing.v1 import AppTest

def test_uc_NN_via_apptest():
    at = AppTest.from_file("path/to/page.py").run()

    # Set widget values
    at.text_input(key="search").set_value("foo").run()

    # Click a button
    at.button(key="submit").click().run()

    # Assert output
    assert at.dataframe[0].value.shape[0] > 0
    assert "Success" in at.success[0].value
```

If `AppTest` cannot reach a particular interaction (custom component,
`file_uploader` with binary content, drag-drop), document the gap in
`## Open questions` and write a `pytest.skip` with the reason. Do NOT
silently leave the case untested.

## Output

A single self-contained pytest module at
`tests/baseline/test_uc_<NN>_<slug>.py` with at least 3 test functions
(happy + alternative + edge), or a documented justification per category
when not applicable.
