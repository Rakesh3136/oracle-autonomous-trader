from dataclasses import dataclass
from oracle.core.trader import Action

@dataclass(frozen=True)
class PaperOrder:
    symbol: str
    action: Action
    quantity: float
    price: float

class PaperExecution:
    """Safe execution adapter: never contacts a live exchange."""
    def __init__(self) -> None:
        self.orders: list[PaperOrder] = []

    def submit(self, order: PaperOrder) -> PaperOrder:
        self.orders.append(order)
        return order
