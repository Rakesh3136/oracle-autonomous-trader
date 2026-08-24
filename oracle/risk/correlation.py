"""Portfolio concentration and correlation-aware exposure checks."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Exposure:
    symbol: str
    notional: float
    beta_group: str

@dataclass(frozen=True)
class ConcentrationCheck:
    approved: bool
    group_notional: float
    limit: float
    reason: str

class ConcentrationGuard:
    def __init__(self, max_group_fraction: float = 0.40) -> None:
        if not 0 < max_group_fraction <= 1:
            raise ValueError("max_group_fraction must be in (0, 1]")
        self.max_group_fraction = max_group_fraction

    def check(self, equity: float, exposures: list[Exposure], candidate: Exposure) -> ConcentrationCheck:
        if equity <= 0 or candidate.notional < 0:
            return ConcentrationCheck(False, 0.0, 0.0, "invalid equity or exposure")
        group = sum(e.notional for e in exposures if e.beta_group == candidate.beta_group) + candidate.notional
        limit = equity * self.max_group_fraction
        if group > limit:
            return ConcentrationCheck(False, group, limit, "correlated exposure limit exceeded")
        return ConcentrationCheck(True, group, limit, "within concentration limit")
