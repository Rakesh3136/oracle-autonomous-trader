from dataclasses import dataclass
from datetime import datetime
from oracle.core.trader import Action

@dataclass(frozen=True)
class TradeJournalEntry:
    timestamp: datetime
    symbol: str
    action: Action
    thesis: str
    outcome_pnl: float | None = None
    notes: str = ""

class TradeJournal:
    def __init__(self) -> None:
        self.entries: list[TradeJournalEntry] = []

    def record(self, entry: TradeJournalEntry) -> None:
        self.entries.append(entry)

    def outcomes(self) -> list[float]:
        return [e.outcome_pnl for e in self.entries if e.outcome_pnl is not None]
