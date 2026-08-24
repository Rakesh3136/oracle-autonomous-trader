"""Deterministic autonomous runtime coordinator.

Dependencies are injected so paper/testnet/live transports can be tested separately.
"""
from dataclasses import dataclass
from time import monotonic
from collections.abc import Callable

@dataclass(frozen=True)
class RuntimeHealth:
    running: bool
    last_market_event_age: float
    safe: bool
    reason: str

class AutonomousLoop:
    def __init__(self, stale_after_seconds: float = 15.0) -> None:
        self.stale_after_seconds = stale_after_seconds
        self._last_market_event = monotonic()
        self._running = False
        self._safe = True
        self._reason = "initialized"

    def market_event_received(self) -> None:
        self._last_market_event = monotonic()

    def start(self) -> None:
        self._running = True
        self._safe = True
        self._reason = "running"

    def stop(self, reason: str = "operator stop") -> None:
        self._running = False
        self._safe = False
        self._reason = reason

    def health(self) -> RuntimeHealth:
        age = monotonic() - self._last_market_event
        safe = self._safe and age <= self.stale_after_seconds
        reason = self._reason if safe else "stale market data"
        return RuntimeHealth(self._running, age, safe, reason)

    def tick(self, cycle: Callable[[], None]) -> RuntimeHealth:
        health = self.health()
        if not health.running or not health.safe:
            return health
        cycle()
        return self.health()
