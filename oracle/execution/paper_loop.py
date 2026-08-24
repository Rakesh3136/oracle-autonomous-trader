"""End-to-end paper execution coordinator."""
from dataclasses import dataclass
from oracle.execution.orders import OrderIntent, OrderRegistry, OrderState, OrderStatus

@dataclass(frozen=True)
class PaperResult:
    order: OrderState
    accepted: bool

class PaperExecutionCoordinator:
    def __init__(self) -> None:
        self.registry = OrderRegistry()

    def submit(self, intent: OrderIntent) -> PaperResult:
        existing = self.registry.get(intent.client_order_id)
        if existing is not None:
            return PaperResult(existing, True)
        order = self.registry.submit_once(intent)
        acknowledged = OrderState(order.intent, OrderStatus.ACKNOWLEDGED, exchange_order_id=f"paper-{intent.client_order_id}")
        self.registry.update(acknowledged)
        return PaperResult(acknowledged, True)
