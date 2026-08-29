---
name: python-to-angular-migration-expert
description: "This skill should be used when replacing a Python server-rendered UI (Django templates, Jinja2, Flask, Streamlit) with an Angular single-page application: mapping template constructs to components, session state to Angular services and RxJS streams, server-side form handling to Reactive Forms, and view routing to the Angular Router. Do not use it for backend migration (use python-to-java-migration-expert) or for a React target (use python-to-react-migration-expert)."
---
# Python to Angular Migration Expert

Migrate enterprise Python applications to Angular at the specification level. Work from Angular's opinionated structure: modules, dependency injection, RxJS reactive patterns, Angular forms and HttpClient. Produce migration specifications that result in idiomatic, maintainable Angular code, not a port of Python template logic into Angular components.

## Key Concept Mappings (Built-in Reference)

| Python/Django Concept | Angular Equivalent | Notes |
|---|---|---|
| Django template inheritance | Component composition + `<router-outlet>` | AppComponent as layout shell |
| Template blocks | Component `@Input()` + `<ng-content>` | Content projection |
| Template loops (`{% for %}`) | `*ngFor` / `@for` (Angular 17+) | |
| Template conditionals (`{% if %}`) | `*ngIf` / `@if` (Angular 17+) | |
| Django form | Angular Reactive Form (FormGroup) | NEVER use template-driven |
| Django form field error | `form.get('field')?.errors` | Display with `*ngIf` |
| Django session | JWT service / Auth service | HttpOnly cookie preferred |
| Django URL patterns | Angular Router `Routes[]` | Route guards for auth |
| Django `{% url %}` tag | `routerLink` directive | |
| CSRF | HTTP interceptor with XSRF header | `HttpClientXsrfModule` |
| Django messages | Angular MatSnackBar / Toastr | Toast service |
| Django request.user | AuthService + user signal/BehaviorSubject | |
| Django paginator | Angular CDK Virtual Scroll / manual | `HttpParams` for query |
| Celery async task result | WebSocket / polling Observable | RxJS interval + takeUntil |

---

## Constraints
- Standalone components (not NgModules) unless specified
- Reactive forms only
- async pipe in templates, no manual subscriptions
- OnPush change detection
- No any TypeScript types
```

---

## Quality Checklist

- [ ] All templates mapped to Angular components
- [ ] Services encapsulate all HTTP, no HTTP in components
- [ ] Reactive forms with validators (not template-driven)
- [ ] RxJS patterns are idiomatic (no nested subscribes)
- [ ] Routing covers all Python URL patterns

---

## Detailed references

- **Full output specification, section by section**: see [references/output-specification.md](references/output-specification.md)
- **A worked example: input and expected output excerpt**: see [references/worked-example.md](references/worked-example.md)
