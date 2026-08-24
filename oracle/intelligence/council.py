"""Multi-agent trader council: independent opinions plus explicit dissent."""
from dataclasses import dataclass
from oracle.core.trader import Action
from oracle.market.models import MarketSnapshot
from oracle.strategies.base import Signal, Strategy

@dataclass(frozen=True)
class CouncilDecision:
    action: Action
    confidence: float
    consensus: float
    signals: tuple[Signal, ...]
    dissent: tuple[str, ...]

class TraderCouncil:
    def __init__(self, agents: list[Strategy]) -> None:
        self.agents = agents

    def deliberate(self, snapshot: MarketSnapshot) -> CouncilDecision:
        signals = tuple(agent.evaluate(snapshot) for agent in self.agents)
        directional = [s for s in signals if s.action in {Action.LONG, Action.SHORT}]
        if not directional:
            return CouncilDecision(Action.NO_TRADE, 0.0, 0.0, signals, tuple(s.strategy for s in signals))
        long = sum(s.confidence for s in directional if s.action is Action.LONG)
        short = sum(s.confidence for s in directional if s.action is Action.SHORT)
        total = long + short
        if long == short:
            return CouncilDecision(Action.NO_TRADE, 0.0, 0.0, signals, tuple(s.strategy for s in directional))
        action = Action.LONG if long > short else Action.SHORT
        winning = max(long, short)
        dissent = tuple(s.strategy for s in directional if s.action is not action)
        return CouncilDecision(action, winning / total, winning / total, signals, dissent)
