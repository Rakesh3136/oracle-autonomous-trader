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
    def __init__(self, min_trades: int = 30, max_drawdown: float = 0.20, min_return: float = 0.0) -> None:
        self.min_trades = min_trades
        self.max_drawdown = max_drawdown
        self.min_return = min_return

    def evaluate(self, name: str, net_return: float, max_drawdown: float, trades: int) -> ValidationReport:
        passed = trades >= self.min_trades and max_drawdown <= self.max_drawdown and net_return > self.min_return
        reason = "passed" if passed else "failed validation gate"
        return ValidationReport(name, passed, net_return, max_drawdown, trades, reason)
