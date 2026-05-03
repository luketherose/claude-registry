# E2E Playwright patterns — frontend-test-writer

> Reference doc for `frontend-test-writer`. Read at runtime when authoring
> Playwright E2E specs derived from Phase 1 user flows.

## Goal

Define the canonical Playwright Page Object Model + spec layout, config knobs,
and Streamlit-aware caveats. One E2E spec per user flow from
`docs/analysis/01-functional/user-flows.md`.

## Spec layout

Use Page Object Model under `e2e/pages/` to keep specs readable.

```typescript
// e2e/flows/<flow-name>.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/login.page';
import { <Feature>Page } from '../pages/<feature>.page';

test.describe('<Flow name from user-flows.md>', () => {
  test('happy path completes end-to-end', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.signIn('test-user', process.env.TEST_PASSWORD!);

    const feature = new <Feature>Page(page);
    await feature.goto();
    await feature.fillForm({ name: 'Test' });
    await feature.submit();

    await expect(feature.successBanner).toBeVisible();
    await expect(feature.itemList).toContainText('Test');
  });

  test('alternative flow: <description>', async ({ page }) => {
    // ... per alternative flow listed in user-flows.md
  });

  test('error: <description>', async ({ page }) => {
    // ... per documented error scenario
  });
});
```

## Playwright config

- `baseURL` from env: `TOBE_FRONTEND_URL` (default `http://localhost:4200`)
- Backend URL: `TOBE_API_BASE_URL` (default `http://localhost:8080`)
- Three browsers: chromium (always), firefox + webkit (CI-only via projects)
- Trace `on-first-retry`, screenshot `only-on-failure`, video
  `retain-on-failure`
- Single worker by default; CI uses `process.env.CI ? 1 : undefined`

Use Playwright fixtures to seed/clean DB between tests: invoke the backend's
test-only `/internal/test/reset` endpoint (added by Phase 4
`hardening-architect` only when `spring.profiles.active=test`).

## Streamlit-aware considerations

For each UC whose AS-IS implementation was a Streamlit page:

- The TO-BE Angular component will look different (no `st.session_state`
  reactivity model, no `st.rerun()`).
- The E2E test asserts the **outcome** of the user flow (data persisted,
  error shown, navigation completed), not the intermediate UI shape.
- If a UC depended on Streamlit-specific reactive behaviour (e.g., changing
  one selectbox auto-refreshes a downstream chart), verify the TO-BE has a
  deliberate equivalent (e.g., explicit Angular signal cascading) and test
  that explicitly.

The Phase 4 frontend-scaffolder produced a Streamlit -> Angular translation
table — read it to understand which constructs were mapped where.

## AS-IS bug carry-over filter

Same approach as `backend-test-writer`: for every BUG-NN in
`as_is_bug_carry_over`, identify which UC's E2E test would assert the buggy
behaviour, and add an explicit comment + assertion using the AS-IS-buggy
expected outcome. Document why.
