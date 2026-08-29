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
├── layout/
│   ├── layout.component.ts                  (app shell: header + sidenav + outlet)
│   ├── layout.component.html
│   └── layout.component.scss
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

### Layout (sidenav shell)

The `<app-layout>` standalone component is **mandatory**. It is the only place where the navigation between bounded contexts lives. Without it the app is unusable for an end user (every route is reachable only by typing the URL).

```typescript
// core/layout/layout.component.ts
import { Component, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../services/auth.service';

interface NavEntry {
  readonly label: string;
  readonly path: string;
  readonly permission?: string;       // undefined = always visible to authenticated users
  readonly bcLabel: string;           // bounded context group
}

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.scss'],
})
export class LayoutComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  // Derived from Phase 1 user flows + Phase 4 bounded-context decomposition.
  // One entry per concrete route the user can reach. Group by `bcLabel` in HTML.
  readonly nav: readonly NavEntry[] = [
    // ... one entry per BC, e.g.:
    // { bcLabel: 'M&A',    label: 'Pipeline',     path: '/ma/pipeline',  permission: 'ma' },
    // { bcLabel: 'Admin',  label: 'Users',        path: '/admin',        permission: '__admin__' },
  ];

  readonly visible = computed(() =>
    this.nav.filter(e => !e.permission || this.auth.hasPermission(e.permission))
  );

  readonly shouldShowShell = computed(() => this.auth.isLoggedIn());

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
```

`layout.component.html` (essentials):

```html
<ng-container *ngIf="shouldShowShell(); else loginOnly">
  <header class="app-header">
    <span class="app-title">{{ appName }}</span>
    <button type="button" (click)="logout()">Sign out</button>
  </header>
  <div class="app-body">
    <nav class="app-sidenav" aria-label="Primary">
      <ng-container *ngFor="let group of grouped()">
        <h3>{{ group.bcLabel }}</h3>
        <a *ngFor="let entry of group.entries"
           [routerLink]="entry.path"
           routerLinkActive="active">{{ entry.label }}</a>
      </ng-container>
    </nav>
    <main class="app-content"><ng-content /></main>
  </div>
</ng-container>
<ng-template #loginOnly>
  <main class="app-content app-content--full"><ng-content /></main>
</ng-template>
```

Self-check the agent MUST run after writing the layout:

```bash
# At least one routerLink must exist in the layout
grep -q "routerLink" src/app/core/layout/layout.component.html
# Every protected route in app.routes.ts must be referenced by the layout
# (the agent diff-checks this — anything missing becomes a TODO comment).
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
