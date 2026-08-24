"""Small persistence abstraction; production DB adapters can implement this contract."""
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class StoredEvent:
    event_id: str
    timestamp: datetime
    kind: str
    payload: dict[str, object]

class EventRepository:
    def __init__(self) -> None:
        self._events: dict[str, StoredEvent] = {}

    def append(self, event: StoredEvent) -> None:
        if event.event_id in self._events:
            raise ValueError(f"duplicate event: {event.event_id}")
        self._events[event.event_id] = event

    def get(self, event_id: str) -> StoredEvent | None:
        return self._events.get(event_id)

    def all(self) -> tuple[StoredEvent, ...]:
        return tuple(self._events.values())
