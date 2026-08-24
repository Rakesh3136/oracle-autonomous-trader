"""Deliberative trader council with explicit disagreement and regime context."""
from dataclasses import dataclass
from oracle.core.trader import Action
from oracle.intelligence.agents import Opinion, Specialist
from oracle.market.models import MarketSnapshot
from oracle.regime.classifier import RegimeAssessment

@dataclass(frozen=True)
class CouncilDecision:
    action: Action
    confidence: float
    consensus: float
    opinions: tuple[Opinion, ...]
    dissent: tuple[Opinion, ...]
    rationale: tuple[str, ...]

class TraderCouncil:
    def __init__(self, specialists: list[Specialist]) -> None:
        self.specialists = specialists

    def deliberate(self, snapshot: MarketSnapshot, regime: RegimeAssessment) -> CouncilDecision:
        opinions = tuple(s.evaluate(snapshot, regime) for s in self.specialists)
        directional = [o for o in opinions if o.action in {Action.LONG, Action.SHORT}]
        if not directional:
            return CouncilDecision(Action.NO_TRADE, 0.0, 1.0, opinions, (), ("no validated directional thesis",))
        long_score = sum(o.confidence for o in directional if o.action is Action.LONG)
        short_score = sum(o.confidence for o in directional if o.action is Action.SHORT)
        total = long_score + short_score
        if long_score == short_score or total == 0:
            return CouncilDecision(Action.NO_TRADE, 0.0, 0.0, opinions, tuple(directional), ("directional disagreement",))
        action = Action.LONG if long_score > short_score else Action.SHORT
        winners = tuple(o for o in directional if o.action is action)
        dissent = tuple(o for o in directional if o.action is not action)
        consensus = len(winners) / len(directional)
        confidence = max(o.confidence for o in winners) * consensus
        return CouncilDecision(action, confidence, consensus, opinions, dissent, tuple(o.thesis for o in winners))
