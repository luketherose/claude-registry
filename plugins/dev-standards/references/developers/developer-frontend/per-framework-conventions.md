# Per-framework conventions — developer-frontend

> Reference doc for `developer-frontend`. Read at runtime once the project's
> framework has been detected (Step 1 of the agent body). Load only the section
> matching the detected stack — never mix.

---

## Angular stack

```
Always invoke:
  frontend/angular/angular-expert   — component architecture, smart/dumb, routing, forms, guards

Invoke when state management is needed:
  frontend/angular/ngrx-expert      — only if shared state across features, side effects,
                                      or undo/redo is required. Not for local state.

Invoke when RxJS streams are involved:
  frontend/angular/rxjs-expert      — flattening operators, subscription cleanup, stream design
```

**Angular — invariants (non-negotiable):**
- **Every component is delivered as 4 co-located files**: `<name>.component.ts`, `<name>.component.html`, `<name>.component.scss` (or `.css`), `<name>.component.spec.ts`. The `.ts` references the template and styles via `templateUrl` and `styleUrls` — **inline `template:` and `styles:`/`styleUrls: []` literals in the `@Component` decorator are forbidden**. Allowed exception: trivial render-prop wrappers (≤ 5 markup lines, single binding, no logic) may inline the template — when in doubt, externalise. Never collapse the file family because the component is small or "obvious".
- `ChangeDetectionStrategy.OnPush` on all presentational (dumb) components
- Lazy loading on every feature module
- Zero `any` in TypeScript — explicit interfaces for every model
- `async` pipe preferred over manual subscribe
- Every manual `subscribe()` has an explicit cleanup strategy
- Dumb components have no service or store dependencies
- NgRx only when a service + BehaviorSubject is insufficient

---

## React stack

```
Always invoke:
  frontend/react/react-expert       — hooks, component architecture, TypeScript, performance

Invoke when server data fetching is needed:
  frontend/react/tanstack-query     — useQuery, useMutation, cache invalidation, optimistic updates

Invoke when client-side routing is needed:
  frontend/react/tanstack           — TanStack Router, file-based routes, type-safe navigation,
                                      loaders, search params

Invoke when full-stack SSR is needed:
  frontend/react/nextjs             — App Router, RSC, Server Actions, metadata, caching
  OR
  frontend/react/tanstack-start     — TanStack Start, createServerFn, SSR, streaming
                                      (use nextjs if team is Next.js-experienced;
                                       use tanstack-start for TanStack-native stacks)
```

**React — invariants (non-negotiable):**
- All props typed with explicit TypeScript interfaces — never `any`
- `useEffect` only for synchronizing with external systems, never for derived state
- `useCallback` / `useMemo` only where genuinely needed (not by default)
- `key` in lists uses stable IDs, never array index for dynamic lists
- Server state managed by TanStack Query — never `useState` + `useEffect` for fetch
- Error boundaries wrap every major feature section

---

## Vue 3 stack

```
Always invoke:
  frontend/vue/vue-expert           — Composition API, script setup, Pinia, Vue Router 4,
                                      composables, reactivity rules
```

**Vue 3 — invariants (non-negotiable):**
- `<script setup lang="ts">` — Options API not used in new code
- Props typed with `defineProps<Interface>()` — never untyped
- `storeToRefs()` when destructuring Pinia stores
- `watch` with specific sources; `deep: true` only when necessary
- Emits typed with `defineEmits<Emits>()`

---

## Qwik stack

```
Always invoke:
  frontend/qwik/qwik-expert         — resumability, component$, signals, useSignal/useStore,
                                      routeLoader$, routeAction$, Qwik City routing
```

**Qwik — invariants (non-negotiable):**
- All interactive handlers use `$` suffix (lazy boundary)
- `useVisibleTask$` used sparingly — it breaks resumability
- Captured variables in `$` closures must be serializable
- Server functions (`routeLoader$`, `routeAction$`) for all data access

---

## Vanilla JS/TS stack

```
Always invoke:
  frontend/vanilla/vanilla-expert   — Web Components, TypeScript strict, DOM API,
                                      fetch wrapper, Custom Events, Intersection Observer
```

**Vanilla — invariants (non-negotiable):**
- TypeScript strict mode — no implicit `any`
- Web Components preferred for reusable, isolated UI elements
- `innerHTML` never used with unsanitized user input
- Every event listener removed on cleanup
