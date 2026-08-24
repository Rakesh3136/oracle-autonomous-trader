"""Regime-specific specialist models and a conservative meta-controller."""
from dataclasses import dataclass
from oracle.learning.model import LogisticBaseline, Prediction
from oracle.learning.regime import Regime
from oracle.learning.dataset_builder import TrainingRow

@dataclass(frozen=True)
class SpecialistDecision:
    regime: Regime
    prediction: Prediction
    confidence: float
    trade_allowed: bool

class RegimeSpecialist:
    def __init__(self, regime: Regime) -> None:
        self.regime = regime
        self.model = LogisticBaseline()
        self.trained = False

    def fit(self, rows: list[TrainingRow]) -> None:
        if not rows:
            raise ValueError(f"no training rows for {self.regime.value}")
        self.model.fit(rows)
        self.trained = True

    def predict(self, row: TrainingRow, min_confidence: float = 0.55) -> SpecialistDecision:
        if not self.trained:
            raise RuntimeError("specialist is not trained")
        prediction = self.model.predict(row)
        confidence = abs(prediction.probability_up - 0.5) * 2.0
        return SpecialistDecision(self.regime, prediction, confidence, confidence >= min_confidence)

class MetaController:
    """Routes to the specialist matching the observed regime; otherwise abstains."""
    def __init__(self) -> None:
        self.specialists = {regime: RegimeSpecialist(regime) for regime in Regime}

    def fit(self, rows: list[TrainingRow]) -> None:
        buckets = {regime: [] for regime in Regime}
        for row in rows:
            buckets[row.regime].append(row)
        for regime, bucket in buckets.items():
            if bucket:
                self.specialists[regime].fit(bucket)

    def decide(self, row: TrainingRow, min_confidence: float = 0.55) -> SpecialistDecision | None:
        specialist = self.specialists.get(row.regime)
        if specialist is None or not specialist.trained:
            return None
        decision = specialist.predict(row, min_confidence)
        return decision if decision.trade_allowed else None
