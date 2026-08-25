"""Single safe startup entry point for ORACLE paper mode."""
from dataclasses import dataclass

from oracle.risk.portfolio import PortfolioSnapshot
from oracle.runtime.integration_health import IntegrationHealth
from oracle.runtime.live_gate import DeploymentStage
from oracle.runtime.runtime_service import OracleRuntime


@dataclass(frozen=True)
class StartupResult:
    started: bool
    stage: DeploymentStage
    reason: str


class PaperStartup:
    def start(self) -> StartupResult:
        health = IntegrationHealth().check()
        if not health.healthy:
            return StartupResult(
                False,
                DeploymentStage.PAPER,
                "integration health failed: " + "; ".join(health.failures),
            )
        # Paper mode has no exchange credentials and cannot authorize mainnet.
        return StartupResult(True, DeploymentStage.PAPER, "ORACLE paper runtime ready")

    def evaluate_once(
        self,
        symbol: str,
        closes: list[float],
        equity: float,
        entry: float,
        stop: float,
    ) -> tuple[bool, str]:
        runtime = OracleRuntime()
        snapshot = PortfolioSnapshot(equity, 0.0, 0.0, 0.0, 0)
        result = runtime.evaluate(symbol, closes, equity, entry, stop, snapshot, [], "crypto")
        return result.approved, result.reason
