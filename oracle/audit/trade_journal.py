"""Structured post-trade journal used by research and learning systems."""
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class TradeJournalEntry:
    trade_id: str
    symbol: str
    thesis: str
    entry_reason: str
    invalidation: str
    outcome_pnl: float
    max_adverse_excursion: float | None = None
    max_favorable_excursion: float | None = None
    execution_cost: float = 0.0
    notes: tuple[str, ...] = ()

class TradeJournal:
    def __init__(self) -> None:
        self.entries: list[TradeJournalEntry] = []

    def record(self, entry: TradeJournalEntry) -> None:
        self.entries.append(entry)

    def by_symbol(self, symbol: str) -> tuple[TradeJournalEntry, ...]:
        return tuple(e for e in self.entries if e.symbol == symbol)
