from oracle.runtime.pipeline import TraderPipeline
from oracle.runtime.paper_runner import PaperRunner


def test_pipeline_fails_closed_on_bad_input():
    result = TraderPipeline().evaluate("BTCUSDT", [100.0] * 5, 10000.0, 100.0, 99.0)
    assert not result.approved


def test_paper_runner_does_not_need_exchange_credentials():
    closes = [100.0 + i * 0.5 for i in range(25)]
    result = PaperRunner(slippage_bps=1.0).run_once("BTCUSDT", closes, 10000.0, closes[-1], closes[-1] - 1.0)
    assert result.approved
    assert result.fill is not None
    assert result.fill.quantity > 0
