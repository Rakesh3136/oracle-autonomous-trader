"""Leakage-safe OHLCV feature generation from information available at each candle."""
from dataclasses import dataclass
from datetime import datetime
from math import log

from oracle.learning.dataset import Candle


@dataclass(frozen=True)
class FeatureRow:
    timestamp: datetime
    symbol: str
    return_1: float
    return_5: float
    range_pct: float
    body_pct: float
    upper_wick_pct: float
    lower_wick_pct: float
    volume_change: float
    volatility_10: float


class FeatureEngine:
    def transform(self, candles: list[Candle]) -> list[FeatureRow]:
        if not candles:
            return []
        closes = [c.close for c in candles]
        rows: list[FeatureRow] = []
        for i, c in enumerate(candles):
            prev = closes[i - 1] if i >= 1 else c.close
            prev5 = closes[i - 5] if i >= 5 else c.close
            base = max(c.close, 1e-12)
            rng = max(c.high - c.low, 1e-12)
            body = abs(c.close - c.open)
            upper = c.high - max(c.open, c.close)
            lower = min(c.open, c.close) - c.low
            returns = [
                log(closes[j] / closes[j - 1])
                for j in range(max(1, i - 9), i + 1)
            ]
            mean_return = sum(returns) / len(returns)
            variance = sum((x - mean_return) ** 2 for x in returns) / len(returns)
            vol_change = (
                0.0
                if i == 0 or candles[i - 1].volume == 0
                else c.volume / candles[i - 1].volume - 1
            )
            rows.append(
                FeatureRow(
                    c.timestamp,
                    c.symbol,
                    c.close / prev - 1,
                    c.close / prev5 - 1,
                    rng / base,
                    body / rng,
                    upper / rng,
                    lower / rng,
                    vol_change,
                    variance**0.5,
                )
            )
        return rows
