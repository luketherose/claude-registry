---
name: python-to-react-migration-expert
description: "This skill should be used when replacing a Python server-rendered UI (Django templates, Jinja2, Flask-Jinja2, Streamlit) with a React single-page application: mapping template constructs to components and hooks, server session state to client state management, form posts to controlled components and mutations, and view routing to a React router. Do not use it for backend migration (use python-to-java-migration-expert) or for an Angular target (use python-to-angular-migration-expert)."
---
# Python to React Migration Expert

Migrate Python server-side rendered applications to React at the specification level. Decompose Django template hierarchies into React component trees, move form validation from server side to client side, design a state management strategy proportional to the application's complexity, and migrate the UI incrementally rather than in a big-bang cutover. Produce specifications that Python developers new to React can follow successfully.

## Key Concept Mappings (Built-in Reference)

| Python/Django Concept | React Equivalent | Notes |
|---|---|---|
| Django template inheritance (`{% extends %}`) | Component composition | Layout components, Outlet (React Router) |
| Django template block (`{% block %}`) | Props + children | Slot pattern or direct children |
| Template loop (`{% for item in items %}`) | `.map()` in JSX | Always use `key` prop |
| Template conditional (`{% if condition %}`) | `condition && <Component />` | |
| Django form | React Hook Form + Zod | Client-side validation required |
| Django form field errors | Field-level error display | `formState.errors.fieldName` |
| CSRF token | Cookie-based or header-based | Axios interceptor or fetch wrapper |
| Django messages framework | Toast/notification state | Zustand store or Context |
| Django URL template tag (`{% url %}`) | React Router `<Link to>` | |
| Django `{% static %}` | Vite asset imports | `import assetUrl from './asset.png'` |
| Django session | JWT in localStorage / HttpOnly cookie | Security decision needed |
| Django paginator | TanStack Query pagination | `useInfiniteQuery` or offset pagination |
| Django `request.user` | Auth context / Zustand auth store | |
| Django `get_context_data()` | Component props + useQuery | |
| Jinja2 filters | Utility functions + format libs | `date-fns`, `numeral.js`, etc. |

---

## Constraints
- No class components, functional components only
- No `any` TypeScript types
- All server state via TanStack Query
- All forms via React Hook Form + Zod
- Accessibility: ARIA required on forms and navigation
```

---

## Quality Checklist

- [ ] All template sections have React component equivalents
- [ ] TypeScript interfaces defined for all API types (no `any`)
- [ ] TanStack Query hooks for all API calls
- [ ] Form components include Zod validation schema
- [ ] Routing migration covers all URL patterns
- [ ] Pitfall register covers ≥ 5 Django-to-React specific issues

---

## Detailed references

- **Full output specification, section by section**: see [references/output-specification.md](references/output-specification.md)
- **A worked example: input and expected output excerpt**: see [references/worked-example.md](references/worked-example.md)
