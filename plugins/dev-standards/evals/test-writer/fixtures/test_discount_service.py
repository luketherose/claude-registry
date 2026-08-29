from decimal import Decimal

import pytest

from discount_service import DiscountService

# Existing suite: covers only the two happy-path tiers.
# Uncovered: total <= 0, unknown customer, blocked customer, STAFF override,
# rounding at the tier boundary, and the audit_log side effect.


def test_apply_five_percent_tier():
    service = DiscountService(StubRepo(tier="STANDARD"), StubAudit())
    assert service.apply(1, Decimal("1000")) == Decimal("950.00")


def test_apply_ten_percent_tier():
    service = DiscountService(StubRepo(tier="STANDARD"), StubAudit())
    assert service.apply(1, Decimal("5000")) == Decimal("4500.00")


class StubRepo:
    def __init__(self, tier):
        self.tier = tier

    def get(self, customer_id):
        return type("C", (), {"blocked": False, "tier": self.tier})()


class StubAudit:
    def record(self, *args):
        pass
