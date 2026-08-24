"""Controlled research experiment records."""
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Experiment:
    experiment_id: str
    hypothesis: str
    train_start: datetime
    train_end: datetime
    validation_start: datetime
    validation_end: datetime

@dataclass(frozen=True)
class ExperimentResult:
    experiment_id: str
    net_return: float
    max_drawdown: float
    sharpe: float
    passed: bool

class ResearchGate:
    """Conservative promotion gate; production changes require validation evidence."""
    def __init__(self, min_sharpe: float = 0.5, max_drawdown: float = 0.20) -> None:
        self.min_sharpe = min_sharpe
        self.max_drawdown = max_drawdown

    def passes(self, result: ExperimentResult) -> bool:
        return result.passed and result.sharpe >= self.min_sharpe and result.max_drawdown <= self.max_drawdown
