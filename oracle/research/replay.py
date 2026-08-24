"""Deterministic event replay for market research."""
from dataclasses import dataclass
from collections.abc import Iterable
from oracle.market.models import Candle

@dataclass(frozen=True)
class ReplayEvent:
    timestamp: object
    candle: Candle

class ReplayEngine:
    def replay(self, candles: Iterable[Candle]) -> tuple[ReplayEvent, ...]:
        ordered = sorted(candles, key=lambda c: c.timestamp)
        return tuple(ReplayEvent(c.timestamp, c) for c in ordered)
