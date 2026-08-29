# Angular component patterns

Worked examples for the smart/dumb split, service ownership of HTTP and business
logic, and the mandatory external-template rule. The SKILL.md body states the
rules; this file carries the full code and the rationale.

## Contents

- [Smart / Dumb component pattern (strict and non-negotiable)](#smart--dumb-component-pattern-strict-and-non-negotiable)
- [Service ownership of HTTP and business logic (strict)](#service-ownership-of-http-and-business-logic-strict)
- [External templates and styles (mandatory)](#external-templates-and-styles-mandatory)

## Smart / Dumb component pattern (strict and non-negotiable)

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

**File layout per component** (mandatory): every component is a triplet of co-located files, namely `name.component.ts`, `name.component.html`, and `name.component.scss` (or `.css`). The `.ts` references them via `templateUrl` and `styleUrls`. See "External templates and styles" rule below for rationale.

```typescript
// ✅ Dumb component — externalised template + styles
// item-card.component.ts
@Component({
  selector: 'app-item-card',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './item-card.component.html',
  styleUrls: ['./item-card.component.scss']
})
export class ItemCardComponent {
  readonly item = input.required<Item>();
  readonly selected = output<Item>();
}
```

```html
<!-- item-card.component.html -->
<article class="card">
  <h3>{{ item().name }}</h3>
  <button (click)="selected.emit(item())">Select</button>
</article>
```

```typescript
// ✅ Smart component — orchestrates only, externalised template + styles
// item-list-page.component.ts
@Component({
  selector: 'app-item-list-page',
  standalone: true,
  imports: [ItemCardComponent, AsyncPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './item-list-page.component.html',
  styleUrls: ['./item-list-page.component.scss']
})
export class ItemListPageComponent {
  private readonly itemFacade = inject(ItemFacade);
  protected readonly items = this.itemFacade.items;   // signal
  protected onSelect(item: Item) { this.itemFacade.selectItem(item.id); }
}
```

```html
<!-- item-list-page.component.html -->
@for (item of items(); track item.id) {
  <app-item-card [item]="item" (selected)="onSelect($event)" />
}
```

## Service ownership of HTTP and business logic (strict)

Components never call `HttpClient` directly. A feature service or facade is the single entrypoint to the backend; components consume signals/observables exposed by that service. Business logic (calculations, validations, state derivations) lives in services or pure functions, never in templates and never in component methods that double as orchestrators.

```typescript
// ✅ Feature service owns HTTP + cache
@Injectable({ providedIn: 'root' })
export class ItemService {
  private readonly http = inject(HttpClient);
  private readonly _items = signal<Item[]>([]);
  readonly items = this._items.asReadonly();

  load(): void {
    this.http.get<Item[]>('/api/items').subscribe(data => this._items.set(data));
  }
}

// ❌ Component owning HTTP — forbidden
export class ItemListPageComponent {
  private readonly http = inject(HttpClient);
  items: Item[] = [];
  ngOnInit() {
    this.http.get<Item[]>('/api/items').subscribe(data => this.items = data);  // WRONG
  }
}
```

## External templates and styles (mandatory)

Every component is a triplet of co-located files: `<name>.component.ts`, `<name>.component.html`, `<name>.component.scss` (or `.css`). The `.ts` references them with `templateUrl` and `styleUrls`. **Inline `template:` and `styles:` in the `@Component` decorator are forbidden** for any non-trivial component.

```typescript
// ✅ CORRECT — external template + styles
@Component({
  selector: 'app-user-profile',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.scss']
})
export class UserProfileComponent { /* ... */ }

// ❌ WRONG — inline template
@Component({
  selector: 'app-user-profile',
  template: `
    <section class="profile">
      <h2>{{ user().name }}</h2>
      <!-- ... 30 more lines ... -->
    </section>
  `,
  styles: [`.profile { padding: 1rem; }`]
})
export class UserProfileComponent { /* ... */ }
```

**Why this is non-negotiable**:
- IDE tooling: Angular Language Service, autocomplete, template type-checking, and Prettier all behave better against `.html` files than against template literals.
- Diffs: template-only changes don't pollute the `.ts` diff and vice versa, easing review.
- Separation of concerns at the file level: markup, behaviour, and styling are three concerns and three files.
- Designers and accessibility tooling can edit `.html`/`.scss` without touching TypeScript.
- Search/grep: finding "where is this markup defined" is unambiguous.

**Allowed exception**: trivial micro-components used as render-prop wrappers (≤ 5 markup lines, single binding, no logic) may use `template:`. When in doubt, externalise.
