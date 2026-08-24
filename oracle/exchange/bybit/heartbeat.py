"""Heartbeat and staleness detection for streaming market data."""
from dataclasses import dataclass
from time import monotonic

@dataclass(frozen=True)
class HeartbeatStatus:
    healthy: bool
    age_seconds: float

class HeartbeatMonitor:
    def __init__(self, max_age_seconds: float = 15.0) -> None:
        self.max_age_seconds = max_age_seconds
        self.last_message: float | None = None

    def mark_message(self) -> None:
        self.last_message = monotonic()

    def status(self) -> HeartbeatStatus:
        if self.last_message is None:
            return HeartbeatStatus(False, float("inf"))
        age = monotonic() - self.last_message
        return HeartbeatStatus(age <= self.max_age_seconds, age)
