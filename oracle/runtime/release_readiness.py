"""Single deterministic release gate for Testnet/live progression."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ReadinessChecklist:
    unit_tests: bool
    type_and_lint: bool
    walk_forward: bool
    stress_tests: bool
    paper_stability: bool
    testnet_stability: bool
    reconciliation: bool
    kill_switch: bool
    monitoring: bool
    secret_management: bool
    rollback: bool
    operator_approval: bool = False

@dataclass(frozen=True)
class ReadinessReport:
    ready_for_testnet: bool
    ready_for_live: bool
    failures: tuple[str, ...]

class ReleaseReadiness:
    def evaluate(self, checks: ReadinessChecklist) -> ReadinessReport:
        failures = tuple(name for name, value in checks.__dict__.items() if not value)
        testnet_required = ("unit_tests", "type_and_lint", "reconciliation", "kill_switch", "secret_management")
        live_required = tuple(checks.__dict__.keys())
        testnet_ready = all(getattr(checks, name) for name in testnet_required)
        live_ready = all(getattr(checks, name) for name in live_required)
        return ReadinessReport(testnet_ready, live_ready, failures)
