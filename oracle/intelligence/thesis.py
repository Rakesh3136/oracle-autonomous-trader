"""Explicit trade-thesis construction from council evidence.

A thesis is an auditable hypothesis, not an order. Execution must separately
validate risk, liquidity, price, and environment constraints.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

class Direction(str, Enum):
    LONG = "long"
    SHORT = "short"
    NONE = "none"

@dataclass(frozen=True)
class TradeThesis:
    symbol: str
    direction: Direction
    thesis: str
    catalyst: str
    entry_low: float | None
    entry_high: float | None
    invalidation: float | None
    target: float | None
    expected_value: float | None
    confidence: float
    quality: float
    expires_at: datetime

class ThesisEngine:
    def build(self, symbol: str, direction: Direction, rationale: str, confidence: float,
              entry_low: float | None = None, entry_high: float | None = None,
              invalidation: float | None = None, target: float | None = None,
              expected_value: float | None = None, ttl_seconds: int = 300) -> TradeThesis:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        confidence = min(1.0, max(0.0, confidence))
        quality = confidence
        return TradeThesis(
            symbol=symbol,
            direction=direction,
            thesis=rationale,
            catalyst="council evidence",
            entry_low=entry_low,
            entry_high=entry_high,
            invalidation=invalidation,
            target=target,
            expected_value=expected_value,
            confidence=confidence,
            quality=quality,
            expires_at=datetime.now(timezone.utc).replace(microsecond=0) + __import__('datetime').timedelta(seconds=ttl_seconds),
        )

    @staticmethod
    def is_expired(thesis: TradeThesis, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        return current >= thesis.expires_at
