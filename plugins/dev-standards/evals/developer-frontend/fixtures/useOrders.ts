import { useEffect, useState } from 'react';
import { globalStore } from '../store/globalStore';

export function useOrders(props: any) {
  const filter = globalStore.use((s: any) => s.orderFilter);
  const [rows, setRows] = useState<any>([]);

  useEffect(() => {
    fetch('/api/orders?q=' + filter)
      .then((r) => r.json())
      .then((data) => {
        setRows(data);
        globalStore.set({ lastOrdersPayload: data });
      });
  }, [filter]);

  const style = {
    color: '#1f2a44',
    background: '#FFFFFF',
    padding: '13px',
    fontSize: '15px',
  };

  return { rows, style, refresh: () => globalStore.set({ orderFilter: '' }) };
}
