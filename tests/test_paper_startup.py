from oracle.runtime.integration_health import REQUIRED_MODULES, IntegrationHealth
from oracle.runtime.live_gate import DeploymentStage
from oracle.runtime.paper_start import PaperStartup


def test_integration_health_loads_required_runtime_modules() -> None:
    report = IntegrationHealth().check()
    assert report.healthy, report.failures
    assert all(report.checks[name] for name in REQUIRED_MODULES)


def test_paper_startup_is_connected_and_stays_in_paper_mode() -> None:
    startup = PaperStartup()
    result = startup.start()
    assert result.started
    assert result.stage is DeploymentStage.PAPER
    assert result.reason == "ORACLE paper runtime ready"


def test_paper_startup_runs_one_end_to_end_decision() -> None:
    closes = [100.0 + i * 0.5 for i in range(25)]
    approved, reason = PaperStartup().evaluate_once(
        "BTCUSDT", closes, 10_000.0, closes[-1], closes[-1] - 1.0
    )
    assert approved, reason
