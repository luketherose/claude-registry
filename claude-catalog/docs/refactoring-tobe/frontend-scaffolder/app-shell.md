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

## README.md

`<frontend-dir>/README.md`:

- build instructions: `npm install && npm run openapi:generate &&
  npm start`
- project layout overview
- BC → feature module mapping
- environment configuration (API base URL, auth issuer)
- links to `docs/refactoring/4.6-api/openapi.yaml` and ADRs
