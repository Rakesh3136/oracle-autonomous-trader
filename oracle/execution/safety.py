"""Production-oriented execution safety primitives.

These guards are deliberately deterministic and independent of AI output.
"""
from dataclasses import dataclass
from time import monotonic

@dataclass(frozen=True)
class ExecutionLimits:
    max_order_notional: float = 1_000.0
    max_orders_per_minute: int = 10
    live_enabled: bool = False

class ExecutionGuard:
    def __init__(self, limits: ExecutionLimits | None = None) -> None:
        self.limits = limits or ExecutionLimits()
        self._timestamps: list[float] = []

    def authorize(self, notional: float) -> tuple[bool, tuple[str, ...]]:
        reasons: list[str] = []
        now = monotonic()
        self._timestamps = [t for t in self._timestamps if now - t < 60]
        if not self.limits.live_enabled:
            reasons.append("live execution disabled")
        if notional <= 0:
            reasons.append("order notional must be positive")
        if notional > self.limits.max_order_notional:
            reasons.append("order notional exceeds execution limit")
        if len(self._timestamps) >= self.limits.max_orders_per_minute:
            reasons.append("order rate limit reached")
        if not reasons:
            self._timestamps.append(now)
        return not reasons, tuple(reasons)
