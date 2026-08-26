"""Small dependency-free probabilistic baseline for leakage-safe model evaluation."""
from dataclasses import dataclass
from math import exp

from oracle.learning.dataset_builder import TrainingRow
from oracle.learning.features import FeatureRow


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
        return LogisticBaseline.vector_from_features(row.features)

    @staticmethod
    def vector_from_features(features: FeatureRow) -> list[float]:
        return [
            features.return_1,
            features.return_5,
            features.range_pct,
            features.body_pct,
            features.upper_wick_pct,
            features.lower_wick_pct,
            features.volume_change,
            features.volatility_10,
        ]

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

    def probability_up(self, features: FeatureRow) -> float:
        if not self.weights:
            raise RuntimeError("model has not been fitted")
        x = self.vector_from_features(features)
        return self._sigmoid(self.bias + sum(w * v for w, v in zip(self.weights, x)))

    def predict(self, row: TrainingRow) -> Prediction:
        probability = self.probability_up(row.features)
        return Prediction(probability, (2.0 * probability - 1.0) * abs(row.label.future_return))

    def score(self, rows: list[TrainingRow]) -> float:
        if not rows:
            raise ValueError("cannot score empty data")
        correct = 0
        for row in rows:
            correct += int((self.probability_up(row.features) >= 0.5) == (row.label.direction > 0))
        return correct / len(rows)
