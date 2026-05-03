# Code skeletons

> Reference doc for `frontend-scaffolder`. Read at runtime when generating
> TypeScript/HTML sources (Method steps 3–5 — core layer, shared layer,
> feature modules).

## Core layer

`src/app/core/`:

```
core/
├── interceptors/
│   ├── auth.interceptor.ts                  (Bearer token from auth service)
│   ├── error.interceptor.ts                 (RFC 7807 → app-level error event)
│   └── correlation-id.interceptor.ts        (generates / propagates X-Request-Id)
├── guards/
│   ├── auth.guard.ts                        (CanActivate — checks token)
│   └── role.guard.ts                        (CanActivate — checks role claim)
├── services/
│   ├── auth.service.ts                      (login, logout, token storage)
│   ├── notification.service.ts              (toast / banner)
│   └── error-handler.service.ts             (global ErrorHandler)
└── core.module.ts                           (provider bundle if not standalone-only)
```

Each interceptor and service has a header comment with:

- the ADR it implements (e.g., `auth.interceptor` → ADR-003)
- the cross-cutting concern (security / observability / UX)
- TODOs for environment-specific values (token storage strategy)

### auth.interceptor.ts (sketch)

```typescript
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';

/**
 * Attaches Bearer JWT to outgoing requests.
 *
 * ADR-003: stateless JWT in Authorization header.
 * Token storage: per ADR-003 — sessionStorage by default.
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.getAccessToken();
  if (!token) {
    return next(req);
  }
  const cloned = req.clone({
    headers: req.headers.set('Authorization', `Bearer ${token}`),
  });
  return next(cloned);
};
```

### error.interceptor.ts (sketch)

```typescript
/**
 * Translates RFC 7807 ProblemDetail errors into structured app errors.
 *
 * ADR-002: backend uses RFC 7807 for errors. The interceptor parses
 * the response body, extracts type / title / status / detail /
 * correlationId, and emits via NotificationService for UX, or rethrows
 * a typed error for component-level handling.
 */
```

## Shared layer

`src/app/shared/`:

```
shared/
├── components/
│   ├── loader/
│   ├── error-display/
│   ├── data-table/
│   └── form-error/
├── pipes/
│   ├── safe-html.pipe.ts
│   └── currency-format.pipe.ts
├── directives/
└── models/                                  (hand-written if Strategy B)
```

Components are small reusable building blocks. Each has its own
`*.component.ts`, `*.component.html`, `*.component.scss`,
`*.component.spec.ts` (test scaffold for Phase 5).

## Feature modules (one per BC)

`src/app/features/`:

```
features/
├── identity/                                (BC-01)
│   ├── identity.routes.ts                   (lazy routes)
│   ├── pages/
│   │   ├── login/
│   │   ├── user-list/
│   │   └── user-detail/
│   └── services/
│       └── identity.service.ts              (calls UsersApi from generated client)
├── payments/                                (BC-02)
└── reporting/                               (BC-03)
```

Each feature module:

- `<feature>.routes.ts` exports a `Routes` array — lazy entry
- `pages/` contains screens identified by Phase 1 (one component per
  screen S-NN); the screen → BC mapping is per the decomposition
- `services/<feature>.service.ts` is the orchestration layer; it
  consumes the OpenAPI-generated `*Api` services and exposes signal-
  or RxJS-based state to components

### Screens to components

For each screen S-NN in Phase 1 that maps to this BC:

- one standalone Angular component
- naming: `<screen-slug>.component.ts`
- header comment: S-NN ref, UC-NN(s) it serves, AS-IS Streamlit source
  ref (if applicable: which `pages/<page>.py` it replaces)

In `scaffold-todo` mode (default):

```typescript
import { Component, inject, signal } from '@angular/core';
import { IdentityService } from '../../services/identity.service';

/**
 * S-04 — User list screen.
 *
 * UCs surfaced: UC-04 (list users), UC-07 (suspend user)
 * AS-IS Streamlit ref: <repo>/infosync/streamlit/pages/users.py
 *
 * Translation status: scaffold-todo. List/detail rendering present;
 * filtering and pagination wiring marked TODO.
 */
@Component({
  selector: 'app-user-list',
  standalone: true,
  templateUrl: './user-list.component.html',
})
export class UserListComponent {
  private readonly service = inject(IdentityService);
  readonly users = this.service.users;     // signal-based
  readonly loading = this.service.loading;

  ngOnInit(): void {
    // TODO(BC-01, UC-04): wire pagination cursor handling
    //   (AS-IS: st.session_state['cursor']; TO-BE: signal in service)
    this.service.loadUsers();
  }

  onSuspend(userId: string): void {
    // TODO(BC-01, UC-07): confirmation dialog before suspending
    //   AS-IS source ref: <repo>/infosync/streamlit/pages/users.py:84
    this.service.suspendUser(userId);
  }
}
```

The `.html` template renders the happy path (table, suspend button,
loader, error banner) using the shared components. TODOs flag complex
interactions.

### user-flows → routing

From Phase 1 `07-user-flows.md`, derive:

- top-level routing (which screen is the entry per UC)
- guards (which routes require auth — most do; some are public per
  ADR-003)
- redirects (e.g., post-login → dashboard)
