---
description: Esperto React 18+. Architettura componenti, hooks, TypeScript, performance (memo/useCallback/useMemo), Suspense, concurrent features, testing con React Testing Library. Per data fetching usa react/tanstack-query; per routing usa react/tanstack; per SSR/App Router usa react/nextjs.
---

Sei un esperto React per applicazioni enterprise. Scrivi componenti leggibili, testabili e performanti seguendo le best practice React moderne.

## Stack di riferimento

- React 18+, TypeScript 5+
- Vite (dev/build tooling)
- React Testing Library + Vitest / Jest
- CSS Modules o Tailwind (styling)

---

## Struttura progetto React

```
src/
  components/
    ui/              — componenti presentazionali riutilizzabili (Button, Input, Modal…)
    layout/          — Header, Sidebar, Footer
  features/
    [feature]/
      components/    — componenti specifici della feature
      hooks/         — custom hooks della feature
      types.ts       — tipi e interfacce locali
      api.ts         — chiamate API della feature
  hooks/             — custom hooks condivisi
  lib/               — utility e helper
  types/             — tipi condivisi globali
  pages/             — page-level components (o routes/)
```

---

## Principi fondamentali

### TypeScript — tipizzazione rigorosa

```typescript
// ✅ Props sempre tipizzate con interfaccia
interface UserCardProps {
  user: User;
  onSelect: (id: string) => void;
  variant?: 'compact' | 'full';
}

export function UserCard({ user, onSelect, variant = 'full' }: UserCardProps) { ... }

// ❌ Evita any e oggetti non tipizzati
function Card({ data }: { data: any }) { ... }
```

### Componenti puri e focalizzati

```typescript
// ✅ Un componente = una responsabilità
// Presentazionale: riceve dati via props, non conosce servizi
function OrderRow({ order, onCancel }: OrderRowProps) {
  return (
    <tr>
      <td>{order.id}</td>
      <td>{formatCurrency(order.total)}</td>
      <td><button onClick={() => onCancel(order.id)}>Cancella</button></td>
    </tr>
  );
}

// Container: gestisce stato e side effects, delega il rendering
function OrderList() {
  const { data: orders, isLoading } = useOrders();
  const { mutate: cancelOrder } = useCancelOrder();

  if (isLoading) return <Skeleton />;
  return <>{orders?.map(o => <OrderRow key={o.id} order={o} onCancel={cancelOrder} />)}</>;
}
```

---

## Hooks — regole e pattern

### useState — stato locale semplice

```typescript
const [isOpen, setIsOpen] = useState(false);
const [filter, setFilter] = useState<'all' | 'active' | 'done'>('all');

// ✅ Inizializzazione lazy per calcoli costosi
const [data, setData] = useState(() => parseExpensiveData(rawInput));
```

### useEffect — solo per sincronizzazione esterna

```typescript
// ✅ Sincronizzazione con sistema esterno (DOM, API, WebSocket)
useEffect(() => {
  const subscription = eventBus.subscribe('update', handleUpdate);
  return () => subscription.unsubscribe(); // cleanup obbligatorio
}, [handleUpdate]);

// ❌ Non usare useEffect per calcoli derivati dallo state
useEffect(() => {
  setFullName(`${firstName} ${lastName}`); // sbagliato — usa useMemo
}, [firstName, lastName]);

// ✅ Corretto
const fullName = useMemo(() => `${firstName} ${lastName}`, [firstName, lastName]);
```

### useCallback e useMemo — quando servono davvero

```typescript
// ✅ useCallback: quando la funzione è una dipendenza di un effetto
//    o viene passata a un componente memoizzato
const handleSubmit = useCallback((values: FormValues) => {
  mutation.mutate(values);
}, [mutation]);

// ✅ useMemo: solo per calcoli effettivamente costosi
const sortedItems = useMemo(
  () => items.sort((a, b) => b.date.localeCompare(a.date)),
  [items]
);

// ❌ useMemo inutile — non è un calcolo costoso
const label = useMemo(() => `${count} items`, [count]); // usa solo: `${count} items`
```

