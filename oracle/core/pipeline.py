"""Reference decision pipeline tying perception to deterministic risk."""
from dataclasses import dataclass
from oracle.core.trader import Action, TraderCore
from oracle.market.models import MarketSnapshot
from oracle.regime.classifier import RegimeClassifier
from oracle.risk.engine import RiskContext, RiskDecision, RiskEngine
from oracle.strategies.ensemble import StrategyEnsemble

@dataclass(frozen=True)
class Decision:
    action: Action
    confidence: float
    risk: RiskDecision
    reasons: tuple[str, ...]

class DecisionPipeline:
    def __init__(self, ensemble: StrategyEnsemble, risk: RiskEngine | None = None) -> None:
        self.trader = TraderCore()
        self.regime = RegimeClassifier()
        self.ensemble = ensemble
        self.risk = risk or RiskEngine()

    def evaluate(self, snapshot: MarketSnapshot, context: RiskContext) -> Decision:
        regime = self.regime.classify(snapshot)
        self.trader.observe(regime=regime.regime.value, evidence={"confidence": regime.confidence})
        decision = self.ensemble.evaluate(snapshot)
        signal = next((s for s in decision.signals if s.action is decision.action), None)
        evidence = signal.rationale if signal else ("ensemble produced no directional signal",)
        invalidation = signal.invalidation if signal else ()
        rr = signal.expected_reward_risk if signal else None
        thesis = self.trader.form_thesis(
            action=decision.action,
            confidence=decision.confidence,
            evidence=evidence,
            alternative="opposite regime or signal interpretation",
            invalidation=invalidation,
            expected_reward_risk=rr,
        )
        risk_result = self.risk.evaluate(thesis, context)
        return Decision(decision.action, decision.confidence, risk_result.decision, risk_result.reasons)
