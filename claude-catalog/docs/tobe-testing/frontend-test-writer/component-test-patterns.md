# Component & service test patterns — frontend-test-writer

> Reference doc for `frontend-test-writer`. Read at runtime when authoring
> component or service unit tests for the Angular 17+ TO-BE workspace.

## Goal

Define the canonical Angular Testing Library + Jest patterns the agent emits
for component, page, and service unit tests. These patterns are read once per
authoring pass; they do not affect dispatch or scheduling decisions.

## Component test patterns

Use Angular Testing Library (`@testing-library/angular`) over the classic
`TestBed.createComponent` pattern. ATL's user-event API
(`fireEvent.click`, `fireEvent.input`) reads more naturally and avoids
fragile DOM queries.

```typescript
import { render, screen, fireEvent } from '@testing-library/angular';
import { <Component> } from './<component>.component';
import { <Service> } from '../services/<service>.service';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';

describe('<Component>', () => {
  it('renders the empty state when no items are loaded', async () => {
    await render(<Component>, {
      providers: [<Service>, provideHttpClient(), provideHttpClientTesting()],
    });

    expect(screen.getByText('No items')).toBeInTheDocument();
  });

  it('disables submit button until form is valid', async () => {
    await render(<Component>, { /* ... */ });

    const submit = screen.getByRole('button', { name: /submit/i });
    expect(submit).toBeDisabled();

    const input = screen.getByLabelText(/name/i);
    fireEvent.input(input, { target: { value: 'Valid name' } });

    expect(submit).toBeEnabled();
  });

  it('shows RFC 7807 error from the API', async () => {
    const { fixture } = await render(<Component>, { /* ... */ });
    const httpMock = TestBed.inject(HttpTestingController);

    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    httpMock.expectOne('/v1/<resource>').flush(
      { type: '...', title: 'Validation failed', status: 400, detail: 'name required' },
      { status: 400, statusText: 'Bad Request', headers: { 'content-type': 'application/problem+json' } },
    );

    expect(await screen.findByText(/name required/i)).toBeInTheDocument();
  });
});
```

Cover for each component:
- Empty / loading / loaded / error states
- Form validation (each rule)
- User-action handlers (click / input / submit)
- Signal updates (if the component uses signals or RxJS state)
- Routing interactions (use `RouterTestingHarness` for route-driven tests)

## Service tests

For services that wrap HTTP, use `HttpTestingController` and assert:

- Request URL, method, body
- Response handling (success, RFC 7807 error, retries)
- Cache behaviour (if `shareReplay` is in use)
- Idempotency-Key header presence on POST writes

## Coverage policy

- Line coverage >= 80% on `frontend/src/app/`
- Function coverage >= 70%
- Excluded: `*.module.ts`, `*.config.ts`, generated OpenAPI client
  (`frontend/src/app/api/`)
- Configured via `jest.config.ts` `collectCoverageFrom` + `coverageThreshold`

If a feature module cannot reach the threshold because the components are
presentation-only (no logic), document this in
`frontend/src/app/<feature>/COVERAGE.md` with the exclusion rationale.
