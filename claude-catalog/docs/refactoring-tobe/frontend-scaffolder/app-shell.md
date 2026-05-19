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

### Self-check before closing the agent run

After writing `app.component.html`, the agent MUST verify:

```bash
# Placeholder strings must NOT exist anywhere under src/app/
! grep -RnE "Hello, \{\{ title \}\}|Congratulations! Your app is running|Explore the Docs|Learn with Tutorials" src/app/
# app.component.html must reference the layout shell
grep -q "app-layout" src/app/app.component.html
# router-outlet must live inside the layout, not at the top of app.component.html
grep -q "router-outlet" src/app/app.component.html
```

If any of these checks fail the scaffold is incomplete — fix and re-emit.

## README.md

`<frontend-dir>/README.md`:

- build instructions: `npm install && npm run openapi:generate &&
  npm start`
- project layout overview
- BC → feature module mapping
- environment configuration (API base URL, auth issuer)
- links to `docs/refactoring/4.6-api/openapi.yaml` and ADRs
