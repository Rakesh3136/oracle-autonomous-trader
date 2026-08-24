"""Post-trade and out-of-sample model evaluation.

Evaluation can propose a champion candidate, but it never mutates live strategy
parameters or authorizes live execution.
"""
from dataclasses import dataclass
from collections import defaultdict
from oracle.audit.trade_journal import TradeJournalEntry
from oracle.learning.model import LogisticBaseline
from oracle.learning.dataset_builder import TrainingRow

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

@dataclass(frozen=True)
class ModelReport:
    accuracy: float
    directional_brier: float
    average_return_when_correct: float
    samples: int

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
        return tuple(LearningCandidate("symbol", symbol, "observed weak historical outcome rate", s.trades, "review or downweight in research")
                     for symbol, s in stats.items() if s.trades >= min_samples and s.win_rate < 0.40)

class ModelEvaluator:
    def evaluate(self, model: LogisticBaseline, rows: list[TrainingRow]) -> ModelReport:
        if not rows:
            raise ValueError("cannot evaluate empty data")
        correct = 0
        brier = 0.0
        returns: list[float] = []
        for row in rows:
            prediction = model.predict(row)
            actual = 1.0 if row.label.direction > 0 else 0.0
            is_correct = (prediction.probability_up >= 0.5) == (actual == 1.0)
            correct += int(is_correct)
            brier += (prediction.probability_up - actual) ** 2
            if is_correct:
                returns.append(row.label.future_return)
        return ModelReport(correct / len(rows), brier / len(rows), sum(returns) / len(returns) if returns else 0.0, len(rows))

class ChampionSelector:
    def select(self, current: ModelReport | None, candidate: ModelReport) -> bool:
        if current is None:
            return candidate.samples > 0
        return (candidate.directional_brier < current.directional_brier and
                candidate.average_return_when_correct >= current.average_return_when_correct and
                candidate.samples >= current.samples)
