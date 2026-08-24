"""Opportunity ranking that explicitly allows no-trade outcomes."""
from dataclasses import dataclass
from oracle.core.trader import Action
from oracle.intelligence.council import CouncilDecision

@dataclass(frozen=True)
class Opportunity:
    symbol: str
    action: Action
    score: float
    confidence: float
    consensus: float
    expected_reward_risk: float | None
    reasons: tuple[str, ...]

class OpportunityRanker:
    def rank(self, symbol: str, decision: CouncilDecision) -> Opportunity:
        rr = max((o.expected_reward_risk or 0.0) for o in decision.opinions if o.action is decision.action) if decision.action is not Action.NO_TRADE else 0.0
        score = decision.confidence * decision.consensus * min(rr / 3.0, 1.0)
        if decision.action is Action.NO_TRADE or score < 0.25:
            return Opportunity(symbol, Action.NO_TRADE, score, decision.confidence, decision.consensus, rr or None, decision.rationale + ("opportunity quality below threshold",))
        return Opportunity(symbol, decision.action, score, decision.confidence, decision.consensus, rr or None, decision.rationale)

    def best(self, opportunities: list[Opportunity]) -> Opportunity | None:
        viable = [o for o in opportunities if o.action is not Action.NO_TRADE]
        return max(viable, key=lambda o: o.score) if viable else None
