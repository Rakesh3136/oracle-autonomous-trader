"""Regime-conditioned model evaluation and selection helpers."""
from dataclasses import dataclass
from collections import defaultdict
from oracle.learning.regime import Regime
from oracle.learning.model import LogisticBaseline
from oracle.learning.dataset_builder import TrainingRow

@dataclass(frozen=True)
class RegimeReport:
    regime: Regime
    samples: int
    accuracy: float
    average_return: float

class RegimeModelEvaluator:
    def evaluate(self, model: LogisticBaseline, rows: list[TrainingRow]) -> list[RegimeReport]:
        buckets: dict[Regime, list[TrainingRow]] = defaultdict(list)
        for row in rows:
            buckets[row.regime].append(row)
        reports: list[RegimeReport] = []
        for regime, bucket in sorted(buckets.items(), key=lambda item: item[0].value):
            correct = 0
            returns: list[float] = []
            for row in bucket:
                pred = model.predict(row)
                actual_up = row.label.direction > 0
                correct += int((pred.probability_up >= 0.5) == actual_up)
                returns.append(row.label.future_return)
            reports.append(RegimeReport(regime, len(bucket), correct / len(bucket), sum(returns) / len(returns)))
        return reports

    def weakest_regime(self, reports: list[RegimeReport]) -> RegimeReport | None:
        return min(reports, key=lambda r: (r.accuracy, r.average_return)) if reports else None
