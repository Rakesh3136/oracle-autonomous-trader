"""Multi-timeframe alignment helpers."""
from dataclasses import dataclass
from datetime import datetime
from collections.abc import Sequence
from oracle.market.models import Candle

@dataclass(frozen=True)
class TimeframeSnapshot:
    timestamp: datetime
    candles_by_interval: dict[str, Candle]

def latest_by_interval(series: dict[str, Sequence[Candle]]) -> TimeframeSnapshot:
    latest: dict[str, Candle] = {}
    for interval, candles in series.items():
        if candles:
            latest[interval] = max(candles, key=lambda c: c.timestamp)
    if not latest:
        raise ValueError("no candles supplied")
    timestamp = max(c.timestamp for c in latest.values())
    return TimeframeSnapshot(timestamp, latest)
