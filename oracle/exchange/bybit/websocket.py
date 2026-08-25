"""Exchange-agnostic WebSocket lifecycle primitives for Bybit streams.

The transport implementation is intentionally injectable: production deployments
can provide an asyncio WebSocket client while tests use a deterministic fake.
"""
from dataclasses import dataclass
from time import monotonic


@dataclass(frozen=True)
class StreamEvent:
    channel: str
    symbol: str
    received_at: float
    payload: dict[str, object]


class StreamSupervisor:
    def __init__(self, reconnect_delay: float = 2.0, max_reconnect_delay: float = 30.0) -> None:
        self.reconnect_delay = reconnect_delay
        self.max_reconnect_delay = max_reconnect_delay
        self._attempts = 0
        self.last_message_at: float | None = None

    def connected(self) -> None:
        self._attempts = 0

    def disconnected(self) -> float:
        self._attempts += 1
        exponent: float = 2.0 ** max(0, self._attempts - 1)
        delay: float = self.reconnect_delay * exponent
        return self.max_reconnect_delay if delay > self.max_reconnect_delay else delay

    def received(self) -> None:
        self.last_message_at = monotonic()
