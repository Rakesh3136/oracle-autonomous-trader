from datetime import datetime, timedelta, timezone

import pytest

from oracle.learning.dataset import Candle
from oracle.learning.dataset_builder import TrainingDatasetBuilder
from oracle.learning.features import FeatureEngine
from oracle.learning.model import LogisticBaseline
from oracle.runtime.bybit_live_paper import BybitLivePaperTrader


def make_candles(count: int = 120) -> list[Candle]:
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    return [
        Candle(
            start + timedelta(minutes=i),
            "BTCUSDT",
            100.0 + i * 0.1,
            101.0 + i * 0.1,
            99.0 + i * 0.1,
            100.5 + i * 0.1,
            1000.0 + i,
        )
        for i in range(count)
    ]


def test_live_probability_uses_latest_features_without_latest_label() -> None:
    candles = make_candles()
    rows = TrainingDatasetBuilder().build(candles, horizon=5, regime_window=20)
    model = LogisticBaseline(epochs=5)
    model.fit(rows[:-1])
    latest = FeatureEngine().transform(candles)[-1]
    probability = model.probability_up(latest)
    assert 0.0 <= probability <= 1.0


class FakePublicBybit:
    def __init__(self, candles: list[Candle]) -> None:
        self.candles = candles
        self.base_url = "fake"

    async def get_candles(self, symbol: str, interval: str, limit: int = 200) -> list[Candle]:
        return self.candles[-limit:]

    async def close(self) -> None:
        return None


@pytest.mark.asyncio
async def test_live_paper_cycle_uses_public_data_and_local_simulator() -> None:
    trader = BybitLivePaperTrader(poll_seconds=1.0)
    await trader.exchange.close()
    trader.exchange = FakePublicBybit(make_candles())  # type: ignore[assignment]

    snapshot = await trader.cycle()

    assert snapshot.symbol == "BTCUSDT"
    assert 0.0 <= snapshot.probability_up <= 1.0
    assert snapshot.report.equity > 0
    assert trader.simulator.fills or not snapshot.approved


def test_live_paper_defaults_to_bybit_testnet_public_data() -> None:
    trader = BybitLivePaperTrader(testnet_public=True)
    assert trader.exchange.base_url == "https://api-testnet.bybit.com"
