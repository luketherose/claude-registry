# Output specification

## Contents

- Output Format
- 1. Angular Application Structure
- 2. Component Hierarchy
- 3. TypeScript Interfaces
- 4. Service Architecture
- 5. Reactive Form Migration
- 6. Routing Configuration
- 7. HTTP Interceptors
- 8. RxJS Patterns
- 9. Migration Pitfalls

## Output Format

### 1. Angular Application Structure

```
src/
├── app/
│   ├── core/
│   │   ├── services/         # Singleton services (auth, HTTP interceptors)
│   │   ├── guards/           # Route guards
│   │   ├── interceptors/     # HTTP interceptors
│   │   └── models/           # TypeScript interfaces
│   ├── shared/
│   │   ├── components/       # Reusable UI components
│   │   └── pipes/            # Shared pipes
│   ├── features/
│   │   └── orders/           # Feature module
│   │       ├── components/
│   │       ├── services/
│   │       └── orders.routes.ts
│   ├── app.component.ts
│   └── app.routes.ts
```

### 2. Component Hierarchy

```
AppComponent (shell)
  NavbarComponent
  <router-outlet>
    OrdersComponent (feature root, lazy loaded)
      OrderListComponent
        OrderCardComponent
      OrderFiltersComponent
    OrderDetailComponent
      OrderHeaderComponent
      OrderItemsTableComponent
      OrderActionsComponent
```

For each component:

| Component | Selector | Responsibility | Inputs | Outputs | Change Detection |
|---|---|---|---|---|---|
| | | | | | OnPush |

### 3. TypeScript Interfaces

```typescript
// core/models/order.model.ts
export interface Order {
  id: number;
  customerId: number;
  status: OrderStatus;
  items: OrderItem[];
  createdAt: string;
  totalAmount: number;
}

export type OrderStatus = 'PENDING' | 'CONFIRMED' | 'SHIPPED' | 'CANCELLED';

export interface OrderItem {
  id: number;
  productId: number;
  quantity: number;
  unitPrice: number;
}
```

### 4. Service Architecture

For each data domain:

```typescript
// features/orders/services/order.service.ts
@Injectable({ providedIn: 'root' })
export class OrderService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = '/api/v1/orders';

  getOrders(filters?: OrderFilters): Observable<OrderListResponse> {
    const params = new HttpParams({ fromObject: { ...filters } });
    return this.http.get<OrderListResponse>(this.apiUrl, { params });
  }

  getOrder(id: number): Observable<Order> {
    return this.http.get<Order>(`${this.apiUrl}/${id}`);
  }

  createOrder(request: CreateOrderRequest): Observable<Order> {
    return this.http.post<Order>(this.apiUrl, request);
  }
}
```

### 5. Reactive Form Migration

For each Django form:

```typescript
// features/orders/components/create-order-form/create-order-form.component.ts
@Component({
  selector: 'app-create-order-form',
  standalone: true,
  imports: [ReactiveFormsModule, MatFormFieldModule, MatButtonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <mat-form-field>
        <mat-label>Customer</mat-label>
        <input matInput formControlName="customerId" type="number">
        @if (form.get('customerId')?.hasError('required')) {
          <mat-error>Customer is required</mat-error>
        }
      </mat-form-field>
      
      <button mat-raised-button type="submit" [disabled]="form.invalid">
        Create Order
      </button>
    </form>
  `
})
export class CreateOrderFormComponent {
  private readonly orderService = inject(OrderService);
  private readonly fb = inject(FormBuilder);

  form = this.fb.group({
    customerId: [null, [Validators.required, Validators.min(1)]],
    items: this.fb.array([], Validators.required),
  });

  onSubmit(): void {
    if (this.form.valid) {
      this.orderService.createOrder(this.form.value as CreateOrderRequest)
        .subscribe({ /* ... */ });
    }
  }
}
```

Validation migration:
| Django Validation | Angular Validators | Custom Validator? |
|---|---|---|

### 6. Routing Configuration

```typescript
// app.routes.ts
export const appRoutes: Routes = [
  { path: '', redirectTo: '/orders', pathMatch: 'full' },
  {
    path: 'orders',
    loadChildren: () => import('./features/orders/orders.routes').then(m => m.ordersRoutes),
    canActivate: [authGuard],
  },
  { path: '**', component: NotFoundComponent },
];

// features/orders/orders.routes.ts
export const ordersRoutes: Routes = [
  { path: '', component: OrderListComponent },
  { path: ':id', component: OrderDetailComponent },
  { path: 'new', component: CreateOrderComponent },
];
```

Django URL to Angular Route mapping:
| Django URL | Angular Route | Component | Guard |
|---|---|---|---|

### 7. HTTP Interceptors

```typescript
// core/interceptors/auth.interceptor.ts
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.getToken();
  
  if (token) {
    req = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`)
    });
  }
  return next(req);
};

// core/interceptors/error.interceptor.ts
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) { /* redirect to login */ }
      return throwError(() => error);
    })
  );
};
```

### 8. RxJS Patterns

Key patterns for this migration:

```typescript
// Correct: switchMap for dependent HTTP calls
this.route.params.pipe(
  switchMap(params => this.orderService.getOrder(+params['id'])),
  takeUntilDestroyed(),
).subscribe(order => this.order.set(order));

// Correct: forkJoin for parallel calls
forkJoin({
  order: this.orderService.getOrder(id),
  products: this.productService.getProducts(),
}).subscribe(({ order, products }) => { /* ... */ });

// WRONG — nested subscriptions:
// this.orderService.getOrder(id).subscribe(order => {
//   this.productService.getProducts().subscribe(...) // ← anti-pattern
// });
```

### 9. Migration Pitfalls

| Pitfall | Django Behavior | Angular Equivalent | Solution |
|---|---|---|---|

Must include:
- CSRF handling difference
- Django form re-render on error vs. Angular reactive form error state
- Server-side redirect vs. Angular router navigation
- Django context processor vs. global services
- Django template filters vs. Angular pipes

---
