"""Runtime gate composing position, portfolio, and concentration risk."""
from dataclasses import dataclass
from oracle.risk.position_sizing import PositionPlan, PositionSizer
from oracle.risk.portfolio import PortfolioRisk, PortfolioSnapshot
from oracle.risk.correlation import ConcentrationGuard, Exposure

@dataclass(frozen=True)
class RiskDecision:
    approved: bool
    position: PositionPlan | None
    reason: str

class RuntimeRiskGate:
    def __init__(self) -> None:
        self.sizer = PositionSizer()
        self.portfolio = PortfolioRisk()
        self.concentration = ConcentrationGuard()

    def approve(self, equity: float, entry: float, stop: float,
                snapshot: PortfolioSnapshot, exposures: list[Exposure],
                symbol: str, beta_group: str) -> RiskDecision:
        if not self.portfolio.evaluate(snapshot):
            return RiskDecision(False, None, self.portfolio.reason)
        try:
            plan = self.sizer.plan(equity, entry, stop)
        except ValueError as exc:
            return RiskDecision(False, None, str(exc))
        check = self.concentration.check(equity, exposures,
                                         Exposure(symbol, plan.notional, beta_group))
        if not check.approved:
            return RiskDecision(False, None, check.reason)
        return RiskDecision(True, plan, "all runtime risk gates passed")
