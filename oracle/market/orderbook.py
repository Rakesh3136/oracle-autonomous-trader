"""Deterministic order-book snapshot/delta reconstruction."""
from dataclasses import dataclass
from oracle.market.models import OrderBookLevel

@dataclass(frozen=True)
class BookUpdate:
    side: str
    price: float
    quantity: float

class OrderBookBuilder:
    def __init__(self) -> None:
        self._bids: dict[float, float] = {}
        self._asks: dict[float, float] = {}
        self.sequence: int | None = None

    def snapshot(self, bids: list[tuple[float, float]], asks: list[tuple[float, float]], sequence: int | None = None) -> None:
        self._bids = {p: q for p, q in bids if q > 0}
        self._asks = {p: q for p, q in asks if q > 0}
        self.sequence = sequence

    def apply(self, updates: list[BookUpdate], sequence: int | None = None) -> None:
        for update in updates:
            book = self._bids if update.side.lower() == "bid" else self._asks
            if update.quantity <= 0:
                book.pop(update.price, None)
            else:
                book[update.price] = update.quantity
        self.sequence = sequence if sequence is not None else self.sequence

    def levels(self, depth: int = 50) -> tuple[tuple[OrderBookLevel, ...], tuple[OrderBookLevel, ...]]:
        bids = tuple(OrderBookLevel(p, q) for p, q in sorted(self._bids.items(), reverse=True)[:depth])
        asks = tuple(OrderBookLevel(p, q) for p, q in sorted(self._asks.items())[:depth])
        return bids, asks
