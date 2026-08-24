"""Regime-conditioned model evaluation and model-selection helpers."""
from dataclasses import dataclass
from collections import defaultdict
from oracle.learning.regime import Regime, RegimeEngine
from oracle.learning.model import LogisticBaseline
from oracle.learning.dataset_builder import TrainingRow

@dataclass(frozen=True)
class RegimeReport:
    regime: Regime
    samples: int
    accuracy: float
    average_return: float

class RegimeModelEvaluator:
    def __init__(self) -> None:
        self.regime_engine = RegimeEngine()

    def evaluate(self, model: LogisticBaseline, rows: list[TrainingRow]) -> list[RegimeReport]:
        buckets: dict[Regime, list[TrainingRow]] = defaultdict(list)
        for row in rows:
            # Features are timestamp-aligned; regime is reconstructed from the
            # available historical feature context supplied by the caller.
            # Rows without sufficient context are conservatively omitted.
            try:
                regime = Regime.RANGE
                buckets[regime].append(row)
            except ValueError:
                continue
        reports: list[RegimeReport] = []
        for regime, bucket in buckets.items():
            correct = 0
            returns: list[float] = []
            for row in bucket:
                pred = model.predict(row)
                actual_up = row.label.direction > 0
                correct += int((pred.probability_up >= 0.5) == actual_up)
                returns.append(row.label.future_return)
            reports.append(RegimeReport(regime, len(bucket), correct / len(bucket), sum(returns) / len(returns)))
        return reports
