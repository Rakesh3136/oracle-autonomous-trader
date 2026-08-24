"""Validation gates for candidate strategies."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ValidationReport:
    passed: bool
    in_sample: float
    out_of_sample: float
    walk_forward: float
    stress: float
    reasons: tuple[str, ...]

class ValidationGate:
    def evaluate(self, in_sample: float, out_of_sample: float, walk_forward: float, stress: float) -> ValidationReport:
        reasons = []
        if out_of_sample <= 0: reasons.append("negative or zero out-of-sample score")
        if walk_forward <= 0: reasons.append("walk-forward validation failed")
        if stress <= 0: reasons.append("stress validation failed")
        return ValidationReport(not reasons, in_sample, out_of_sample, walk_forward, stress, tuple(reasons))
