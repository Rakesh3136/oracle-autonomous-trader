"""Trader Council: independent hypotheses, explicit disagreement, no order placement."""
from dataclasses import dataclass
from oracle.core.trader import Action
from oracle.market.models import MarketSnapshot
from oracle.strategies.base import Signal, Strategy

@dataclass(frozen=True)
class CouncilDecision:
    action: Action
    confidence: float
    consensus: float
    dissent: tuple[str, ...]
    signals: tuple[Signal, ...]

class TraderCouncil:
    def __init__(self, agents: list[Strategy]) -> None:
        self.agents = agents

    def deliberate(self, snapshot: MarketSnapshot) -> CouncilDecision:
        signals = tuple(agent.evaluate(snapshot) for agent in self.agents)
        active = [s for s in signals if s.action in (Action.LONG, Action.SHORT)]
        if not active:
            return CouncilDecision(Action.NO_TRADE, 0.0, 0.0, ("no directional consensus",), signals)
        long = sum(s.confidence for s in active if s.action is Action.LONG)
        short = sum(s.confidence for s in active if s.action is Action.SHORT)
        total = long + short
        if not total or long == short:
            return CouncilDecision(Action.NO_TRADE, 0.0, 0.0, ("directional disagreement",), signals)
        action = Action.LONG if long > short else Action.SHORT
        confidence = max(long, short) / total
        dissent = tuple(s.strategy for s in active if s.action is not action)
        return CouncilDecision(action, confidence, confidence, dissent, signals)
