"""Final deployment gate: live trading is impossible until every safety gate passes."""
from dataclasses import dataclass
from enum import Enum

class DeploymentStage(str, Enum):
    DEVELOPMENT = "development"
    PAPER = "paper"
    TESTNET = "testnet"
    LIVE = "live"

@dataclass(frozen=True)
class ReadinessReport:
    stage: DeploymentStage
    tests_passed: bool
    validation_passed: bool
    testnet_passed: bool
    reconciliation_passed: bool
    risk_controls_passed: bool
    security_passed: bool
    explicit_human_approval: bool

    @property
    def live_authorized(self) -> bool:
        return all((self.tests_passed, self.validation_passed, self.testnet_passed,
                    self.reconciliation_passed, self.risk_controls_passed,
                    self.security_passed, self.explicit_human_approval)) and self.stage == DeploymentStage.LIVE

class FinalReadinessGate:
    def evaluate(self, report: ReadinessReport) -> bool:
        return report.live_authorized
