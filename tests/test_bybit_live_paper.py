from datetime import datetime, timedelta, timezone

from oracle.learning.dataset import Candle
from oracle.learning.dataset_builder import TrainingDatasetBuilder
from oracle.learning.features import FeatureEngine
from oracle.learning.model import LogisticBaseline


def make_candles(count: int = 80) -> list[Candle]:
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
