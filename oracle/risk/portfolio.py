"""Portfolio-level capital allocation and risk gates."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class PortfolioRiskConfig:
    risk_per_trade: float = 0.005
    max_portfolio_heat: float = 0.02
    max_leverage: float = 5.0
    max_daily_loss: float = 0.03
    max_position_notional_fraction: float = 0.25

@dataclass(frozen=True)
class PortfolioContext:
    equity: float
    current_heat: float = 0.0
    daily_pnl_fraction: float = 0.0
    existing_notional: float = 0.0

@dataclass(frozen=True)
class SizingDecision:
    approved: bool
    quantity: float
    notional: float
    reasons: tuple[str, ...]

class PortfolioRiskManager:
    def __init__(self, config: PortfolioRiskConfig | None = None) -> None:
        self.config = config or PortfolioRiskConfig()

    def size(self, context: PortfolioContext, entry: float, stop: float, leverage: float = 1.0) -> SizingDecision:
        reasons: list[str] = []
        if context.equity <= 0 or not isfinite(context.equity):
            return SizingDecision(False, 0.0, 0.0, ("invalid equity",))
        if entry <= 0 or stop <= 0 or entry == stop:
            return SizingDecision(False, 0.0, 0.0, ("invalid entry/stop",))
        if context.daily_pnl_fraction <= -self.config.max_daily_loss:
            reasons.append("daily loss limit reached")
        if context.current_heat >= self.config.max_portfolio_heat:
            reasons.append("portfolio heat limit reached")
        if leverage <= 0 or leverage > self.config.max_leverage:
            reasons.append("leverage limit exceeded")
        risk_per_unit = abs(entry - stop)
        risk_budget = context.equity * self.config.risk_per_trade
        quantity = risk_budget / risk_per_unit
        notional = quantity * entry
        max_notional = context.equity * self.config.max_position_notional_fraction * leverage
        quantity = min(quantity, max_notional / entry)
        notional = quantity * entry
        if context.existing_notional + notional > context.equity * self.config.max_position_notional_fraction * leverage:
            reasons.append("position notional limit reached")
        if notional <= 0:
            reasons.append("zero-sized position")
        return SizingDecision(not reasons, quantity if not reasons else 0.0, notional if not reasons else 0.0, tuple(reasons))
