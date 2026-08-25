"""End-to-end paper execution coordinator."""
from dataclasses import dataclass

from oracle.execution.fills import Fill
from oracle.execution.orders import OrderIntent, OrderRegistry, OrderState, OrderStatus


@dataclass(frozen=True)
class PaperResult:
    order: OrderState
    accepted: bool


class PaperExecutionCoordinator:
    """Deterministic paper order lifecycle with idempotent submission and fills."""

    def __init__(self) -> None:
        self.registry = OrderRegistry()
        self._fills: list[Fill] = []

    def submit(self, intent: OrderIntent) -> PaperResult:
        existing = self.registry.get(intent.client_order_id)
        if existing is not None:
            return PaperResult(existing, existing.status not in {OrderStatus.REJECTED})
        order = self.registry.submit_once(intent)
        acknowledged = OrderState(
            order.intent,
            OrderStatus.ACKNOWLEDGED,
            exchange_order_id=f"paper-{intent.client_order_id}",
        )
        self.registry.update(acknowledged)
        return PaperResult(acknowledged, True)

    def fill(
        self,
        client_order_id: str,
        quantity: float,
        price: float,
        fee: float = 0.0,
    ) -> OrderState:
        state = self._require_active(client_order_id)
        if quantity <= 0:
            raise ValueError("fill quantity must be positive")
        if price <= 0:
            raise ValueError("fill price must be positive")
        if fee < 0:
            raise ValueError("fill fee cannot be negative")

        filled_quantity = state.filled_quantity + quantity
        if filled_quantity > state.intent.quantity + 1e-12:
            raise ValueError("fill quantity exceeds order quantity")

        previous_notional = state.filled_quantity * (state.average_fill_price or 0.0)
        average_price = (previous_notional + quantity * price) / filled_quantity
        status = (
            OrderStatus.FILLED
            if abs(filled_quantity - state.intent.quantity) <= 1e-12
            else OrderStatus.PARTIALLY_FILLED
        )
        updated = OrderState(
            state.intent,
            status,
            filled_quantity=filled_quantity,
            average_fill_price=average_price,
            exchange_order_id=state.exchange_order_id,
        )
        self.registry.update(updated)
        self._fills.append(
            Fill(
                order_id=state.exchange_order_id or client_order_id,
                quantity=quantity,
                price=price,
                fee=fee,
            )
        )
        return updated

    def cancel(self, client_order_id: str) -> OrderState:
        state = self._require_active(client_order_id)
        canceled = OrderState(
            state.intent,
            OrderStatus.CANCELED,
            filled_quantity=state.filled_quantity,
            average_fill_price=state.average_fill_price,
            exchange_order_id=state.exchange_order_id,
        )
        self.registry.update(canceled)
        return canceled

    def reject(self, client_order_id: str) -> OrderState:
        state = self.registry.get(client_order_id)
        if state is None:
            raise KeyError(f"unknown paper order: {client_order_id}")
        if state.status is not OrderStatus.ACKNOWLEDGED:
            raise ValueError("only acknowledged orders can be rejected")
        rejected = OrderState(
            state.intent,
            OrderStatus.REJECTED,
            exchange_order_id=state.exchange_order_id,
        )
        self.registry.update(rejected)
        return rejected

    def fills(self) -> tuple[Fill, ...]:
        return tuple(self._fills)

    def _require_active(self, client_order_id: str) -> OrderState:
        state = self.registry.get(client_order_id)
        if state is None:
            raise KeyError(f"unknown paper order: {client_order_id}")
        if state.status not in {OrderStatus.ACKNOWLEDGED, OrderStatus.PARTIALLY_FILLED}:
            raise ValueError(f"paper order is not active: {state.status.value}")
        return state
