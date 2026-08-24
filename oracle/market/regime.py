"""Deterministic market-regime classifier for downstream strategy selection."""
from dataclasses import dataclass
from enum import Enum
from statistics import mean, pstdev

from oracle.market.models import Candle


class MarketRegime(str, Enum):
    TREND_UP = "trend_up"
    TREND_DOWN = "trend_down"
    RANGE = "range"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    TRANSITION = "transition"


@dataclass(frozen=True)
class RegimeSnapshot:
    regime: MarketRegime
    trend_score: float
    volatility: float
    confidence: float


class RegimeClassifier:
    def classify(self, candles: list[Candle], lookback: int = 30) -> RegimeSnapshot:
        if len(candles) < max(10, lookback):
            return RegimeSnapshot(MarketRegime.TRANSITION, 0.0, 0.0, 0.0)
        series = candles[-lookback:]
        closes = [c.close for c in series]
        returns = [
            closes[i] / closes[i - 1] - 1.0
            for i in range(1, len(closes))
            if closes[i - 1]
        ]
        if not returns:
            return RegimeSnapshot(MarketRegime.TRANSITION, 0.0, 0.0, 0.0)
        trend = closes[-1] / closes[0] - 1.0
        volatility = pstdev(returns)
        avg_abs_return = mean(abs(r) for r in returns)
        if volatility > max(0.01, avg_abs_return * 1.8):
            regime = MarketRegime.HIGH_VOLATILITY
        elif volatility < max(0.001, avg_abs_return * 0.6):
            regime = MarketRegime.LOW_VOLATILITY
        elif abs(trend) < volatility * 3:
            regime = MarketRegime.RANGE
        elif trend > 0:
            regime = MarketRegime.TREND_UP
        elif trend < 0:
            regime = MarketRegime.TREND_DOWN
        else:
            regime = MarketRegime.TRANSITION
        confidence = min(1.0, max(0.0, abs(trend) / max(volatility * 3, 1e-9)))
        return RegimeSnapshot(regime, trend, volatility, confidence)
