from decimal import Decimal


class DiscountRejected(Exception):
    """Raised when a discount cannot be applied to the order."""


class DiscountService:
    """Applies the loyalty discount ladder to an order total."""

    TIERS = ((Decimal("1000"), Decimal("0.05")), (Decimal("5000"), Decimal("0.10")))

    def __init__(self, customer_repo, audit_log):
        self._customers = customer_repo
        self._audit = audit_log

    def apply(self, customer_id: int, total: Decimal) -> Decimal:
        if total <= 0:
            raise ValueError("total must be positive")

        customer = self._customers.get(customer_id)
        if customer is None:
            raise DiscountRejected(f"unknown customer {customer_id}")
        if customer.blocked:
            raise DiscountRejected("customer is blocked")

        rate = Decimal("0")
        for threshold, tier_rate in self.TIERS:
            if total >= threshold:
                rate = tier_rate

        if customer.tier == "STAFF":
            rate = max(rate, Decimal("0.20"))

        discounted = (total * (Decimal("1") - rate)).quantize(Decimal("0.01"))
        self._audit.record(customer_id, total, discounted)
        return discounted
