# App shell

> Reference doc for `frontend-scaffolder`. Read at runtime when generating
> the Angular bootstrap files (Method step 8 — main.ts + app.config.ts,
> and Method step 9 — README.md).

## main.ts

```typescript
// main.ts
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';

bootstrapApplication(AppComponent, appConfig).catch(err => console.error(err));
```

## app.config.ts

```typescript
// app.config.ts
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { authInterceptor, errorInterceptor, correlationIdInterceptor } from './core/interceptors';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(withInterceptors([
      authInterceptor,
      correlationIdInterceptor,
      errorInterceptor,
    ])),
  ],
};
```

## app.component.ts

```typescript
// app.component.ts
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { LayoutComponent } from './core/layout/layout.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, LayoutComponent],
  templateUrl: './app.component.html',
})
export class AppComponent {}
```

## app.component.html

> **HARD RULE.** The `ng new` scaffold emits a 300+ line "Hello / Congratulations" placeholder. **You MUST overwrite this file completely.** No `<h1>Hello, {{ title }}</h1>`, no `Congratulations! Your app is running 🎉`, no "Explore the Docs" / "Learn with Tutorials" cards may survive in the emitted file.
>
> The emitted `app.component.html` is exactly the shell delegation below — three lines. The actual layout (header, sidenav, content area) lives in `core/layout/layout.component.html` (see `code-skeletons.md > Core layer > Layout`).

```html
<app-layout>
  <router-outlet />
</app-layout>
```

The `<app-layout>` component is responsible for:

- showing the sidenav + header only when the user is authenticated (it hides itself on `/login`, `/forgot-password`, etc.);
- emitting one nav entry per bounded context, gated on permissions from `AuthService`;
- providing the main content area that the `<router-outlet />` projects into.

### Self-check (HARD GATE) — run before reporting `status: ok`

A scaffold that compiles is NOT necessarily a scaffold a user can use.
The two most common failure modes are: (a) leaving the `ng new`
placeholder template intact, (b) forgetting to emit any navigation.
The app then builds green but is unusable. All 6 checks must pass:

```bash
# 1. No CLI placeholder strings survive
! grep -RlnE "Hello, \{\{ title \}\}|Congratulations! Your app is running|Explore the Docs|Learn with Tutorials" src/app/

# 2. app.component.html delegates to layout + has router-outlet
grep -q "app-layout" src/app/app.component.html
grep -q "router-outlet" src/app/app.component.html

# 3. Layout component exists with routerLinks
test -f src/app/core/layout/layout.component.ts
test -f src/app/core/layout/layout.component.html
grep -q "routerLink" src/app/core/layout/layout.component.html

# 4. Every protected route in app.routes.ts is referenced by the layout.
#    Build a list of `path: '...'` literals (excluding `**`, `login`, pure
#    redirects) and grep each in layout.component.html. Any unreferenced
#    path becomes a TODO marker in layout.component.ts with a (BC-NN) tag.

# 5. Interceptors exist (app.config.ts must not reference files the agent
#    forgot to write).
test "$(ls src/app/core/interceptors/*.interceptor.ts | wc -l)" -ge 1
grep -q "withInterceptors" src/app/app.config.ts

# 6. No per-service Authorization header — use the interceptor.
! grep -rln 'Authorization.*Bearer' src/app --include='*.service.ts'
```

Report each check + outcome in the agent's `## Self-check` response
section. Do NOT claim `status: ok` if any check failed.

## README.md

`<frontend-dir>/README.md`:

- build instructions: `npm install && npm run openapi:generate &&
  npm start`
- project layout overview
- BC → feature module mapping
- environment configuration (API base URL, auth issuer)
- links to `docs/refactoring/4.6-api/openapi.yaml` and ADRs
