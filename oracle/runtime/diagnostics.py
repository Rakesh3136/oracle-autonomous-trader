"""Deterministic startup diagnostics for the ORACLE runtime."""
from dataclasses import dataclass
from oracle.runtime.integration_health import IntegrationHealth
from oracle.runtime.paper_start import PaperStartup

@dataclass(frozen=True)
class DiagnosticReport:
    healthy: bool
    integration_ok: bool
    paper_start_ok: bool
    failures: tuple[str, ...]

class RuntimeDiagnostics:
    def run(self) -> DiagnosticReport:
        health = IntegrationHealth().check()
        startup = PaperStartup().start()
        failures = list(health.failures)
        if not startup.started:
            failures.append(startup.reason)
        return DiagnosticReport(
            healthy=not failures,
            integration_ok=health.healthy,
            paper_start_ok=startup.started,
            failures=tuple(failures),
        )
