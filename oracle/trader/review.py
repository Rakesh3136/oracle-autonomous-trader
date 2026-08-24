"""Post-trade review metrics for improving playbooks from observed outcomes."""
from collections import defaultdict
from dataclasses import dataclass

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
        buckets: dict[str, list[tuple[TradeRecord, float]]] = defaultdict(list)
        for record in records:
            if record.exit is not None and record.pnl is not None:
                buckets[record.setup].append((record, record.pnl))
        result: list[PlaybookStats] = []
        for setup, trades in sorted(buckets.items()):
            pnls = [pnl for _, pnl in trades]
            wins = sum(pnl > 0 for pnl in pnls)
            losses = sum(pnl < 0 for pnl in pnls)
            total = sum(pnls)
            result.append(
                PlaybookStats(setup, len(pnls), wins, losses, wins / len(pnls), total, total / len(pnls))
            )
        return result

    def best_setup(self, records: list[TradeRecord]) -> PlaybookStats | None:
        stats = self.summarize(records)
        return max(stats, key=lambda s: s.total_pnl, default=None)
