use std::collections::HashMap;
use std::sync::{Arc, Mutex};

pub trait PriceRule {
    fn apply(&self, total: f64) -> f64;
}

pub struct OrderService {
    // Arc<Mutex<..>> on a field only ever touched from one task
    cache: Arc<Mutex<HashMap<u64, Order>>>,
    // Box<dyn Trait> where a single generic parameter would do
    rule: Box<dyn PriceRule>,
}

impl OrderService {
    pub fn place(&self, raw: &str, ids: &Vec<u64>) -> Order {
        let payload: Payload = serde_json::from_str(raw).unwrap();
        let customer = self.lookup(payload.customer_id).expect("customer must exist");

        let mut lines = Vec::new();
        for id in ids {
            // allocation inside the hot loop: a new String per iteration
            let label = format!("line-{}", id);
            let item = self.cache.lock().unwrap().get(id).unwrap().clone();
            lines.push((label, item));
        }

        let total = self.rule.apply(payload.total);
        // clone() added to silence the borrow checker rather than restructuring ownership
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
