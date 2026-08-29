import logging

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self, repository, gateway):
        self.repository = repository
        self.gateway = gateway

    # no type hints, no return annotation, payload is a raw dict
    def place(self, payload):
        total = payload["total"]
        email = payload["customer"]["email"]
        card = payload["customer"]["card_number"]

        logger.info("placing order for %s card %s total %s", email, card, total)

        if total > 1000:
            payload["discount"] = total * 0.05

        try:
            charge = self.gateway.charge(total)
        except Exception:
            return None

        if not charge["ok"]:
            raise Exception("payment failed")

        order = self.repository.save(payload)
        return {"id": order["id"], "total": total}

    def cancel(self, order_id):
        try:
            self.repository.delete(order_id)
        except Exception as exc:
            logger.debug(exc)
        return True
