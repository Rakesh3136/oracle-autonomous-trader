"""Deterministic risk gate.

The risk engine is intentionally independent of the AI layer. A proposed
trade can be rejected regardless of model confidence.
"""

from dataclasses import dataclass
from enum import StrEnum

from oracle.core.trader import Action, Thesis


class RiskDecision(StrEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


@dataclass(frozen=True)
class RiskLimits:
    max_position_notional: float = 1_000.0
    max_daily_loss: float = 100.0
    max_drawdown: float = 0.10
    max_leverage: float = 3.0
    min_reward_risk: float = 1.5


@dataclass(frozen=True)
class RiskContext:
    equity: float
    daily_pnl: float
    drawdown: float
    proposed_notional: float
    leverage: float


@dataclass(frozen=True)
class RiskResult:
    decision: RiskDecision
    reasons: tuple[str, ...]


class RiskEngine:
    """Hard risk boundary between AI proposals and execution."""

    def __init__(self, limits: RiskLimits | None = None) -> None:
        self.limits = limits or RiskLimits()

    def evaluate(self, thesis: Thesis, context: RiskContext) -> RiskResult:
        reasons: list[str] = []

        if context.equity <= 0:
            reasons.append("non-positive equity")
        if context.daily_pnl <= -self.limits.max_daily_loss:
            reasons.append("daily loss limit reached")
        if context.drawdown >= self.limits.max_drawdown:
            reasons.append("maximum drawdown reached")
        if context.proposed_notional > self.limits.max_position_notional:
            reasons.append("position notional exceeds limit")
        if context.leverage > self.limits.max_leverage:
            reasons.append("leverage exceeds limit")
        if (
            thesis.action in {Action.LONG, Action.SHORT}
            and thesis.expected_reward_risk is not None
            and thesis.expected_reward_risk < self.limits.min_reward_risk
        ):
            reasons.append("expected reward/risk below minimum")

        if thesis.action == Action.NO_TRADE:
            reasons.append("strategy explicitly selected no-trade")

        return RiskResult(
            decision=RiskDecision.REJECT if reasons else RiskDecision.APPROVE,
            reasons=tuple(reasons),
        )
