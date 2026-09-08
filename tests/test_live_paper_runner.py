from datetime import datetime, timedelta, timezone

import pytest

from oracle.exchange.bybit.public_rest import BybitPublicRest
from oracle.market.models import Candle
from oracle.paper.live_runner import LivePaperRunner


class FakeSource:
    def __init__(self, candles: list[Candle]) -> None:
        self.candles = candles
        self.calls: list[tuple[str, str, int]] = []

    async def get_candles(self, symbol: str, interval: str, limit: int = 200) -> list[Candle]:
        self.calls.append((symbol, interval, limit))
        return self.candles


def make_candles(count: int, start: datetime) -> list[Candle]:
    return [
        Candle("BTCUSDT", "1", start + timedelta(minutes=i), 100 + i, 101 + i, 99 + i, 100.5 + i, 10)
        for i in range(count)
    ]


@pytest.mark.asyncio
async def test_live_runner_ignores_in_progress_candle_and_deduplicates() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    candles = make_candles(21, start)
    source = FakeSource(candles)
    runner = LivePaperRunner(source, history_size=200)

    now = start + timedelta(minutes=20, seconds=30)
    cycle = await runner.step(now)

    assert cycle is not None
    assert cycle.timestamp == start + timedelta(minutes=19)
    assert len(runner.history) == 20
    assert candles[-1].timestamp > cycle.timestamp
    assert await runner.step(now) is None


@pytest.mark.asyncio
async def test_live_runner_uses_public_adapter_without_private_order_calls() -> None:
    adapter = BybitPublicRest(testnet=True)
    assert adapter.base_url == "https://api-testnet.bybit.com"
    await adapter.close()

    source = FakeSource(make_candles(20, datetime(2026, 1, 1, tzinfo=timezone.utc)))
    runner = LivePaperRunner(source)
    cycle = await runner.step(datetime(2026, 1, 1, 0, 20, 30, tzinfo=timezone.utc))
    assert cycle is not None
    assert runner.simulator.fills is not None
