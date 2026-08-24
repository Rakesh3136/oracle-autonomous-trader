from dataclasses import dataclass
from oracle.core.trader import Action
from oracle.market.models import MarketSnapshot
from oracle.strategies.base import Signal, Strategy

@dataclass(frozen=True)
class EnsembleDecision:
    action: Action
    confidence: float
    signals: tuple[Signal, ...]

class StrategyEnsemble:
    def __init__(self, strategies: list[Strategy]) -> None:
        self.strategies = strategies

    def evaluate(self, snapshot: MarketSnapshot) -> EnsembleDecision:
        signals = tuple(s.evaluate(snapshot) for s in self.strategies)
        directional = [s for s in signals if s.action in {Action.LONG, Action.SHORT}]
        if not directional:
            return EnsembleDecision(Action.NO_TRADE, 0.0, signals)
        long_score = sum(s.confidence for s in directional if s.action is Action.LONG)
        short_score = sum(s.confidence for s in directional if s.action is Action.SHORT)
        total = long_score + short_score
        if total == 0 or long_score == short_score:
            return EnsembleDecision(Action.NO_TRADE, 0.0, signals)
        action = Action.LONG if long_score > short_score else Action.SHORT
        return EnsembleDecision(action, max(long_score, short_score) / total, signals)
