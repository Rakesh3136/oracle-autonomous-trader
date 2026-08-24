"""Post-trade review metrics for improving playbooks from observed outcomes."""
from dataclasses import dataclass
from collections import defaultdict
from oracle.trader.journal import TradeRecord

@dataclass(frozen=True)
class PlaybookStats:
    setup: str
    trades: int
    wins: int
    losses: int
    win_rate: float
    total_pnl: float
    average_pnl: float

class TradeReviewEngine:
    def summarize(self, records: list[TradeRecord]) -> list[PlaybookStats]:
        buckets: dict[str, list[TradeRecord]] = defaultdict(list)
        for record in records:
            if record.exit is not None and record.pnl is not None:
                buckets[record.setup].append(record)
        result: list[PlaybookStats] = []
        for setup, trades in sorted(buckets.items()):
            wins = sum(t.pnl > 0 for t in trades)
            losses = sum(t.pnl < 0 for t in trades)
            total = sum(t.pnl for t in trades)
            result.append(PlaybookStats(setup, len(trades), wins, losses,
                                        wins / len(trades), total, total / len(trades)))
        return result

    def best_setup(self, records: list[TradeRecord]) -> PlaybookStats | None:
        stats = self.summarize(records)
        return max(stats, key=lambda s: s.total_pnl, default=None)
