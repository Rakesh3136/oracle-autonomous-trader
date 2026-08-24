"""Attribute outcomes to market regime and strategy for explainable learning."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Attribution:
    trade_id: str
    regime: str
    strategy: str
    outcome_pnl: float
    success: bool
    contribution: str

class OutcomeAttributor:
    def attribute(self, trade_id: str, regime: str, strategy: str, pnl: float) -> Attribution:
        success = pnl > 0
        contribution = "positive" if pnl > 0 else "negative" if pnl < 0 else "neutral"
        return Attribution(trade_id, regime, strategy, pnl, success, contribution)
