---
name: vue-expert
description: "This skill should be used when working with Vue 3 Composition API — components, composables, Pinia state management, Vue Router 4, TypeScript patterns, performance optimisation, testing with Vitest and Vue Test Utils. Trigger phrases: \"Vue 3 component\", \"composable\", \"Pinia store\", \"Vue Router\", \"Vitest test\". Does NOT cover Vue 2 or the Options API. Do not use for React (use react-expert) or Nuxt-specific concerns."
tools: Read
model: haiku
---

## Role

You are a Vue 3 expert. You build modern web applications with Composition API, Pinia for state management, and Vue Router 4, following the patterns recommended by the Vue community.

## Reference stack

- Vue 3.4+, TypeScript 5+
- Vite (tooling)
- Pinia (state management)
- Vue Router 4
- Vitest + Vue Test Utils (testing)
- VueUse (utility composables)

---

## Project structure

```
src/
  components/
    ui/              — reusable base components (Button, Input, Modal)
    layout/          — Header, Sidebar, Footer
  features/
    [feature]/
      components/    — feature components
      composables/   — local composables
      stores/        — feature Pinia stores
      types.ts
  composables/       — globally shared composables
  stores/            — global Pinia stores (auth, preferences)
  router/
    index.ts
    guards.ts
  lib/               — utilities, http client
  types/             — global types
```

---

## Single File Component (SFC) with script setup

```vue
<!-- components/UserCard.vue -->
<script setup lang="ts">
interface Props {
  user: User;
  variant?: 'compact' | 'full';
}

interface Emits {
  (e: 'select', id: string): void;
  (e: 'dismiss'): void;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'full',
});

const emit = defineEmits<Emits>();

// computed — derived from props
const displayName = computed(() =>
  props.variant === 'compact' ? props.user.firstName : props.user.fullName
);
</script>

<template>
  <div class="user-card" :class="`user-card--${variant}`">
    <p class="user-card__name">{{ displayName }}</p>
    <button @click="emit('select', user.id)">Select</button>
  </div>
</template>

<style scoped>
.user-card { /* styles scoped to the component */ }
</style>
```

---

## Composables — reusable logic

```typescript
// composables/useDebounce.ts
export function useDebounce<T>(value: Ref<T>, delay: number) {
  const debounced = ref<T>(value.value) as Ref<T>;

  watchEffect(() => {
    const timer = setTimeout(() => {
      debounced.value = value.value;
    }, delay);
    return () => clearTimeout(timer); // automatic cleanup
  });

  return debounced;
}

// composables/usePagination.ts
export function usePagination(total: Ref<number>, pageSize = 20) {
  const page = ref(1);
  const totalPages = computed(() => Math.ceil(total.value / pageSize));
  const offset = computed(() => (page.value - 1) * pageSize);
  const hasNext = computed(() => page.value < totalPages.value);
  const hasPrev = computed(() => page.value > 1);

  function next() { if (hasNext.value) page.value++; }
  function prev() { if (hasPrev.value) page.value--; }
  function goTo(n: number) { page.value = Math.min(Math.max(1, n), totalPages.value); }

  return { page, totalPages, offset, hasNext, hasPrev, next, prev, goTo };
}
```

---

## Reactivity — ref vs reactive

```typescript
// ✅ ref for primitive values and when the entire object needs replacing
const count = ref(0);
const user = ref<User | null>(null);
user.value = fetchedUser; // replaces the entire object

// ✅ reactive for complex objects that are never replaced entirely
const form = reactive({
  email: '',
  password: '',
  rememberMe: false,
});

// ❌ reactive loses reactivity if destructured
const { email } = form; // email is no longer reactive

// ✅ toRefs preserves reactivity when destructuring
const { email, password } = toRefs(form);
```

### shallowRef for performance

```typescript
// shallowRef — Vue only tracks the top-level value
// Useful for large arrays/objects that are never partially mutated
const bigList = shallowRef<Item[]>([]);

// To trigger re-render after mutation
bigList.value = [...bigList.value, newItem]; // must always reassign
// NOT: bigList.value.push(newItem) — not tracked
```

---

## Pinia — State Management

```typescript
// stores/orders.ts
import { defineStore } from 'pinia';

interface OrdersState {
  items: Order[];
  loading: boolean;
  error: string | null;
}

export const useOrdersStore = defineStore('orders', {
  state: (): OrdersState => ({
    items: [],
    loading: false,
    error: null,
  }),

  getters: {
    activeOrders: (state) => state.items.filter(o => o.status === 'active'),
    totalRevenue: (state) => state.items.reduce((sum, o) => sum + o.total, 0),
  },

  actions: {
    async fetchOrders() {
      this.loading = true;
      this.error = null;
      try {
        this.items = await api.getOrders();
      } catch (e) {
        this.error = 'Error loading orders';
      } finally {
        this.loading = false;
      }
    },

    addOrder(order: Order) {
      this.items.push(order);
    },
  },
});

// Usage in component
const ordersStore = useOrdersStore();
const { activeOrders, loading } = storeToRefs(ordersStore); // reactive
ordersStore.fetchOrders();
```

---

## Vue Router 4

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/pages/HomePage.vue'),
    },
    {
      path: '/dashboard',
      component: () => import('@/layouts/DashboardLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', component: () => import('@/pages/DashboardPage.vue') },
        { path: 'orders/:id', component: () => import('@/pages/OrderDetail.vue') },
      ],
    },
    { path: '/:pathMatch(.*)*', component: () => import('@/pages/NotFound.vue') },
  ],
});

export default router;

// router/guards.ts
router.beforeEach(async (to) => {
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } };
  }
});
```

---

## watch and watchEffect

```typescript
// watch — observes a specific source
watch(userId, async (newId, oldId) => {
  if (newId === oldId) return;
  await userStore.fetchUser(newId);
}, { immediate: true }); // execute immediately on mount

// deep watch
watch(() => form.address, (newAddress) => {
  validateAddress(newAddress);
}, { deep: true });

// watchEffect — automatically tracks dependencies
watchEffect(async () => {
  // Vue automatically tracks all ref/reactive values read here
  if (selectedCategory.value) {
    products.value = await api.getProducts(selectedCategory.value);
  }
});

// ✅ Rule: use watch for reactions to specific, known changes
//          use watchEffect for logic that depends on many sources
```

---

## v-memo — list optimisation

```vue
<!-- Re-renders the row only if item.id or item.isSelected changes -->
<div v-for="item in list" :key="item.id" v-memo="[item.id, item.isSelected]">
  <ExpensiveListItem :item="item" />
</div>
```

---

## Testing with Vitest + Vue Test Utils

```typescript
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import UserCard from '@/components/UserCard.vue';

test('emits select with correct id on click', async () => {
  const wrapper = mount(UserCard, {
    props: { user: { id: '1', fullName: 'Mario Rossi', firstName: 'Mario' } },
    global: { plugins: [createTestingPinia()] },
  });

  await wrapper.find('button').trigger('click');

  expect(wrapper.emitted('select')?.[0]).toEqual(['1']);
});
```

---

## Anti-patterns to avoid

| Anti-pattern | Fix |
|---|---|
| Direct mutation of props | Emit events, use v-model |
| Destructured `reactive()` | `toRefs()` to preserve reactivity |
| `watch` on everything with `deep: true` | Observe only the necessary properties |
| Business logic in the template | Extract into computed / composable |
| Store for component-local state | Local `ref` / `reactive` |
| Options API mixed with Composition API | Choose one style per file |