"""Multi-timeframe feature extraction without leaking future information."""
from dataclasses import dataclass
from statistics import mean
from oracle.market.state import Candle

@dataclass(frozen=True)
class TimeframeFeatures:
    timeframe: str
    last_close: float
    return_pct: float | None
    average_range_pct: float | None
    volume_ratio: float | None
    direction: int

class MultiTimeframeFeatures:
    def compute(self, candles: list[Candle], timeframe: str, lookback: int = 20) -> TimeframeFeatures | None:
        series = [c for c in candles if c.timeframe == timeframe]
        if not series:
            return None
        series = series[-max(lookback, 2):]
        first, last = series[0], series[-1]
        return_pct = (last.close / first.close - 1.0) if first.close else None
        ranges = [(c.high - c.low) / c.close for c in series if c.close]
        prior_volumes = [c.volume for c in series[:-1]]
        avg_volume = mean(prior_volumes) if prior_volumes else None
        volume_ratio = last.volume / avg_volume if avg_volume else None
        direction = 1 if last.close > first.close else -1 if last.close < first.close else 0
        return TimeframeFeatures(timeframe, last.close, return_pct, mean(ranges) if ranges else None, volume_ratio, direction)

    def align(self, candles: list[Candle], timeframes: tuple[str, ...]) -> tuple[TimeframeFeatures, ...]:
        features = []
        for timeframe in timeframes:
            feature = self.compute(candles, timeframe)
            if feature is not None:
                features.append(feature)
        return tuple(features)
