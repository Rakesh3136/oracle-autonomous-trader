"""Server clock synchronization primitives for signed exchange requests."""
from dataclasses import dataclass
from time import time

@dataclass(frozen=True)
class ClockOffset:
    milliseconds: int = 0

class ServerClock:
    def __init__(self) -> None:
        self.offset = ClockOffset()

    def update(self, server_timestamp_ms: int) -> None:
        local_ms = int(time() * 1000)
        self.offset = ClockOffset(server_timestamp_ms - local_ms)

    def now_ms(self) -> int:
        return int(time() * 1000) + self.offset.milliseconds
