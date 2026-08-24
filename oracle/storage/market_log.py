"""Append-only market event log abstraction for historical replay."""
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass(frozen=True)
class MarketLogRecord:
    timestamp: datetime
    event_type: str
    symbol: str
    payload: dict[str, object]

class MarketEventLog:
    def __init__(self) -> None:
        self.records: list[MarketLogRecord] = []

    def append(self, record: MarketLogRecord) -> None:
        self.records.append(record)

    def export_jsonl(self) -> str:
        return "\n".join(json.dumps({"timestamp": r.timestamp.isoformat(), "event_type": r.event_type, "symbol": r.symbol, "payload": r.payload}, sort_keys=True) for r in self.records)
