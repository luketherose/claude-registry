# Worked example

## Example

**Input:** `COMPONENT_NAME = "OrderHistoryPage"`, Django view + template injected,
React architecture spec provided.

**Output excerpt:**

```tsx
// hooks/useOrderHistory.ts
export function useOrderHistory(customerId: string) {
  return useQuery({
    queryKey: ['orders', customerId],
    queryFn: () => orderApi.getByCustomer(customerId),
  });
}

// pages/OrderHistoryPage.tsx
export function OrderHistoryPage() {
  const { customerId } = useParams<{ customerId: string }>();
  const { data, isLoading, error } = useOrderHistory(customerId!);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorBoundaryFallback error={error} />;
  return <OrderList orders={data!} />;
}
```

**Business rules preserved:** BR-03 (sort by date desc), BR-04 (show last 12 months by default).

---
