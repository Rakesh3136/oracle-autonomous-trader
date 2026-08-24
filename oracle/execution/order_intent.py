"""Exchange-agnostic order intent and idempotency primitives.

An intent describes what execution should attempt. It is deliberately separate
from any Bybit client so research, paper trading, and live adapters share the
same safety contract.
"""
from dataclasses import dataclass
from enum import Enum
import hashlib

class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"

@dataclass(frozen=True)
class OrderIntent:
    intent_id: str
    symbol: str
    side: Side
    order_type: OrderType
    quantity: float
    limit_price: float | None = None
    reduce_only: bool = False

    @staticmethod
    def make(symbol: str, side: Side, order_type: OrderType, quantity: float,
            limit_price: float | None = None, reduce_only: bool = False) -> "OrderIntent":
        if not symbol or quantity <= 0:
            raise ValueError("symbol and positive quantity are required")
        if order_type is OrderType.LIMIT and (limit_price is None or limit_price <= 0):
            raise ValueError("limit orders require a positive limit_price")
        material = f"{symbol}|{side.value}|{order_type.value}|{quantity:.12g}|{limit_price}|{reduce_only}"
        intent_id = hashlib.sha256(material.encode()).hexdigest()
        return OrderIntent(intent_id, symbol, side, order_type, quantity, limit_price, reduce_only)

class IntentRegistry:
    def __init__(self) -> None:
        self._submitted: set[str] = set()

    def seen(self, intent_id: str) -> bool:
        return intent_id in self._submitted

    def mark_submitted(self, intent_id: str) -> None:
        self._submitted.add(intent_id)
