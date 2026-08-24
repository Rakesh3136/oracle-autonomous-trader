"""Confidence calibration utilities for specialist forecasts."""
from dataclasses import dataclass

@dataclass(frozen=True)
class CalibrationBucket:
    lower: float
    upper: float
    predictions: int
    successes: int

    @property
    def empirical_rate(self) -> float:
        return self.successes / self.predictions if self.predictions else 0.0

class ConfidenceCalibrator:
    def __init__(self, bucket_count: int = 10) -> None:
        if bucket_count <= 0:
            raise ValueError("bucket_count must be positive")
        self.bucket_count = bucket_count

    def buckets(self, predictions: list[tuple[float, bool]]) -> tuple[CalibrationBucket, ...]:
        buckets: list[CalibrationBucket] = []
        for i in range(self.bucket_count):
            lo = i / self.bucket_count
            hi = (i + 1) / self.bucket_count
            selected = [(p, success) for p, success in predictions if lo <= p < hi or (i == self.bucket_count - 1 and p == hi)]
            buckets.append(CalibrationBucket(lo, hi, len(selected), sum(1 for _, success in selected if success)))
        return tuple(buckets)
