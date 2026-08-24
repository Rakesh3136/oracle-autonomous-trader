"""Chronological market replay primitives for end-to-end research tests."""
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Iterable

@dataclass(frozen=True)
class MarketTick:
    timestamp: datetime
    symbol: str
    price: float
    volume: float = 0.0

@dataclass(frozen=True)
class ReplayResult:
    ticks: int
    decisions: int
    errors: tuple[str, ...]

class MarketReplay:
    """Feeds historical ticks strictly in timestamp order; never looks ahead."""
    def run(self, ticks: Iterable[MarketTick], on_tick: Callable[[MarketTick], bool]) -> ReplayResult:
        ordered = list(ticks)
        ordered.sort(key=lambda x: x.timestamp)
        errors: list[str] = []
        decisions = 0
        previous: datetime | None = None
        for tick in ordered:
            if tick.price <= 0:
                errors.append(f"invalid price at {tick.timestamp.isoformat()}")
                continue
            if previous is not None and tick.timestamp < previous:
                errors.append("non-monotonic timestamp")
                continue
            previous = tick.timestamp
            try:
                if on_tick(tick):
                    decisions += 1
            except Exception as exc:  # noqa: BLE001 — replay must record any callback failure and continue.
                errors.append(f"tick handler error: {type(exc).__name__}")
        return ReplayResult(len(ordered), decisions, tuple(errors))
