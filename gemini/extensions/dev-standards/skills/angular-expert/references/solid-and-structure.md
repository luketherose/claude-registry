# SOLID, file structure and naming in Angular

The five SOLID principles restated for Angular, plus the file, folder and naming
conventions pulled from the official style guide.

## Contents

- [SOLID adapted to Angular](#solid-adapted-to-angular)
- [File and folder structure](#file-and-folder-structure)
- [Naming conventions](#naming-conventions)
- [Consistency](#consistency)

## SOLID adapted to Angular

**Single Responsibility**
- One component = one responsibility (either UI or logic, not both)
- A service does not mix HTTP calls, business logic and UI transformations
- A smart component does not also handle detailed data rendering

**Open/Closed**
- Extend via `@Input`, composition and `ng-content`, avoiding invasive modifications
- Prefer configurable components over components specialised for each case

**Liskov Substitution**
- Specialised components respect the expected behaviour of the base component
- Do not alter the semantics of @Input/@Output in specialisations

**Interface Segregation**
- @Input/@Output minimal, explicit and typed
- Avoid enormous configuration objects as a single @Input
- Each @Input carries one concept, not a bundle of heterogeneous options

**Dependency Inversion**
- Always inject via DI, never `new MyService()`
- Components depend on abstractions (interfaces/tokens), not on concrete implementations

## File and folder structure
- File names: kebab-case, separator `-` (`user-profile.ts`, not `userProfile.ts`).
- Test files end with `.spec.ts`.
- Match file name to TypeScript identifier: class `UserProfile` lives in `user-profile.ts`.
- Component family: same base name across `.ts`, `.html`, `.scss`, `.spec.ts`.
- Avoid generic file names such as `helpers.ts`, `utils.ts`, `common.ts`. Name by purpose.
- Organise by feature, not by type. Avoid top-level `components/`, `services/`, `directives/` directories.
- One concept per file.

## Naming conventions
- Components: `feature-name.component.ts` exporting `FeatureNameComponent`.
- Services: `feature-name.service.ts` exporting `FeatureNameService`.
- Directives use camelCase attribute selectors with an app prefix: `[appTooltip]`.

## Consistency
- When existing project conventions differ from these rules, prioritise consistency within the file/feature being edited. Do not rewrite a whole module to match style: change only the file under edit.
