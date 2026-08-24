"""Exchange-independent order lifecycle and idempotency primitives."""
from dataclasses import dataclass
from enum import Enum

class OrderStatus(str, Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"

@dataclass(frozen=True)
class OrderIntent:
    client_order_id: str
    symbol: str
    side: str
    quantity: float
    price: float | None = None
    reduce_only: bool = False

@dataclass(frozen=True)
class OrderState:
    intent: OrderIntent
    status: OrderStatus
    filled_quantity: float = 0.0
    average_fill_price: float | None = None
    exchange_order_id: str | None = None

class OrderRegistry:
    def __init__(self) -> None:
        self._orders: dict[str, OrderState] = {}

    def submit_once(self, intent: OrderIntent) -> OrderState:
        existing = self._orders.get(intent.client_order_id)
        if existing is not None:
            return existing
        state = OrderState(intent, OrderStatus.NEW)
        self._orders[intent.client_order_id] = state
        return state

    def update(self, state: OrderState) -> None:
        self._orders[state.intent.client_order_id] = state

    def get(self, client_order_id: str) -> OrderState | None:
        return self._orders.get(client_order_id)
