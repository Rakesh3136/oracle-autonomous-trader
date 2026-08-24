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
    rows: tuple[TrainingRow, ...]

class TrainingDatasetBuilder:
    def __init__(self) -> None:
        self.features = FeatureEngine()
        self.labels = LabelEngine()

    def build(self, candles: list[Candle], horizon: int = 5) -> list[TrainingRow]:
        feature_rows = self.features.transform(candles)
        label_rows = self.labels.transform(candles, (horizon,))
        labels = {(r.timestamp, r.symbol): r for r in label_rows}
        rows: list[TrainingRow] = []
        for feature in feature_rows:
            label = labels.get((feature.timestamp, feature.symbol))
            if label is not None:
                rows.append(TrainingRow(feature.timestamp, feature.symbol, feature, label))
        return rows

    def walk_forward(self, rows: list[TrainingRow], train_days: int, validation_days: int,
                     test_days: int, step_days: int) -> list[WalkForwardWindow]:
        if min(train_days, validation_days, test_days, step_days) <= 0:
            raise ValueError("window sizes must be positive")
        if not rows:
            return []
        ordered = sorted(rows, key=lambda r: r.timestamp)
        start = ordered[0].timestamp
        end = ordered[-1].timestamp
        windows: list[WalkForwardWindow] = []
        cursor = start
        while cursor + timedelta(days=train_days + validation_days + test_days) <= end:
            train_end = cursor + timedelta(days=train_days)
            validation_end = train_end + timedelta(days=validation_days)
            test_end = validation_end + timedelta(days=test_days)
            window_rows = tuple(r for r in ordered if cursor <= r.timestamp < test_end)
            windows.append(WalkForwardWindow(cursor, train_end, validation_end, test_end, window_rows))
            cursor += timedelta(days=step_days)
        return windows
