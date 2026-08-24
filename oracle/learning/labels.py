"""Forward-looking labels generated strictly after each feature timestamp."""
from dataclasses import dataclass
from oracle.learning.dataset import Candle

@dataclass(frozen=True)
class LabelRow:
    timestamp: object
    symbol: str
    horizon: int
    future_return: float
    direction: int
    max_favorable_return: float
    max_adverse_return: float

class LabelEngine:
    def transform(self, candles: list[Candle], horizons: tuple[int, ...] = (1, 5, 20)) -> list[LabelRow]:
        if not candles:
            return []
        closes = [c.close for c in candles]
        rows: list[LabelRow] = []
        for i in range(len(candles)):
            for h in horizons:
                j = i + h
                if j >= len(candles):
                    continue
                base = closes[i]
                future = closes[j] / base - 1.0
                path = [closes[k] / base - 1.0 for k in range(i + 1, j + 1)]
                rows.append(LabelRow(candles[i].timestamp, candles[i].symbol, h, future,
                                     1 if future > 0 else -1 if future < 0 else 0,
                                     max(path), min(path)))
        return rows
