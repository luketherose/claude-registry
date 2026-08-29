---
name: angular-expert
description: "This skill should be used when the user works on Angular 17+ code: writing or reviewing components, applying the smart/dumb split, configuring OnPush, integrating RxJS observables in templates, building Reactive Forms, setting up lazy-loaded routes, or refactoring an Angular module. Trigger phrases: \"Angular component\", \"OnPush\", \"standalone component\", \"reactive form\", \"lazy module\", \"Angular FE refactoring\". Do not use for state-management tasks specifically (use ngrx-expert) or pure RxJS pipelines (use rxjs-expert)."
---

# Angular Expert

Analyse, improve and refactor Angular code by rigorously applying software quality principles and modern best practices. Produce Angular code that is **readable, maintainable, scalable and testable**.

## Reference technical stack

- Angular 18+ (standalone components + Signals are the default), TypeScript 5+
- RxJS, Angular Router, Reactive Forms, Angular Animations
- `inject()` function over constructor parameter injection
- Angular CLI, Karma + Jasmine (Vitest acceptable for new projects)
- Reverse proxy to the backend (e.g. `/api`)

> Canonical reference for ambiguous cases: https://angular.dev/style-guide

## Project structure (`frontend/src/app/`)

```
core/
  guards/         — AuthGuard, PermissionGuard (singleton, app-wide)
  interceptors/   — HTTP interceptors (auth token, error handling)
  models/         — shared TypeScript interfaces
  services/       — singleton services injected at root
features/
  [feature-name]/
    components/   — dumb components (presentational)
    containers/   — smart components (aware of store/services)
    services/     — services local to the feature
    models/       — local interfaces
    store/        — NgRx (only if necessary)
    [feature].module.ts
    [feature]-routing.module.ts
shared/
  components/     — reusable components without domain dependencies
  pipes/          — pure pipes
  directives/     — reusable directives
assets/           — fonts, images, icons
environments/     — environment.ts / environment.prod.ts
```

---

## Quick reference: the rules that get violated most

| Situation | Correct choice |
|---|---|
| Page-level component owned by a route | Smart container: injects services, orchestrates, renders dumb components |
| Reusable UI piece | Dumb component: `input()` / `output()` only, zero injected services, `OnPush` |
| Component needs backend data | Call a feature service or facade. Never inject `HttpClient` into a component |
| Component template exceeds 30 lines | Extract sub-components |
| Any non-trivial component | `templateUrl` + `styleUrls`, never inline `template:` / `styles:` |
| Feature module registration | `loadChildren` lazy route, always |
| Simple UI state (`isLoading`, `isOpen`) | Local component state |
| Shared state within one feature | Service + signal or `BehaviorSubject` |
| Complex global state with side effects | NgRx (see `ngrx-expert`) |
| Reading a stream in a template | `async` pipe, not a manual `subscribe` |
| A `subscribe` that is genuinely needed | `takeUntilDestroyed(inject(DestroyRef))` |
| Live search cancelling the previous call | `switchMap` |
| Form submit ignoring repeat clicks | `exhaustMap` |
| Iterating in a template | `@for` with a mandatory `track` |
| Typing a service method | Explicit types. `any` is never acceptable |
| Complex form | Reactive Forms. Template-driven forms are for trivial cases only |

---

## Mandatory principles

### 1. SOLID adapted to Angular

One component means one responsibility (UI or logic, never both). Extend via `@Input`, composition and `ng-content` rather than invasive modification. Keep `@Input`/`@Output` minimal, explicit and typed, one concept each. Always inject via DI, never `new MyService()`, and depend on abstractions rather than concrete implementations.

Full principle-by-principle breakdown: see [references/solid-and-structure.md](references/solid-and-structure.md).

### 2. Smart / Dumb component pattern (strict and non-negotiable)

This is the most frequently violated rule in our generated code. **Apply it without exception.**

**Smart (container) component**, the page-level component owned by a route:
- Aware of services, store, router, route params
- Orchestrates data flow: invokes services, subscribes to streams, dispatches actions
- Renders dumb components and binds data into them
- **Does not** contain markup-heavy templates (>30 lines of HTML is a smell)
- **Does not** contain raw business logic: that lives in services

**Dumb (presentational) component**, every reusable UI piece:
- Receives data via `input()` (signals) or `@Input`; emits via `output()` or `@Output`
- **Zero injected services**, **zero `HttpClient`**, **zero store access**
- Uses `ChangeDetectionStrategy.OnPush`
- Has no knowledge of how data was fetched or where events go

**Defect to avoid**: a "page component" that injects `HttpClient`, calls the API directly, transforms the payload inline, and renders the result. This is three responsibilities collapsed into one. Split it.

Worked smart/dumb pair, the service-ownership example and the external-template mandate with its rationale: see [references/component-patterns.md](references/component-patterns.md).

### 2.b Service ownership of HTTP and business logic (strict)

Components never call `HttpClient` directly. A feature service or facade is the single entrypoint to the backend; components consume signals/observables exposed by that service. Business logic (calculations, validations, state derivations) lives in services or pure functions, never in templates and never in component methods that double as orchestrators.

### 3. Mandatory lazy loading

Every feature module is loaded lazily:

```typescript
{
  path: 'items',
  loadChildren: () => import('./features/items/items.module').then(m => m.ItemsModule)
}
```

The Core Module is imported only by AppModule. The Shared Module is imported by feature modules.

### 4. State management: complexity hierarchy

