import { useEffect, useState } from 'react';
import { globalStore } from '../store/globalStore';

// Props are untyped and the payload is `any`.
export function useOrders(props: any) {
  // Filter text is used only inside this hook but is kept in the global store.
  const filter = globalStore.use((s: any) => s.orderFilter);
  const [rows, setRows] = useState<any>([]);

  useEffect(() => {
    fetch('/api/orders?q=' + filter)
      .then((r) => r.json())
      .then((data) => {
        setRows(data);
        globalStore.set({ lastOrdersPayload: data });
      });
    // dependency array omits `props.customerId`, which the URL below depends on
  }, [filter]);

  const style = {
    color: '#1f2a44',
    background: '#FFFFFF',
    padding: '13px',
    fontSize: '15px',
  };

  return { rows, style, refresh: () => globalStore.set({ orderFilter: '' }) };
}
