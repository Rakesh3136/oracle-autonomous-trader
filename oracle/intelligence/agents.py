"""Specialist trader agents with explicit, auditable opinions."""
from dataclasses import dataclass
from abc import ABC, abstractmethod
from oracle.core.trader import Action
from oracle.market.models import MarketSnapshot
from oracle.regime.classifier import RegimeAssessment

@dataclass(frozen=True)
class Opinion:
    specialist: str
    action: Action
    confidence: float
    thesis: str
    evidence: tuple[str, ...]
    invalidation: tuple[str, ...]
    expected_reward_risk: float | None = None

class Specialist(ABC):
    name: str
    @abstractmethod
    def evaluate(self, snapshot: MarketSnapshot, regime: RegimeAssessment) -> Opinion: ...

class TrendSpecialist(Specialist):
    name = "trend"
    def evaluate(self, snapshot, regime):
        if regime.regime.value == "bull_trend":
            return Opinion(self.name, Action.LONG, regime.confidence, "trend continuation", regime.reasons, ("trend regime invalidated",), 2.0)
        if regime.regime.value == "bear_trend":
            return Opinion(self.name, Action.SHORT, regime.confidence, "trend continuation", regime.reasons, ("trend regime invalidated",), 2.0)
        return Opinion(self.name, Action.NO_TRADE, 0.2, "no directional trend", regime.reasons, ())

class MeanReversionSpecialist(Specialist):
    name = "mean_reversion"
    def evaluate(self, snapshot, regime):
        if regime.regime.value == "range":
            return Opinion(self.name, Action.NO_TRADE, 0.4, "range requires location context", regime.reasons, ())
        return Opinion(self.name, Action.NO_TRADE, 0.2, "no validated mean-reversion setup", regime.reasons, ())

class VolatilitySpecialist(Specialist):
    name = "volatility"
    def evaluate(self, snapshot, regime):
        if regime.regime.value == "high_volatility":
            return Opinion(self.name, Action.NO_TRADE, regime.confidence, "volatility regime requires defensive sizing", regime.reasons, ())
        return Opinion(self.name, Action.NO_TRADE, 0.2, "volatility not extreme", regime.reasons, ())