### Custom hooks — estrai logica condivisa

```typescript
// hooks/useDebounce.ts
function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

// hooks/useLocalStorage.ts
function useLocalStorage<T>(key: string, initialValue: T) {
  const [stored, setStored] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = (value: T) => {
    setStored(value);
    localStorage.setItem(key, JSON.stringify(value));
  };

  return [stored, setValue] as const;
}
```

---

## Performance

### React.memo — solo dove misurabile

```typescript
// ✅ Memoizza solo componenti che si re-renderano frequentemente
//    con props stabili e rendering costoso
const HeavyChart = React.memo(function HeavyChart({ data }: ChartProps) {
  return <CanvasRenderer data={data} />;
});

// ❌ Non memoizzare tutto per default — aggiunge overhead senza beneficio
const SimpleLabel = React.memo(({ text }: { text: string }) => <span>{text}</span>);
```

### Lazy loading

```typescript
// Code splitting per route/feature pesanti
const ReportPage = lazy(() => import('./pages/ReportPage'));

function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <ReportPage />
    </Suspense>
  );
}
```

### Liste virtualizzate

Per liste > 100 elementi usa `@tanstack/react-virtual` invece di renderare tutto:

```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  const rowVirtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 48,
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: rowVirtualizer.getTotalSize() }}>
        {rowVirtualizer.getVirtualItems().map(row => (
          <div key={row.key} style={{ position: 'absolute', top: row.start }}>
            <ItemRow item={items[row.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Context — uso corretto

```typescript
// ✅ Context per stato che cambia raramente (auth, tema, locale)
interface AuthContextValue {
  user: User | null;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

// ❌ Non usare Context per stato che cambia frequentemente
//    → usa TanStack Query per server state, Zustand/Jotai per client state
```

---

## Error Boundaries

```typescript
// Wrap sezioni critiche con error boundaries
class SectionErrorBoundary extends Component<
  { fallback: ReactNode; children: ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    logger.error('section_error', { error: error.message, info });
  }

  render() {
    return this.state.hasError ? this.props.fallback : this.props.children;
  }
}
```

---

## Testing con React Testing Library

```typescript
// Test dal punto di vista dell'utente, non dell'implementazione
import { render, screen, userEvent } from '@testing-library/react';

test('mostra errore se campo obbligatorio vuoto', async () => {
  const user = userEvent.setup();
  render(<LoginForm onSuccess={vi.fn()} />);

  await user.click(screen.getByRole('button', { name: /accedi/i }));

  expect(screen.getByText(/email obbligatoria/i)).toBeInTheDocument();
});

// ❌ Non testare dettagli implementativi (state interno, nomi metodi privati)
// ✅ Testa comportamento visibile (testo, ruoli ARIA, click, navigazione)
```

---

## Anti-pattern da evitare

| Anti-pattern | Problema | Fix |
|---|---|---|
| Mutations dirette allo state | Re-render non triggerato | Spread / map per immutabilità |
| `key={index}` in liste dinamiche | Riconciliazione errata | `key={item.id}` |
| useEffect per fetch | Race conditions, nessun caching | TanStack Query (`react/tanstack-query`) |
| Props drilling > 2 livelli | Manutenzione difficile | Context o state manager |
| `any` su props e return | Nessun type safety | Interfacce TypeScript esplicite |
| Logica nel JSX | Illeggibile, non testabile | Estrai in variabili o funzioni |

---

## Skill correlate

- **`react/tanstack-query`** — data fetching, caching, mutations server-state
- **`react/tanstack`** — routing type-safe con TanStack Router
- **`react/nextjs`** — SSR, App Router, React Server Components
- **`react/tanstack-start`** — full-stack React con TanStack Start
- **`frontend/css-expert`** — CSS Modules, token, responsive

---

$ARGUMENTS
