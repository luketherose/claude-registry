---
name: frontend-orchestrator
description: "ALWAYS use this skill when a frontend task spans multiple concerns: the user asks to design a feature mixing routing, state management, styling, and API calls; a new FE component or feature is built from scratch in any framework; an existing FE module is refactored or architecturally reviewed; the framework is undecided; or the request explicitly asks for cross-skill coordination. Trigger phrases: \"design a feature end-to-end\", \"review the architecture of this FE module\", \"plan the FE for X\", \"NgRx + RxJS + design system together\". Coordinates Angular, NgRx, RxJS, React, Vue, Qwik, CSS/SCSS, Design, FE Refactoring skills. Do not use for single-framework, single-concern tasks (use the targeted skill directly), for purely backend tasks (java-expert), for repository analysis (tech-analyst), or for migrations (migration-orchestrator)."
---

# Frontend Orchestrator

Coordinate the frontend skills, guaranteeing architectural, stylistic and functional consistency between design, implementation and state.

## Step 0: Identify the project framework

Before activating any FE skill, determine the project framework:

| Framework | Primary skill | Related skills |
|---|---|---|
| **Angular** | `angular-expert` | `ngrx-expert`, `rxjs-expert` |
| **React** | `react-expert` | `tanstack-query`, `tanstack`, `nextjs`, `tanstack-start` |
| **Vue 3** | `vue-expert` | n/a |
| **Qwik** | `qwik-expert` | n/a |
| **Vanilla JS/TS** | `vanilla-expert` | n/a |

**Styles and design** (cross-cutting across all frameworks):
| Skill | Scope |
|---|---|
| `design-expert` | Layout, mockups, design system, UI/UX |
| `css-expert` | SCSS, design tokens, layout, responsive, theming |
| `refactoring-expert` | FE refactoring with SOLID, DRY, separation of concerns scope |

## FE context sources

Before activating FE skills, consult the documentation and analysis artefacts available in the project:

1. **Migration / mapping artefacts**: if available, look for the mapping of the legacy component/page being migrated to Angular
2. **Functional analysis**: for the requirements of the component to implement
3. **Technical analysis**: to understand the bounded context and dependencies of the component
4. **Architectural artefacts**: to understand the end-to-end flow in which the FE component fits

### When to consult pre-existing artefacts (FE context)

**For new components from legacy migration:**
1. Look for the component mapping in the available analysis artefacts
2. Read the source logic and business rules of the legacy component
3. Identify the component's dependencies in the corresponding bounded context

**For existing FE refactoring:**
- Consult the architectural artefacts to understand what depends on the component being modified

**Do not consult** analysis artefacts for purely stylistic tasks or Angular micro-fixes.

## FE orchestration algorithm

### Step 1: Analyse the FE task

Guiding questions:
- **New component from scratch?**                  → Start with design, then Angular, then CSS
- **Complex state shared between features?**       → Evaluate whether NgRx is needed (see Step 2)
- **Problematic RxJS streams?**                    → Activate `rxjs-expert`
- **Styles to reorganise or create from scratch?** → Activate `css-expert`
- **Only refactoring of existing code?**           → Activate `refactoring-expert` with FE scope

### Step 2: Evaluate whether NgRx is necessary

**NgRx is appropriate when:**
- State shared between multiple components not hierarchically related
- Complex side effects (API calls, cache, WebSocket)
- Need for time-travel debugging or undo/redo
- Feature with many state transformations

**NgRx is overkill when:**
- State local to a single component or isolated feature
- Simple parent-child communication via @Input/@Output
- The problem is solved with a service + BehaviorSubject

**Rule**: reach for NgRx only when a service with BehaviorSubject is not sufficient.

### Step 3: Standard activation orders

**Scenario A: new component from scratch**
```
1. design-expert     → layout, mockup, design tokens
2. angular-expert    → component structure, smart/dumb, services
3. css-expert        → modular SCSS, responsive
4. ngrx-expert       → (only if there is state to manage)
5. rxjs-expert       → (only if there are complex streams)
```

**Scenario B: existing FE refactoring**
```
1. refactoring-expert     → identify code smells, SOLID violations
2. angular-expert         → apply structural corrections
3. rxjs-expert            → correct problematic RxJS patterns
4. css-expert             → correct styles (if necessary)
```

**Scenario C: feature with complex state**
```
1. design-expert     → UI and user flow
2. ngrx-expert       → store design, actions, effects
3. angular-expert    → connect components to the store via facade
4. rxjs-expert       → manage streams in effects
```

**Scenario D: migration of a legacy component → Angular**
```
Delegate to /orchestrators/migration-orchestrator
(already includes FE orchestration as part of the pipeline)
```

## Parallel execution

