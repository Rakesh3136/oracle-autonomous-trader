"""Fail-closed position sizing primitives.

Calculates a maximum position from explicit account risk and stop distance.
It never decides whether a trade should exist; the thesis/risk gates do that.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class RiskLimits:
    risk_fraction: float = 0.005
    max_notional_fraction: float = 0.10
    max_leverage: float = 3.0

@dataclass(frozen=True)
class PositionPlan:
    quantity: float
    notional: float
    risk_amount: float
    leverage: float

class PositionSizer:
    def __init__(self, limits: RiskLimits | None = None) -> None:
        self.limits = limits or RiskLimits()
        if not (0 < self.limits.risk_fraction <= 1):
            raise ValueError("risk_fraction must be in (0, 1]")
        if not (0 < self.limits.max_notional_fraction <= 1):
            raise ValueError("max_notional_fraction must be in (0, 1]")
        if self.limits.max_leverage <= 0:
            raise ValueError("max_leverage must be positive")

    def plan(self, equity: float, entry: float, stop: float, price: float | None = None) -> PositionPlan:
        if equity <= 0 or entry <= 0 or stop <= 0:
            raise ValueError("equity, entry and stop must be positive")
        distance = abs(entry - stop)
        if distance == 0:
            raise ValueError("stop must differ from entry")
        risk_amount = equity * self.limits.risk_fraction
        quantity = risk_amount / distance
        notional = quantity * (price or entry)
        max_notional = equity * self.limits.max_notional_fraction * self.limits.max_leverage
        if notional > max_notional:
            notional = max_notional
            quantity = notional / (price or entry)
            risk_amount = quantity * distance
        leverage = notional / equity
        return PositionPlan(quantity, notional, risk_amount, leverage)
