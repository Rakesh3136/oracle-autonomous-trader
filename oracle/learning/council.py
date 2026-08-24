"""Transparent multi-specialist council with disagreement-aware abstention."""
from dataclasses import dataclass
from oracle.learning.dataset_builder import TrainingRow
from oracle.learning.model import LogisticBaseline, Prediction

@dataclass(frozen=True)
class SpecialistVote:
    name: str
    prediction: Prediction
    weight: float

@dataclass(frozen=True)
class CouncilDecision:
    probability_up: float
    expected_return: float
    agreement: float
    confidence: float
    trade_allowed: bool
    reason: str

class TradingCouncil:
    def __init__(self) -> None:
        self.models: dict[str, LogisticBaseline] = {}

    def register(self, name: str, model: LogisticBaseline, weight: float = 1.0) -> None:
        if not name or weight <= 0:
            raise ValueError("name and positive weight are required")
        self.models[name] = model

    def decide(self, row: TrainingRow, min_confidence: float = 0.60,
               min_agreement: float = 0.60) -> CouncilDecision:
        votes: list[SpecialistVote] = []
        for name, model in self.models.items():
            try:
                votes.append(SpecialistVote(name, model.predict(row), 1.0))
            except RuntimeError:
                continue
        if not votes:
            return CouncilDecision(0.5, 0.0, 0.0, 0.0, False, "no trained specialists")
        total_weight = sum(v.weight for v in votes)
        probability = sum(v.prediction.probability_up * v.weight for v in votes) / total_weight
        expected = sum(v.prediction.expected_return * v.weight for v in votes) / total_weight
        bullish = sum(v.weight for v in votes if v.prediction.probability_up >= 0.5)
        bearish = total_weight - bullish
        agreement = max(bullish, bearish) / total_weight
        confidence = abs(probability - 0.5) * 2.0
        allowed = confidence >= min_confidence and agreement >= min_agreement
        reason = "council consensus" if allowed else "council disagreement or low confidence"
        return CouncilDecision(probability, expected, agreement, confidence, allowed, reason)
