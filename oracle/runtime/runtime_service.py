"""Fail-closed runtime composition for paper/Testnet operation."""
from dataclasses import dataclass

from oracle.runtime.live_gate import DeploymentStage, GateChecklist, LiveGate
from oracle.runtime.pipeline import TraderPipeline
from oracle.runtime.risk_gate import RuntimeRiskGate
from oracle.risk.correlation import Exposure
from oracle.risk.portfolio import PortfolioSnapshot


@dataclass(frozen=True)
class RuntimeResult:
    approved: bool
    reason: str


class OracleRuntime:
    def __init__(self) -> None:
        self.pipeline = TraderPipeline()
        self.risk = RuntimeRiskGate()
        self.live_gate = LiveGate()

    def evaluate(
        self,
        symbol: str,
        closes: list[float],
        equity: float,
        entry: float,
        stop: float,
        snapshot: PortfolioSnapshot,
        exposures: list[Exposure],
        beta_group: str,
        stage: DeploymentStage = DeploymentStage.PAPER,
    ) -> RuntimeResult:
        decision = self.pipeline.evaluate(symbol, closes, equity, entry, stop)
        if not decision.approved:
            return RuntimeResult(False, decision.reason)
        risk = self.risk.approve(
            equity, entry, stop, snapshot, exposures, symbol, beta_group
        )
        if not risk.approved:
            return RuntimeResult(False, risk.reason)
        checks = GateChecklist(False, False, stage is DeploymentStage.PAPER, False, False, False)
        if not self.live_gate.authorize(stage, checks):
            return RuntimeResult(False, "deployment gate not satisfied")
        return RuntimeResult(True, "intelligence and runtime risk gates passed")
