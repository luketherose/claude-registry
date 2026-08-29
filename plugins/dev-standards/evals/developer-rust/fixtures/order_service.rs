use std::collections::HashMap;
use std::sync::{Arc, Mutex};

pub trait PriceRule {
    fn apply(&self, total: f64) -> f64;
}

pub struct OrderService {
    cache: Arc<Mutex<HashMap<u64, Order>>>,
    rule: Box<dyn PriceRule>,
}

impl OrderService {
    pub fn place(&self, raw: &str, ids: &Vec<u64>) -> Order {
        let payload: Payload = serde_json::from_str(raw).unwrap();
        let customer = self.lookup(payload.customer_id).expect("customer must exist");

        let mut lines = Vec::new();
        for id in ids {
            let label = format!("line-{}", id);
            let item = self.cache.lock().unwrap().get(id).unwrap().clone();
            lines.push((label, item));
        }

        let total = self.rule.apply(payload.total);
        let owner = customer.name.clone();

        Order {
            id: payload.customer_id,
            owner,
            total,
            lines: lines.clone(),
        }
    }

    fn lookup(&self, id: u64) -> Option<Customer> {
        self.cache.lock().unwrap().get(&id).map(|o| o.customer.clone())
    }
}
