"""Normalization boundary for exchange websocket messages."""
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class NormalizedEvent:
    event_type: str
    symbol: str
    timestamp: datetime
    data: dict[str, object]

def normalize_topic(topic: str, payload: dict[str, object]) -> NormalizedEvent:
    parts = topic.split(".")
    event_type = parts[0] if parts else "unknown"
    symbol = parts[-1] if len(parts) > 1 else ""
    raw_ts = payload.get("ts")
    timestamp = datetime.now(timezone.utc)
    if isinstance(raw_ts, (int, float)):
        timestamp = datetime.fromtimestamp(raw_ts / 1000, tz=timezone.utc)
    return NormalizedEvent(event_type, symbol, timestamp, payload)
