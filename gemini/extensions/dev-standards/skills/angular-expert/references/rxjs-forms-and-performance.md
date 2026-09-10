# RxJS, change detection, forms and typing

Detail behind the reactive and performance rules in the SKILL.md body: operator
choice, subscription lifetime, change-detection levers, Reactive Forms and the
zero-`any` typing rule.

## Contents

- [RxJS and observables](#rxjs-and-observables)
- [Change detection and performance](#change-detection-and-performance)
- [Reactive Forms](#reactive-forms)
- [TypeScript: zero `any`](#typescript-zero-any)

## RxJS and observables

**Prefer `async` pipe** and avoid manual subscribes:

```typescript
// ✅ Correct
items$ = this.itemService.getAll();
// In the template: *ngIf="items$ | async as items"

// ❌ Avoid
ngOnInit() {
  this.itemService.getAll().subscribe(i => this.items = i);
}
```

**If subscribe is necessary**, manage the unsubscribe:

```typescript
private destroyRef = inject(DestroyRef);
ngOnInit() {
  this.service.data$
    .pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe(data => this.process(data));
}
```

**Correct flattening strategy**:
- `switchMap`: live search, cancels the previous request
- `concatMap`: sequential operations dependent on order
- `mergeMap`: independent parallel operations
- `exhaustMap`: form submit, ignores new clicks during the request

**Error handling**:
```typescript
this.service.getData().pipe(
  catchError(err => {
    this.errorMessage = 'Error loading data';
    return EMPTY;
  })
);
```

## Change detection and performance

**OnPush** on all dumb components:
```typescript
@Component({ changeDetection: ChangeDetectionStrategy.OnPush })
```

**TrackBy** in ngFor:
```typescript
trackById(index: number, item: Item): number { return item.id; }
// In the template: *ngFor="let i of items; trackBy: trackById"
```

**Pure Pipes**: prefer pipes over methods in the template (methods execute on every change detection cycle).

## Reactive Forms

```typescript
form = this.fb.group({
  name:  ['', [Validators.required, Validators.minLength(2)]],
  code:  ['', [Validators.required, codeValidator]],
  email: ['', [Validators.required, Validators.email]]
});

// Pure validator
export function codeValidator(control: AbstractControl): ValidationErrors | null {
  return /^[A-Z0-9]{5,}$/.test(control.value) ? null : { invalidCode: true };
}
```

Never use template-driven forms for complex forms.

## TypeScript: zero `any`

```typescript
// ❌ Avoid
getItem(id: any): any { ... }

// ✅ Correct
getItem(id: number): Observable<Item> { ... }

interface Item {
  id: number;
  name: string;
  code: string;
  isActive: boolean;
}
```
