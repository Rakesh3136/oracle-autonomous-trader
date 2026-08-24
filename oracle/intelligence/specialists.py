"""Small, deterministic specialist implementations for the Trader Council.

These specialists produce evidence, not orders. Risk and execution remain separate.
"""
from dataclasses import dataclass
from enum import Enum
from statistics import mean

class Bias(str, Enum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"

@dataclass(frozen=True)
class SpecialistView:
    specialist: str
    bias: Bias
    confidence: float
    rationale: str

class TrendSpecialist:
    name = "trend"
    def evaluate(self, closes: list[float]) -> SpecialistView:
        if len(closes) < 3:
            return SpecialistView(self.name, Bias.NEUTRAL, 0.0, "insufficient trend history")
        change = closes[-1] / closes[0] - 1 if closes[0] else 0
        bias = Bias.LONG if change > 0 else Bias.SHORT if change < 0 else Bias.NEUTRAL
        return SpecialistView(self.name, bias, min(1.0, abs(change) * 10), f"lookback return={change:.5f}")

class MomentumSpecialist:
    name = "momentum"
    def evaluate(self, closes: list[float]) -> SpecialistView:
        if len(closes) < 2 or closes[-2] == 0:
            return SpecialistView(self.name, Bias.NEUTRAL, 0.0, "insufficient momentum history")
        change = closes[-1] / closes[-2] - 1
        bias = Bias.LONG if change > 0 else Bias.SHORT if change < 0 else Bias.NEUTRAL
        return SpecialistView(self.name, bias, min(1.0, abs(change) * 20), f"last return={change:.5f}")

class MeanReversionSpecialist:
    name = "mean_reversion"
    def evaluate(self, closes: list[float], window: int = 20) -> SpecialistView:
        if len(closes) < window:
            return SpecialistView(self.name, Bias.NEUTRAL, 0.0, "insufficient mean history")
        avg = mean(closes[-window:])
        if avg == 0:
            return SpecialistView(self.name, Bias.NEUTRAL, 0.0, "invalid mean")
        deviation = closes[-1] / avg - 1
        bias = Bias.SHORT if deviation > 0 else Bias.LONG if deviation < 0 else Bias.NEUTRAL
        return SpecialistView(self.name, bias, min(1.0, abs(deviation) * 10), f"mean deviation={deviation:.5f}")

class VolatilitySpecialist:
    name = "volatility"
    def evaluate(self, closes: list[float], window: int = 20) -> SpecialistView:
        if len(closes) < window + 1:
            return SpecialistView(self.name, Bias.NEUTRAL, 0.0, "insufficient volatility history")
        returns = [closes[i] / closes[i-1] - 1 for i in range(len(closes)-window, len(closes)) if closes[i-1]]
        vol = (sum(r*r for r in returns) / len(returns)) ** 0.5 if returns else 0.0
        return SpecialistView(self.name, Bias.NEUTRAL, min(1.0, vol * 20), f"realized volatility={vol:.5f}")
