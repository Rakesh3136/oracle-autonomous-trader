"""Explicit deployment gate for progression from paper to Testnet/live.

The gate is intentionally conservative: mainnet remains denied unless every
required control is explicitly true and an operator provides a live approval.
"""
from dataclasses import dataclass
from enum import Enum

class DeploymentStage(str, Enum):
    PAPER = "paper"
    TESTNET = "testnet"
    SHADOW = "shadow"
    LIVE = "live"

@dataclass(frozen=True)
class GateChecklist:
    tests_passed: bool
    walk_forward_passed: bool
    paper_stable: bool
    reconciliation_verified: bool
    kill_switch_verified: bool
    operator_approved: bool

class LiveGate:
    def authorize(self, stage: DeploymentStage, checks: GateChecklist) -> bool:
        if stage is not DeploymentStage.LIVE:
            return True
        return all((checks.tests_passed, checks.walk_forward_passed,
                    checks.paper_stable, checks.reconciliation_verified,
                    checks.kill_switch_verified, checks.operator_approved))
