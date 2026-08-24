"""Trade lifecycle state machine for entries, protection, exits and closure."""
from dataclasses import dataclass, replace
from enum import Enum

class PositionState(str, Enum):
    PLANNED = "planned"
    OPEN = "open"
    PARTIAL = "partial"
    EXITING = "exiting"
    CLOSED = "closed"
    INVALIDATED = "invalidated"

@dataclass(frozen=True)
class TradePlan:
    symbol: str
    side: int
    entry: float
    stop: float
    target: float
    quantity: float
    state: PositionState = PositionState.PLANNED
    remaining_quantity: float = 0.0
    realized_pnl: float = 0.0

    def __post_init__(self) -> None:
        if self.remaining_quantity == 0.0:
            object.__setattr__(self, "remaining_quantity", self.quantity)

    def open(self) -> "TradePlan":
        if self.state is not PositionState.PLANNED:
            raise ValueError("trade is not planned")
        return replace(self, state=PositionState.OPEN)

    def reduce(self, quantity: float, exit_price: float) -> "TradePlan":
        if self.state not in {PositionState.OPEN, PositionState.PARTIAL}:
            raise ValueError("trade is not active")
        if quantity <= 0 or quantity > self.remaining_quantity:
            raise ValueError("invalid reduction quantity")
        pnl = (exit_price - self.entry) * quantity * self.side
        remaining = self.remaining_quantity - quantity
        state = PositionState.CLOSED if remaining == 0 else PositionState.PARTIAL
        return replace(self, remaining_quantity=remaining, realized_pnl=self.realized_pnl + pnl, state=state)

    def invalidate(self) -> "TradePlan":
        if self.state not in {PositionState.OPEN, PositionState.PARTIAL}:
            raise ValueError("trade is not active")
        return replace(self, state=PositionState.INVALIDATED)

    def trailing_stop(self, new_stop: float) -> "TradePlan":
        if self.state not in {PositionState.OPEN, PositionState.PARTIAL}:
            raise ValueError("trade is not active")
        if (self.side > 0 and new_stop <= self.stop) or (self.side < 0 and new_stop >= self.stop):
            raise ValueError("trailing stop must only tighten")
        return replace(self, stop=new_stop)
