"""Append-only audit ledger for decisions, risk gates, execution and outcomes."""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json

@dataclass(frozen=True)
class AuditRecord:
    sequence: int
    timestamp: datetime
    event_type: str
    payload: dict[str, object]
    previous_hash: str
    record_hash: str

class AuditLedger:
    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def append(self, event_type: str, payload: dict[str, object]) -> AuditRecord:
        previous = self._records[-1].record_hash if self._records else "GENESIS"
        sequence = len(self._records) + 1
        timestamp = datetime.now(timezone.utc)
        canonical = json.dumps({"sequence": sequence, "timestamp": timestamp.isoformat(), "event_type": event_type, "payload": payload, "previous_hash": previous}, sort_keys=True, default=str)
        record_hash = hashlib.sha256(canonical.encode()).hexdigest()
        record = AuditRecord(sequence, timestamp, event_type, payload, previous, record_hash)
        self._records.append(record)
        return record

    def verify(self) -> bool:
        previous = "GENESIS"
        for record in self._records:
            canonical = json.dumps({"sequence": record.sequence, "timestamp": record.timestamp.isoformat(), "event_type": record.event_type, "payload": record.payload, "previous_hash": previous}, sort_keys=True, default=str)
            if hashlib.sha256(canonical.encode()).hexdigest() != record.record_hash:
                return False
            previous = record.record_hash
        return True

    def records(self) -> tuple[AuditRecord, ...]:
        return tuple(self._records)
