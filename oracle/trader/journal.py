"""Structured trade journal for post-trade review and future learning."""
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class TradeRecord:
    trade_id: str
    symbol: str
    setup: str
    direction: str
    thesis: str
    entry: float
    invalidation: float
    target: float
    exit: float | None
    pnl: float | None
    outcome: str
    opened_at: str
    closed_at: str | None

class TradeJournal:
    def __init__(self) -> None:
        self._records: dict[str, TradeRecord] = {}

    def record_open(self, trade_id: str, symbol: str, setup: str, direction: str,
                    thesis: str, entry: float, invalidation: float, target: float) -> TradeRecord:
        if trade_id in self._records:
            raise ValueError("trade_id already exists")
        if entry <= 0 or invalidation <= 0 or target <= 0:
            raise ValueError("prices must be positive")
        record = TradeRecord(trade_id, symbol, setup, direction, thesis, entry,
                             invalidation, target, None, None, "OPEN",
                             datetime.now(timezone.utc).isoformat(), None)
        self._records[trade_id] = record
        return record

    def record_close(self, trade_id: str, exit_price: float, pnl: float) -> TradeRecord:
        record = self._records[trade_id]
        if record.exit is not None:
            raise ValueError("trade is already closed")
        outcome = "WIN" if pnl > 0 else "LOSS" if pnl < 0 else "FLAT"
        closed = TradeRecord(**{**record.__dict__, "exit": exit_price, "pnl": pnl,
                                "outcome": outcome,
                                "closed_at": datetime.now(timezone.utc).isoformat()})
        self._records[trade_id] = closed
        return closed

    def all_records(self) -> tuple[TradeRecord, ...]:
        return tuple(self._records.values())
