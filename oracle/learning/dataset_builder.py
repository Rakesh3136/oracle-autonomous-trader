"""Leakage-safe feature/label dataset assembly and walk-forward windows."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from oracle.learning.dataset import Candle
from oracle.learning.features import FeatureEngine, FeatureRow
from oracle.learning.labels import LabelEngine, LabelRow

@dataclass(frozen=True)
class TrainingRow:
    timestamp: object
    symbol: str
    features: FeatureRow
    label: LabelRow

@dataclass(frozen=True)
class WalkForwardWindow:
    train_start: datetime
    train_end: datetime
    validation_end: datetime
    test_end: datetime
    train: tuple[TrainingRow, ...]
    validation: tuple[TrainingRow, ...]
    test: tuple[TrainingRow, ...]

class TrainingDatasetBuilder:
    def __init__(self) -> None:
        self.features = FeatureEngine()
        self.labels = LabelEngine()

    def build(self, candles: list[Candle], horizon: int = 5) -> list[TrainingRow]:
        feature_rows = self.features.transform(candles)
        label_rows = self.labels.transform(candles, (horizon,))
        labels = {(r.timestamp, r.symbol): r for r in label_rows}
        return [TrainingRow(f.timestamp, f.symbol, f, labels[(f.timestamp, f.symbol)])
                for f in feature_rows if (f.timestamp, f.symbol) in labels]

    def walk_forward(self, rows: list[TrainingRow], train_days: int, validation_days: int,
                     test_days: int, step_days: int) -> list[WalkForwardWindow]:
        if min(train_days, validation_days, test_days, step_days) <= 0:
            raise ValueError("window sizes must be positive")
        ordered = sorted(rows, key=lambda r: r.timestamp)
        if not ordered:
            return []
        start, end = ordered[0].timestamp, ordered[-1].timestamp
        windows: list[WalkForwardWindow] = []
        cursor = start
        while cursor + timedelta(days=train_days + validation_days + test_days) <= end:
            train_end = cursor + timedelta(days=train_days)
            validation_end = train_end + timedelta(days=validation_days)
            test_end = validation_end + timedelta(days=test_days)
            train = tuple(r for r in ordered if cursor <= r.timestamp < train_end)
            validation = tuple(r for r in ordered if train_end <= r.timestamp < validation_end)
            test = tuple(r for r in ordered if validation_end <= r.timestamp < test_end)
            if train and validation and test:
                windows.append(WalkForwardWindow(cursor, train_end, validation_end, test_end,
                                                 train, validation, test))
            cursor += timedelta(days=step_days)
        return windows