1. **Local component state**: for simple UI state (e.g. `isLoading`, `isOpen`)
2. **Service + BehaviorSubject**: for shared state within a feature
3. **NgRx**: for complex global state, side effects, time-travel debugging

Use the simplest level that solves the problem. Do not reach for NgRx if a service is sufficient.

### 5. RxJS, change detection, forms and typing

Prefer the `async` pipe over a manual `subscribe`. Where a `subscribe` is unavoidable, tie it to `takeUntilDestroyed(inject(DestroyRef))`. Pick the flattening operator by intent: `switchMap` for live search, `concatMap` for order-dependent sequences, `mergeMap` for independent parallel work, `exhaustMap` for form submit. Put `ChangeDetectionStrategy.OnPush` on every dumb component, always supply `track` in `@for`, and prefer pure pipes over template method calls. Build complex forms with Reactive Forms and pure validator functions. Type everything: `any` is never acceptable in a signature.

Operator table, unsubscribe pattern, error handling, trackBy, form group and validator samples, and the zero-`any` examples: see [references/rxjs-forms-and-performance.md](references/rxjs-forms-and-performance.md).

### 6. Structure and readability

- Small, focused components (indicatively < 150 lines)
- Complex logic extracted into services or pure functions
- Clean templates: move logic out of the template, extract sub-components if the template grows
- Clear and consistent names (technical English for code, domain language for application concepts)
- Avoid excessive nesting in the template

### 7. Testability

- Inject dependencies via DI → facilitates mocking
- Keep logic out of the template → testable in isolation
- Test services separately from components
- Use `ComponentFixture` for components

---

## Modern Angular conventions (Angular 18+)

Pulled from the official style guide at https://angular.dev/style-guide. These are the rules most often missed in generated code.

### Dependency injection
- Use `inject()` function over constructor parameter injection. Better readability and type inference.
- Mark `inject()`-assigned fields `private readonly`.

### Components and directives: structure
- Group Angular-specific properties first, at the top of the class: injected dependencies, inputs, outputs, queries.
- Define Angular-specific properties before methods.
- Implement lifecycle hook interfaces (`OnInit`, `OnDestroy`) when using lifecycle methods.
- Keep lifecycle hooks short: extract logic into separate methods.

### Inputs/outputs (signals-first)
- Prefer the signal-based `input()` / `input.required()` / `output()` over `@Input` / `@Output` decorators in new code.
- Mark inputs/outputs `readonly` (this prevents accidental overwrite of Angular-managed properties).
- Apply `readonly` broadly to all properties initialised by Angular: `input`, `model`, `output`, `viewChild`, `contentChild`, etc.
- Use `protected` (not `public`) for component members accessed only from the template.

### Templates
- **External template files are the default**: every component declares `templateUrl: './name.component.html'`, never an inline `template:` literal. Inline templates allowed only for trivial components (≤ 5 lines of markup, no bindings beyond a single `{{ value }}`) and never for any component containing more than one element.
- Avoid complex template logic: refactor into `computed()` signals or component methods.
- Prefer direct `[class]` and `[style]` bindings over `NgClass` / `NgStyle`.
- Use the new control-flow blocks (`@if`, `@for`, `@switch`) over `*ngIf`, `*ngFor`, `*ngSwitch` in new code.
- For `@for`, always provide `track` (mandatory in modern Angular).
- Event handler names describe the action, not the trigger: `onSaveProfile()` not `onClick()`.

### File names and consistency
- File names kebab-case, matching the TypeScript identifier: class `UserProfile` lives in `user-profile.ts`.
- Organise by feature, not by type. One concept per file.
- Where existing project conventions differ from these rules, prioritise consistency within the file or feature being edited.

Full file, folder and naming conventions: see [references/solid-and-structure.md](references/solid-and-structure.md).

---

## Process given input code

1. Critically analyse the code
2. Identify code smells, violations of the principles above, anti-patterns
3. Refactor applying the principles
4. Extract if useful: services, dumb components, pure pipes, helper functions
5. Do not change functional behaviour (except for obvious bugs)

## Required output

- Complete refactored Angular code (`.ts` + `.html` + `.scss`)
- Brief explanation of the main changes (optional but recommended)

## Constraints

- Do not change functional behaviour (except for obvious bugs)
- Do not introduce complexity not required by the task (YAGNI)
- Do not add libraries that are not strictly necessary
- Maintain consistency with the existing project style

## Fundamental guideline

> Clarity > cleverness. Simplicity > premature abstraction. Composition > complexity.

---

## TODOs are not optional: be aggressive, not conservative

Never leave an Angular component empty (`// TBD`, `throw new Error('Not implemented')`, an empty template) because the source-to-Angular translation is uncertain. Implement the most reasonable best-guess version, fully wired up, and mark the assumption with a specific `// TODO: [assumption made] - verify [what the human should check]` comment at the point where it was made.

Rationale and the best-guess versus conservative-stub examples: see [references/todo-policy.md](references/todo-policy.md).

## Detailed references

- **Smart/dumb worked examples, service ownership of HTTP, external templates**: see [references/component-patterns.md](references/component-patterns.md)
- **SOLID principle by principle, file and folder structure, naming conventions**: see [references/solid-and-structure.md](references/solid-and-structure.md)
- **RxJS operators, subscription lifetime, change detection, Reactive Forms, typing**: see [references/rxjs-forms-and-performance.md](references/rxjs-forms-and-performance.md)
- **The TODO policy with best-guess and forbidden-stub examples**: see [references/todo-policy.md](references/todo-policy.md)
