"""Initial deterministic market-regime classifier.

This is deliberately transparent and replaceable. ML regime models can later
be evaluated as challengers against this baseline.
"""

from dataclasses import dataclass
from enum import StrEnum

from oracle.market.features import order_book_imbalance, realized_volatility, returns
from oracle.market.models import MarketSnapshot


class Regime(StrEnum):
    UNKNOWN = "unknown"
    BULL_TREND = "bull_trend"
    BEAR_TREND = "bear_trend"
    RANGE = "range"
    HIGH_VOLATILITY = "high_volatility"


@dataclass(frozen=True)
class RegimeAssessment:
    regime: Regime
    confidence: float
    reasons: tuple[str, ...]


class RegimeClassifier:
    """Conservative baseline classifier; confidence is bounded and explainable."""

    def classify(self, snapshot: MarketSnapshot) -> RegimeAssessment:
        candles = snapshot.candles
        if len(candles) < 21:
            return RegimeAssessment(Regime.UNKNOWN, 0.0, ("insufficient candle history",))

        change = returns(candles)
        volatility = realized_volatility(candles)
        imbalance = order_book_imbalance(snapshot.order_book) if snapshot.order_book else None

        if change is None or volatility is None:
            return RegimeAssessment(Regime.UNKNOWN, 0.0, ("features unavailable",))

        reasons: list[str] = []
        if volatility >= 0.03:
            reasons.append("elevated realized volatility")
            return RegimeAssessment(Regime.HIGH_VOLATILITY, min(1.0, volatility / 0.06), tuple(reasons))

        if change >= 0.01:
            reasons.append("positive recent return")
            if imbalance is not None and imbalance > 0.10:
                reasons.append("positive order-book imbalance")
            return RegimeAssessment(Regime.BULL_TREND, min(1.0, abs(change) / 0.03), tuple(reasons))

        if change <= -0.01:
            reasons.append("negative recent return")
            if imbalance is not None and imbalance < -0.10:
                reasons.append("negative order-book imbalance")
            return RegimeAssessment(Regime.BEAR_TREND, min(1.0, abs(change) / 0.03), tuple(reasons))

        reasons.append("recent return within neutral range")
        return RegimeAssessment(Regime.RANGE, 0.5, tuple(reasons))
