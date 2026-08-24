"""Market-data quality gates for autonomous decision making."""
from dataclasses import dataclass

@dataclass(frozen=True)
class DataQuality:
    score: float
    usable: bool
    reasons: tuple[str, ...]

class DataQualityGate:
    def evaluate(self, candles: int, has_book: bool, has_derivatives: bool, minimum: float = 0.8) -> DataQuality:
        score = (0.5 if candles > 0 else 0.0) + (0.3 if has_book else 0.0) + (0.2 if has_derivatives else 0.0)
        reasons = []
        if candles == 0: reasons.append("no candle data")
        if not has_book: reasons.append("order book unavailable")
        if not has_derivatives: reasons.append("derivatives context unavailable")
        return DataQuality(score, score >= minimum, tuple(reasons))
