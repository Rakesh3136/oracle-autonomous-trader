from datetime import datetime, timedelta, timezone

import pytest

from oracle.backtest.ledger import TradeLedger
from oracle.backtest.replay import MarketReplay, MarketTick, ReplayTrade


def ticks() -> list[MarketTick]:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [
        MarketTick(start + timedelta(minutes=i), "BTCUSDT", price)
        for i, price in enumerate([100.0, 101.0, 102.0, 99.0, 103.0])
    ]


def test_ledger_records_realized_pnl_fees_and_equity() -> None:
    ledger = TradeLedger(10_000.0)
    ledger.record(ticks()[1].timestamp, "t1", "BTCUSDT", 1, 2.0, 100.0, 102.0, 0.50)
    ledger.record(ticks()[3].timestamp, "t2", "BTCUSDT", -1, 1.0, 102.0, 99.0, 0.25)

    summary = ledger.summary()
    assert summary.trades == 2
    assert summary.wins == 1
    assert summary.losses == 1
    assert summary.realized_pnl == pytest.approx(7.25)
    assert summary.fees == pytest.approx(0.75)
    assert summary.ending_equity == pytest.approx(10_007.25)
    assert summary.return_pct == pytest.approx(0.0725)
    assert ledger.equity_curve()[-1].equity == pytest.approx(10_007.25)


def test_replay_never_sorts_or_looks_ahead() -> None:
    seen: list[datetime] = []
    result = MarketReplay().run(ticks(), lambda tick: seen.append(tick.timestamp) or True)

    assert result.errors == ()
    assert result.decisions == 5
    assert seen == [tick.timestamp for tick in ticks()]


def test_replay_rejects_non_monotonic_input() -> None:
    data = ticks()
    data[3], data[4] = data[4], data[3]
    result = MarketReplay().run(data, lambda _: True)

    assert result.decisions == 4
    assert any("non-monotonic" in error for error in result.errors)


def test_replay_records_trade_equity_curve() -> None:
    data = ticks()
    result = MarketReplay().record_trades(
        data,
        [
            ReplayTrade("t1", "BTCUSDT", 1, 0, 2, 2.0, 100.0, 102.0, 0.5),
            ReplayTrade("t2", "BTCUSDT", -1, 2, 4, 1.0, 102.0, 103.0, 0.25),
        ],
    )

    assert result.errors == ()
    assert result.summary.trades == 2
    assert result.summary.realized_pnl == pytest.approx(2.25)
    assert result.summary.ending_equity == pytest.approx(10_002.25)
    assert result.equity_curve == pytest.approx((10_001.5, 10_002.25))


def test_ledger_rejects_duplicate_trade_ids() -> None:
    ledger = TradeLedger(10_000.0)
    timestamp = ticks()[0].timestamp
    ledger.record(timestamp, "same", "BTCUSDT", 1, 1.0, 100.0, 101.0)

    with pytest.raises(ValueError, match="duplicate trade id"):
        ledger.record(timestamp, "same", "BTCUSDT", 1, 1.0, 100.0, 101.0)
