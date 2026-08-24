from datetime import datetime, timedelta, timezone

from oracle.market.models import Candle, MarketSnapshot
from oracle.regime.classifier import Regime, RegimeClassifier


def test_classifier_requires_history() -> None:
    snapshot = MarketSnapshot(
        symbol="BTCUSDT",
        timestamp=datetime.now(timezone.utc),
        candles=tuple(
            Candle("BTCUSDT", "1m", datetime.now(timezone.utc), 100, 100, 100, 100, 1)
            for _ in range(5)
        ),
    )
    assert RegimeClassifier().classify(snapshot).regime is Regime.UNKNOWN


def test_classifier_detects_bullish_move() -> None:
    start = datetime.now(timezone.utc)
    candles = tuple(
        Candle("BTCUSDT", "1m", start + timedelta(minutes=i), p, p, p, p, 1)
        for i, p in enumerate([100.0] * 20 + [102.0])
    )
    snapshot = MarketSnapshot("BTCUSDT", candles[-1].timestamp, candles=candles)
    assert RegimeClassifier().classify(snapshot).regime is Regime.BULL_TREND
