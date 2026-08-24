"""Deterministic market features used by regime and strategy layers."""

from collections.abc import Sequence
from math import sqrt

from oracle.market.models import Candle, OrderBook


def returns(candles: Sequence[Candle]) -> float | None:
    if len(candles) < 2:
        return None
    previous = candles[-2].close
    if previous <= 0:
        return None
    return candles[-1].close / previous - 1.0


def realized_volatility(candles: Sequence[Candle], window: int = 20) -> float | None:
    if window < 2 or len(candles) < window + 1:
        return None
    values = [c.close / candles[i - 1].close - 1.0 for i, c in enumerate(candles[-window:], start=len(candles) - window)]
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return sqrt(variance)


def order_book_imbalance(book: OrderBook, depth: int = 10) -> float | None:
    bids = sum(level.quantity for level in book.bids[:depth])
    asks = sum(level.quantity for level in book.asks[:depth])
    total = bids + asks
    if total == 0:
        return None
    return (bids - asks) / total
