from datetime import datetime, timedelta, timezone
import pytest
from oracle.ai.council import TraderCouncil
from oracle.core.trader import Action
from oracle.market.models import Candle
from oracle.paper.live_paper import LivePaperTrader
from oracle.strategies.baseline import MomentumStrategy

class FakeFeed:
    def __init__(self, closes: list[float]) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.candles = [
            Candle("BTCUSDT", "1", start + timedelta(minutes=i), p, p, p, p, 1.0)
            for i, p in enumerate(closes)
        ]
        self.calls = 0

    async def get_candles(self, symbol: str, interval: str, limit: int = 200) -> list[Candle]:
        self.calls += 1
        return self.candles

    async def close(self) -> None:
        return None

@pytest.mark.asyncio
async def test_live_market_data_drives_only_simulated_orders() -> None:
    feed = FakeFeed([100.0, 100.7])
    trader = LivePaperTrader(feed, TraderCouncil([MomentumStrategy()]), quantity=1.0)
    step = await trader.step()
    assert step.action is Action.LONG
    assert step.opened
    assert len(trader.simulator.fills) == 1
    assert trader.report().trades == 0

@pytest.mark.asyncio
async def test_repeated_candle_is_not_traded_twice() -> None:
    feed = FakeFeed([100.0, 100.7])
    trader = LivePaperTrader(feed, TraderCouncil([MomentumStrategy()]), quantity=1.0)
    first = await trader.step()
    second = await trader.step()
    assert first.opened
    assert not second.opened
    assert len(trader.simulator.fills) == 1

@pytest.mark.asyncio
async def test_opposite_signal_closes_and_reverses_in_paper_mode() -> None:
    feed = FakeFeed([100.0, 100.7, 99.0])
    trader = LivePaperTrader(feed, TraderCouncil([MomentumStrategy()]), quantity=1.0)
    await trader.step()
    feed.candles = feed.candles[:2] + [Candle("BTCUSDT", "1", feed.candles[1].timestamp + timedelta(minutes=1), 99.0, 99.0, 99.0, 99.0, 1.0)]
    step = await trader.step()
    assert step.action is Action.SHORT
    assert step.closed and step.opened
    assert trader.report().trades == 1
    assert len(trader.simulator.fills) == 2
