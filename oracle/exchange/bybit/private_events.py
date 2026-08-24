"""Normalize private Bybit order, execution, position and wallet events."""
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class PrivateEvent:
    kind: str
    symbol: str
    timestamp: datetime
    payload: dict[str, object]

def normalize_private(topic: str, payload: dict[str, object]) -> PrivateEvent:
    raw_ts = payload.get("creationTime") or payload.get("ts")
    timestamp = datetime.now(timezone.utc)
    if isinstance(raw_ts, (int, float)):
        timestamp = datetime.fromtimestamp(raw_ts / 1000, tz=timezone.utc)
    data = payload.get("data")
    first = data[0] if isinstance(data, list) and data else data
    symbol = first.get("symbol", "") if isinstance(first, dict) else ""
    return PrivateEvent(topic, str(symbol), timestamp, payload)
