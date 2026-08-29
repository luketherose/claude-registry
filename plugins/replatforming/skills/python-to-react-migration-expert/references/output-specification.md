# Output specification

## Contents

- Output Format
- 1. Migration Scope Summary
- 2. Component Decomposition
- 3. TypeScript Type Definitions
- 4. Data Fetching Layer (TanStack Query)
- 5. State Management Strategy
- 6. Form Migration
- 7. Routing Migration
- 8. Migration Pitfalls

## Output Format

### 1. Migration Scope Summary

- UI sections being migrated
- Python template patterns identified
- React components to be created

### 2. Component Decomposition

Component tree hierarchy:

```
<AppLayout>
  <NavBar />
  <Routes>
    <Route path="/orders" element={<OrdersPage />}>
      <OrderList />  [uses useOrders hook]
      <OrderFilters />
    </Route>
    <Route path="/orders/:id" element={<OrderDetailPage />}>
      <OrderHeader />
      <OrderItems />  [list of <OrderItemRow />]
      <OrderActions />  [conditionally rendered]
    </Route>
  </Routes>
</AppLayout>
```

For each component:

| Component | Responsibility | Props | Server State? | Local State? |
|---|---|---|---|---|

### 3. TypeScript Type Definitions

For each API response and shared data structure:

```typescript
// Order types — derived from API contract
export interface Order {
  id: number;
  customerId: number;
  status: 'PENDING' | 'CONFIRMED' | 'SHIPPED' | 'CANCELLED';
  items: OrderItem[];
  createdAt: string; // ISO 8601
  totalAmount: number;
}

export interface OrderItem {
  id: number;
  productId: number;
  quantity: number;
  unitPrice: number;
}
```

### 4. Data Fetching Layer (TanStack Query)

For each API interaction:

```typescript
// hooks/useOrders.ts
export function useOrders(filters?: OrderFilters) {
  return useQuery({
    queryKey: ['orders', filters],
    queryFn: () => orderApi.getOrders(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateOrderRequest) => orderApi.createOrder(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
  });
}
```

### 5. State Management Strategy

| State Type | Approach | Library | Rationale |
|---|---|---|---|
| Server state (API data) | TanStack Query | TanStack Query | |
| Auth state | Global store | Zustand | |
| UI state (modal, drawer) | Component local | useState | |
| Form state | RHF controller | React Hook Form | |
| URL/filter state | URL search params | | |

For complex global state, provide Zustand store stub:

```typescript
// store/authStore.ts
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()((set) => ({
  user: null,
  isAuthenticated: false,
  login: async (credentials) => { /* ... */ },
  logout: () => set({ user: null, isAuthenticated: false }),
}));
```

### 6. Form Migration

For each Django form being migrated:

---
**[DjangoFormName]** → `[ComponentName].tsx`

Original fields: [list from template]

React Hook Form + Zod stub:

```typescript
const createOrderSchema = z.object({
  customerId: z.number().positive('Customer is required'),
  items: z.array(z.object({
    productId: z.number().positive(),
    quantity: z.number().int().positive().max(100),
  })).min(1, 'At least one item is required'),
});

type CreateOrderFormData = z.infer<typeof createOrderSchema>;

export function CreateOrderForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<CreateOrderFormData>({
    resolver: zodResolver(createOrderSchema),
  });
  
  const createOrder = useCreateOrder();
  
  const onSubmit = (data: CreateOrderFormData) => {
    createOrder.mutate(data);
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* fields */}
    </form>
  );
}
```

Validation rules migrated from Django:
| Django Validation | Zod Equivalent |
|---|---|

---

### 7. Routing Migration

| Django URL Pattern | React Router Route | Component | Notes |
|---|---|---|---|

Routing configuration stub:

```typescript
// router/index.tsx
export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/orders" replace /> },
      { path: 'orders', element: <OrdersPage /> },
      { path: 'orders/:id', element: <OrderDetailPage /> },
    ],
  },
]);
```

### 8. Migration Pitfalls

| Pitfall | Django Behavior | React Equivalent | Solution |
|---|---|---|---|

Must include:
- CSRF handling
- Form submission (multipart vs. JSON)
- Session vs. JWT auth
- Server-side validation messages vs. client validation
- Django's built-in pagination vs. client-side
- Template context vs. React props/state mental model

---
