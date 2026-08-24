"""Deterministic price-protection decisions independent of AI confidence."""
from dataclasses import dataclass
from oracle.portfolio.lifecycle import TradePlan, PositionState

@dataclass(frozen=True)
class ProtectionDecision:
    action: str
    reason: str

class ProtectionEngine:
    def evaluate(self, trade: TradePlan, mark_price: float) -> ProtectionDecision:
        if trade.state not in {PositionState.OPEN, PositionState.PARTIAL}:
            return ProtectionDecision("hold", "trade is not active")
        if trade.side > 0 and mark_price <= trade.stop:
            return ProtectionDecision("stop", "long invalidation reached")
        if trade.side < 0 and mark_price >= trade.stop:
            return ProtectionDecision("stop", "short invalidation reached")
        if trade.side > 0 and mark_price >= trade.target:
            return ProtectionDecision("target", "long target reached")
        if trade.side < 0 and mark_price <= trade.target:
            return ProtectionDecision("target", "short target reached")
        return ProtectionDecision("hold", "no protection threshold reached")
