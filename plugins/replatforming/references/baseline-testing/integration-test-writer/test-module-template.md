# Integration test module — Python skeleton

> Reference doc for `integration-test-writer`. Read at runtime when scaffolding
> a new `tests/baseline/test_integration_<system>.py` module.

## Goal

Provide the canonical pytest module skeleton for AS-IS baseline integration
tests covering one external system (database, file system, outbound API,
cache). Each system gets its own file and inherits determinism (seed, time,
network blocked) from `tests/baseline/conftest.py`.

## Skeleton

```python
"""
Baseline integration test — <system name>.

Covers:
- <system>: <one-line description>
- Boundaries: <list of access patterns / INT-NN / path patterns>

Sources:
- docs/analysis/02-technical/04-data-access/access-pattern-map.md
- docs/analysis/02-technical/05-integrations/integration-map.md (INT-NN)
- .indexing-kb/06-data-flow/<file>.md

Determinism: inherited from conftest.py (seed, time, network blocked).

Mocking strategy:
- DB: in-memory SQLite (engine=postgresql in production — see
  docstring of each test for engine-specific notes)
- HTTP: responses / respx
- File system: tmp_path

AS-IS contract: tests exercise AS-IS adapters as-is. Failures indicate
either a test issue or a latent bug — never modify AS-IS source.
"""

import pytest
import responses

# from <repo_pkg>.<adapter> import <client>


@pytest.fixture
def db_engine():
    """In-memory SQLite engine with the AS-IS schema applied."""
    ...


def test_db_read_orders_by_user(db_engine, realistic_orders):
    """Canonical read: orders by user_id returns expected rows."""
    ...


@responses.activate
def test_external_api_happy_path():
    """INT-03 — Stripe charge creation: 200 response is parsed and DB
    row is created.
    """
    responses.add(
        responses.POST,
        "https://api.stripe.com/v1/charges",
        json={"id": "ch_xxx", "status": "succeeded"},
    )
    # exercise AS-IS function
    # assert request.headers["Authorization"].startswith("Bearer ")
    # assert DB row created


@responses.activate
def test_external_api_timeout(monkeypatch):
    """INT-03 — Stripe charge creation: timeout is surfaced (per
    Phase 2 finding RISK-INT-NN — no timeout configured).
    """
    # If Phase 2 flagged "no timeout", this test DOCUMENTS the
    # absence by asserting current (potentially broken) behavior.
    pass
```

## Mocking libraries reference

- `responses` — for `requests`-based clients
- `respx` — for `httpx`-based clients
- ad-hoc `monkeypatch` for SDK-specific clients (`boto3` → moto;
  `google.cloud` → google-cloud-testutils; etc.)

## Bug-found policy

Same as `usecase-test-writer`: never modify AS-IS source. Document the bug in
`## Open questions`, write the test against the SPEC, mark with an
`AS-IS-BUG` comment, let the supervisor's failure policy handle the
disposition.
