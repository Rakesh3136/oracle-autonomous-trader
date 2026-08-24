"""Integration health checks for ORACLE runtime dependencies."""
from dataclasses import dataclass
from importlib import import_module

@dataclass(frozen=True)
class HealthReport:
    healthy: bool
    checks: dict[str, bool]
    failures: tuple[str, ...]

REQUIRED_MODULES = (
    "oracle.runtime.pipeline",
    "oracle.runtime.risk_gate",
    "oracle.execution.order_intent",
    "oracle.execution.state_machine",
    "oracle.execution.coordinator",
    "oracle.execution.simulator",
    "oracle.backtest.replay",
    "oracle.backtest.analytics",
)

class IntegrationHealth:
    def check(self) -> HealthReport:
        checks: dict[str, bool] = {}
        failures: list[str] = []
        for name in REQUIRED_MODULES:
            try:
                import_module(name)
                checks[name] = True
            except Exception as exc:
                checks[name] = False
                failures.append(f"{name}: {type(exc).__name__}")
        return HealthReport(not failures, checks, tuple(failures))
