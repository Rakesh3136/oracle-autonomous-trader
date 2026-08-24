"""Versioned, leakage-resistant historical training dataset primitives."""
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256

@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass(frozen=True)
class DatasetSlice:
    name: str
    start: datetime
    end: datetime
    candles: tuple[Candle, ...]

@dataclass(frozen=True)
class DatasetManifest:
    version: str
    row_count: int
    content_hash: str

class DatasetBuilder:
    def validate(self, candles: list[Candle]) -> None:
        previous: datetime | None = None
        for c in candles:
            if not (c.open > 0 and c.high > 0 and c.low > 0 and c.close > 0 and c.volume >= 0):
                raise ValueError("invalid candle values")
            if c.high < max(c.open, c.close) or c.low > min(c.open, c.close) or c.high < c.low:
                raise ValueError("invalid OHLC relationship")
            if previous is not None and c.timestamp <= previous:
                raise ValueError("candles must be strictly chronological")
            previous = c.timestamp

    def manifest(self, version: str, candles: list[Candle]) -> DatasetManifest:
        self.validate(candles)
        raw = "\n".join(f"{c.timestamp.isoformat()}|{c.symbol}|{c.open}|{c.high}|{c.low}|{c.close}|{c.volume}" for c in candles)
        return DatasetManifest(version, len(candles), sha256(raw.encode()).hexdigest())

    def time_split(self, candles: list[Candle], train_end: datetime, validation_end: datetime) -> tuple[DatasetSlice, DatasetSlice, DatasetSlice]:
        self.validate(candles)
        train = tuple(c for c in candles if c.timestamp <= train_end)
        validation = tuple(c for c in candles if train_end < c.timestamp <= validation_end)
        test = tuple(c for c in candles if c.timestamp > validation_end)
        if not train or not validation or not test:
            raise ValueError("train, validation, and test slices must all contain data")
        return (
            DatasetSlice("train", train[0].timestamp, train[-1].timestamp, train),
            DatasetSlice("validation", validation[0].timestamp, validation[-1].timestamp, validation),
            DatasetSlice("test", test[0].timestamp, test[-1].timestamp, test),
        )
