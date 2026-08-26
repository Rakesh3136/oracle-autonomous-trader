import pytest
from oracle.execution.order_intent import OrderIntent, OrderType, Side
from oracle.execution.simulator import ExecutionSimulator
from oracle.paper.performance import PaperPerformance

def test_paper_report_calculates_win_rate_equity_and_drawdown() -> None:
    performance = PaperPerformance(10_000.0)
    simulator = ExecutionSimulator()
    intent = OrderIntent.make("BTCUSDT", Side.BUY, OrderType.MARKET, 1.0)
    fill = simulator.submit(intent, 100.0)
    performance.record(PaperPerformance.close_fill(fill, 110.0, fees=1.0))
    performance.record(PaperPerformance.close_fill(fill, 90.0, fees=1.0))
    report = performance.report()
    assert report.trades == 2
    assert report.wins == 1
    assert report.losses == 1
    assert report.win_rate == pytest.approx(0.5)
    assert report.net_pnl == pytest.approx(0.0)
    assert report.fees == pytest.approx(2.0)
    assert report.equity == pytest.approx(9998.0)
    assert report.max_drawdown == pytest.approx(21.0)

def test_short_trade_pnl_is_reversed() -> None:
    simulator = ExecutionSimulator()
    intent = OrderIntent.make("BTCUSDT", Side.SELL, OrderType.MARKET, 2.0)
    fill = simulator.submit(intent, 100.0)
    trade = PaperPerformance.close_fill(fill, 90.0)
    assert trade.pnl == pytest.approx(20.0)
