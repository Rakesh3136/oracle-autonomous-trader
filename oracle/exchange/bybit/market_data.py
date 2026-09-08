"""Bybit market-data boundary for paper trading.

This module deliberately contains no order-placement code. A transport adapter can
feed validated public candle data into the paper strategy without granting trading
permissions to the market-data path.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ValueError("candle timestamp must be timezone-aware")
        if min(self.open, self.high, self.low, self.close, self.volume) < 0:
            raise ValueError("candle values cannot be negative")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be at least open, close and low")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be at most open, close and high")


class BybitPublicCandleParser:
    """Parse the normalized candle payload from an injected Bybit transport."""

    def parse(self, payload: Mapping[str, object]) -> list[Candle]:
        raw = payload.get("result")
        if not isinstance(raw, Mapping):
            raise ValueError("missing Bybit result payload")
        rows = raw.get("list")
        if not isinstance(rows, list):
            raise ValueError("missing Bybit candle list")
        candles: list[Candle] = []
        for row in rows:
            if not isinstance(row, list) or len(row) < 6:
                raise ValueError("invalid Bybit candle row")
            timestamp = datetime.fromtimestamp(float(row[0]) / 1000.0, tz=timezone.utc)
            candles.append(Candle(timestamp, float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5])))
        candles.sort(key=lambda candle: candle.timestamp)
        return candles
