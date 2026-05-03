# Frontend hardening — config templates

> Reference doc for `hardening-architect`. Read at runtime when applying
> Method steps 6–7 (frontend CSP + correlation-id propagation).

## Goal

Verbatim configuration blocks the agent emits when hardening the frontend
scaffold.

---

## 6. CSP via index.html meta tag

`<frontend-dir>/src/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>App</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
  <!-- ADR-005: Content Security Policy.
       Adjust per environment via deployment-time replacement if
       inline scripts / styles are required by Angular's dev server. -->
  <meta http-equiv="Content-Security-Policy"
        content="default-src 'self';
                 script-src 'self';
                 style-src 'self' 'unsafe-inline';
                 connect-src 'self' http://localhost:8080 https://api.example.com;
                 img-src 'self' data:;
                 frame-ancestors 'none';
                 base-uri 'self';
                 form-action 'self';">
  <meta http-equiv="X-Content-Type-Options" content="nosniff">
</head>
<body>
  <app-root></app-root>
</body>
</html>
```

Note: the `connect-src` allowlist must include the API origin. Tune per
environment.

Update `<frontend-dir>/src/app/core/interceptors/auth.interceptor.ts`
header comment to reference ADR-005 token-storage decision (default:
sessionStorage for short access tokens; refresh flow per ADR-003).

---

## 7. Correlation-id propagation

Verify `<frontend-dir>/src/app/core/interceptors/correlation-id.interceptor.ts`
generates a new UUID per request (or propagates an inherited one if
nested calls); document in the file's header comment.