### Independence criterion
Two tasks are parallelizable when:
- They do not write to the same files
- Neither depends on the other's output
- They operate on distinct system layers or surfaces

### Phase model
Map every multi-skill task into phases before executing:
```
Phase 1 — Sequential anchor    (shared contracts, interfaces, schemas)
Phase 2 — Parallel fan-out     (independent implementation workers)
Phase 3 — Sequential merge     (integration, consistency checks, tests)
```

### Domain-specific parallelization rules

```
Parallelizable pairs:
  - design-expert (mockup/tokens) ∥ css-expert (global styles not tied to component)
  - component implementation ∥ unit tests for already-specified component interface

Always sequential:
  design-expert    → framework-expert (component needs finalized design tokens)
  framework-expert → ngrx-expert/tanstack-query (state needs component contract defined)
```

### When NOT to parallelize
- Tasks share mutable output files (same component, same table, same service)
- Task B's input is Task A's output
- Only 1-2 tasks total (coordination overhead exceeds benefit)

---

### Step 4: Mandatory FE invariants

These rules apply to every orchestrated output, regardless of the scenario:

```
[Design]    → Tokens always for colours/spacing/typography — never hardcoded values
[Design]    → Components from the project design system library before creating custom ones
[Design]    → Accessibility: focus ring on interactive controls, WCAG AA contrast

[Angular]   → ChangeDetectionStrategy.OnPush on all dumb components
[Angular]   → Zero any in TypeScript — explicit interfaces for every model
[Angular]   → Lazy loading on every feature module
[Angular]   → Typed @Input/@Output — no omnibus configuration objects
[Angular]   → Dumb components without dependencies on services or store

[RxJS]      → async pipe preferred over manual subscribes
[RxJS]      → Every manual subscribe has an explicit cleanup strategy
[RxJS]      → Do not modify external variables in map (use tap)

[SCSS]      → Styles in .component.scss — no inline CSS in the template
[SCSS]      → Flat BEM selectors — maximum 3 levels of nesting
[SCSS]      → @use instead of @import for tokens and mixins

[NgRx]      → Pure reducers — no side effects, no HTTP calls
[NgRx]      → If using facade, components do not access the store directly
[NgRx]      → Event-driven actions with source tag: [Page/API] Event Occurred
```

### Step 5: FE decision patterns

**State: when to choose what**
```
UI state (isOpen, isLoading, activeTab)   → Component local state
State shared within a feature             → Service + BehaviorSubject
Global state / complex side effects       → NgRx
Parent-child communication                → @Input/@Output
```

**API queries: which operator to use**
```
Live search / autocomplete                → switchMap (cancels the previous)
Form submit (prevents double click)       → exhaustMap
Dependent sequential operations           → concatMap
Independent parallel downloads            → mergeMap
```

**Component: smart or dumb?**
```
Knows services, router, store             → Smart (container)
Receives only @Input, emits only @Output  → Dumb (presentational, OnPush mandatory)
```

## Acceptance Criteria for completed FE orchestration

**Scenario A (new component) completed when:**
- [ ] Design spec produced with token names (not hex values)
- [ ] Component tree (smart/dumb) defined
- [ ] Lazy feature module configured
- [ ] Styles in modular `.component.scss`
- [ ] No `any` in TypeScript
- [ ] Observables managed with `async` pipe or explicit cleanup
- [ ] All dumb components with `OnPush`

**Scenario C (complex state) completed when:**
- [ ] Store design documented (state interface, actions, selectors)
- [ ] Effects for every API call
- [ ] Facade as the single access point to the store for components
- [ ] Unit tests for reducers and selectors

### React, Vue, Qwik scenarios

**Scenario R: new React component from scratch**
```
1. design-expert     → layout, mockup, design tokens
2. react-expert      → components, hooks, TypeScript
3. tanstack-query    → if data fetching is needed
4. tanstack          → if routing is needed
5. css-expert        → modular/Tailwind styles
```

**Scenario R-Full: full-stack React app**
```
1. nextjs            → if SSR/RSC (App Router)
   or tanstack-start → if TanStack-native
2. react-expert      → client components
3. tanstack-query    → client state/data fetching
```

**Scenario V: Vue 3 from scratch**
```
1. design-expert     → layout, mockup
2. vue-expert        → SFC, composables, Pinia, Vue Router
3. css-expert        → scoped styles
```

**Scenario Q: Qwik / Qwik City**
```
1. design-expert     → layout, mockup
2. qwik-expert       → components, loaders, actions, signals
3. css-expert        → styles
```

---

## Expected output

At the end of FE orchestration, produce:
- Summary of the skills activated and their contributions
- Complete code for the chosen framework
- Notes on the patterns adopted and architectural motivations
