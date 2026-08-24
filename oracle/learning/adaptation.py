"""Controlled adaptation: learning produces candidates, never direct live orders."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Lesson:
    category: str
    observation: str
    confidence: float

class AdaptationEngine:
    def extract(self, outcome_pnl: float, thesis_quality: float) -> Lesson:
        if outcome_pnl < 0 and thesis_quality < 0.5:
            return Lesson("thesis", "review weak thesis formation", 0.8)
        if outcome_pnl < 0:
            return Lesson("risk", "review adverse outcome and sizing", 0.7)
        return Lesson("execution", "retain evidence from successful process", min(1.0, thesis_quality))
