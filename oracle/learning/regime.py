"""Deterministic market-regime classification using only information known at t."""
from dataclasses import dataclass
from enum import Enum
from statistics import pstdev

class Regime(str, Enum):
    BULL = "bull"
    BEAR = "bear"
    RANGE = "range"
    HIGH_VOL = "high_volatility"
    LOW_VOL = "low_volatility"

@dataclass(frozen=True)
class RegimeState:
    regime: Regime
    trend_score: float
    volatility: float

class RegimeEngine:
    def classify(self, closes: list[float], window: int = 20) -> RegimeState:
        if len(closes) < max(5, window):
            raise ValueError("insufficient history for regime classification")
        recent = closes[-window:]
        start = max(abs(recent[0]), 1e-12)
        trend = (recent[-1] - recent[0]) / start
        returns = [recent[i] / recent[i - 1] - 1 for i in range(1, len(recent))]
        vol = pstdev(returns) if len(returns) > 1 else 0.0
        if vol >= 0.04:
            regime = Regime.HIGH_VOL
        elif vol <= 0.005:
            regime = Regime.LOW_VOL
        elif trend >= 0.08:
            regime = Regime.BULL
        elif trend <= -0.08:
            regime = Regime.BEAR
        else:
            regime = Regime.RANGE
        return RegimeState(regime, trend, vol)
