"""Post-trade evaluation and bounded learning candidates.

This layer proposes changes; it does not mutate live strategy parameters.
"""
from dataclasses import dataclass
from collections import defaultdict
from oracle.audit.trade_journal import TradeJournalEntry

@dataclass(frozen=True)
class StrategyStats:
    trades: int
    wins: int
    losses: int
    total_pnl: float
    win_rate: float
    average_pnl: float

@dataclass(frozen=True)
class LearningCandidate:
    dimension: str
    key: str
    observation: str
    evidence_count: int
    proposed_action: str

class LearningEvaluator:
    def summarize(self, entries: list[TradeJournalEntry]) -> dict[str, StrategyStats]:
        grouped: dict[str, list[TradeJournalEntry]] = defaultdict(list)
        for entry in entries:
            grouped[entry.symbol].append(entry)
        result: dict[str, StrategyStats] = {}
        for key, trades in grouped.items():
            wins = sum(1 for t in trades if t.outcome_pnl > 0)
            pnl = sum(t.outcome_pnl for t in trades)
            result[key] = StrategyStats(len(trades), wins, len(trades) - wins, pnl, wins / len(trades), pnl / len(trades))
        return result

    def candidates(self, entries: list[TradeJournalEntry], min_samples: int = 20) -> tuple[LearningCandidate, ...]:
        stats = self.summarize(entries)
        candidates: list[LearningCandidate] = []
        for symbol, s in stats.items():
            if s.trades >= min_samples and s.win_rate < 0.40:
                candidates.append(LearningCandidate("symbol", symbol, "observed weak historical outcome rate", s.trades, "review or downweight in research"))
        return tuple(candidates)
