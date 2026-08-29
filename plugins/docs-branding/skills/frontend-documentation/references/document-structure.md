# Frontend document structure

The default chapter and section layout for `frontend-doc.tex`, used whenever
the provided Word template does not impose one.

```
1.  Title page
2.  Revision history
3.  Table of contents
4.  Introduction
    4.1 Purpose of the document
    4.2 Technology stack (Angular — project version, TypeScript, NgRx)
    4.3 Prerequisites

5.  Application Architecture
    5.1 Feature modules and lazy loading structure
    5.2 Smart/dumb component pattern
    5.3 Dependency injection and shared services
    5.4 Main module tree

6.  Feature Modules
    For each documented feature module:
    6.N [FeatureName]Module
        6.N.1 Component tree (smart/dumb)
        6.N.2 Components — table with type, @Input/@Output, responsibilities
        6.N.3 Feature-specific services
        6.N.4 Feature routing
        6.N.5 NgRx store (if present in the bounded context)

7.  State Management (NgRx)
    7.1 Global state interface
    7.2 Actions (per feature)
    7.3 Reducers
    7.4 Effects (side effects and API calls)
    7.5 Selectors
    7.6 Facade pattern

8.  Routing and Navigation
    8.1 Main route structure (table: path → module → guard)
    8.2 Lazy loading strategy
    8.3 Route guards (AuthGuard, PermissionGuard)
    8.4 Route resolvers

9.  API Service Layer
    9.1 API services per project bounded context
    9.2 HTTP interceptors (auth token, error handling)
    9.3 TypeScript DTOs (API contract interfaces)
    9.4 HTTP error handling

10. Forms and Validation
    10.1 Reactive forms pattern
    10.2 Custom validators
    10.3 Form submission flow

11. Design System
    11.1 Project SCSS design tokens (colours, typography, spacing)
    11.2 Components from the project UI library
    11.3 SCSS patterns (BEM, @use, variables)
    11.4 Responsive breakpoints

12. Performance
    12.1 Change detection strategy (OnPush)
    12.2 trackBy for ngFor
    12.3 Async pipe vs manual subscribe
    12.4 Lazy loading and code splitting
    12.5 Bundle size targets

13. Appendix
    13.1 FE glossary
    13.2 Legacy component → Angular mapping table (if applicable)
    13.3 References
```

---
