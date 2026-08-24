"""Validation gates for candidate strategies/models."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ValidationReport:
    name: str
    passed: bool
    net_return: float
    max_drawdown: float
    trades: int
    reason: str

class ValidationGate:
    def __init__(self, min_trades: int = 100, max_drawdown: float = 0.20, min_return: float = 0.0) -> None:
        self.min_trades = min_trades
        self.max_drawdown = max_drawdown
        self.min_return = min_return

    def evaluate(self, name: str, net_return: float, max_drawdown: float, trades: int) -> ValidationReport:
        reasons: list[str] = []
        if trades < self.min_trades:
            reasons.append("insufficient sample size")
        if net_return <= self.min_return:
            reasons.append("return threshold not met")
        if max_drawdown > self.max_drawdown:
            reasons.append("drawdown threshold exceeded")
        return ValidationReport(name, not reasons, net_return, max_drawdown, trades, "passed" if not reasons else "; ".join(reasons))
