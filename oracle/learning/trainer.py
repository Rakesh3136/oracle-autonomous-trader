"""Controlled walk-forward candidate training and promotion proposals."""
from dataclasses import dataclass
from oracle.learning.dataset_builder import TrainingDatasetBuilder, TrainingRow
from oracle.learning.evaluation import ModelEvaluator, ModelReport
from oracle.learning.model import LogisticBaseline
from oracle.learning.registry import ModelRegistry, ModelVersion

@dataclass(frozen=True)
class TrainingProposal:
    version: str
    report: ModelReport
    eligible: bool
    reason: str

class WalkForwardTrainer:
    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or ModelRegistry()
        self.evaluator = ModelEvaluator()
        self.builder = TrainingDatasetBuilder()

    def train_candidate(self, rows: list[TrainingRow], version: str) -> TrainingProposal:
        if len(rows) < 10:
            raise ValueError("candidate dataset is too small")
        # Chronological split: the final 20% is never used for fitting.
        cut = max(1, int(len(rows) * 0.8))
        train_rows, test_rows = rows[:cut], rows[cut:]
        model = LogisticBaseline()
        model.fit(train_rows)
        report = self.evaluator.evaluate(model, test_rows)
        current = self.registry.champion
        current_report = current.report if current else None
        eligible = self._better(current_report, report)
        reason = "candidate beats current champion on held-out data" if eligible else "candidate rejected by promotion criteria"
        self.registry.register(version, report)
        return TrainingProposal(version, report, eligible, reason)

    @staticmethod
    def _better(current: ModelReport | None, candidate: ModelReport) -> bool:
        if current is None:
            return candidate.samples >= 10 and candidate.directional_brier < 0.25
        return (candidate.directional_brier < current.directional_brier and
                candidate.average_return_when_correct >= current.average_return_when_correct and
                candidate.samples >= current.samples)

    def promote_if_eligible(self, proposal: TrainingProposal) -> ModelVersion | None:
        if not proposal.eligible:
            return None
        return self.registry.promote(proposal.version)
