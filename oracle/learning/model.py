"""Small dependency-free probabilistic baseline for leakage-safe model evaluation.

This is intentionally a transparent baseline, not a claim of predictive superiority.
A production ML backend can implement the same interface later.
"""
from dataclasses import dataclass
from math import exp
from oracle.learning.dataset_builder import TrainingRow

@dataclass(frozen=True)
class Prediction:
    probability_up: float
    expected_return: float

class LogisticBaseline:
    def __init__(self, learning_rate: float = 0.05, epochs: int = 100) -> None:
        if learning_rate <= 0 or epochs <= 0:
            raise ValueError("learning_rate and epochs must be positive")
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.weights: list[float] = []
        self.bias = 0.0

    @staticmethod
    def _vector(row: TrainingRow) -> list[float]:
        f = row.features
        return [f.return_1, f.return_5, f.range_pct, f.body_pct,
                f.upper_wick_pct, f.lower_wick_pct, f.volume_change, f.volatility_10]

    @staticmethod
    def _sigmoid(x: float) -> float:
        x = max(-40.0, min(40.0, x))
        return 1.0 / (1.0 + exp(-x))

    def fit(self, rows: list[TrainingRow]) -> None:
        if not rows:
            raise ValueError("cannot train on empty data")
        self.weights = [0.0] * len(self._vector(rows[0]))
        self.bias = 0.0
        for _ in range(self.epochs):
            for row in rows:
                x = self._vector(row)
                y = 1.0 if row.label.direction > 0 else 0.0
                p = self._sigmoid(self.bias + sum(w * v for w, v in zip(self.weights, x)))
                error = p - y
                self.bias -= self.learning_rate * error
                for i, value in enumerate(x):
                    self.weights[i] -= self.learning_rate * error * value

    def predict(self, row: TrainingRow) -> Prediction:
        if not self.weights:
            raise RuntimeError("model has not been fitted")
        x = self._vector(row)
        p = self._sigmoid(self.bias + sum(w * v for w, v in zip(self.weights, x)))
        return Prediction(p, (2.0 * p - 1.0) * abs(row.label.future_return))

    def score(self, rows: list[TrainingRow]) -> float:
        if not rows:
            raise ValueError("cannot score empty data")
        correct = 0
        for row in rows:
            prediction = self.predict(row)
            actual_up = row.label.direction > 0
            correct += int((prediction.probability_up >= 0.5) == actual_up)
        return correct / len(rows)
