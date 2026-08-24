"""Controlled strategy evolution: candidates compete in research, never directly in live execution."""
from dataclasses import dataclass

@dataclass(frozen=True)
class StrategyCandidate:
    strategy_id: str
    version: str
    in_sample_score: float
    out_of_sample_score: float
    robustness_score: float
    trades: int

@dataclass(frozen=True)
class PromotionDecision:
    strategy_id: str
    version: str
    promoted: bool
    score: float
    reason: str

class ChampionSelector:
    def __init__(self, min_trades: int = 100, min_oos_score: float = 0.0, min_robustness: float = 0.5) -> None:
        self.min_trades = min_trades
        self.min_oos_score = min_oos_score
        self.min_robustness = min_robustness

    def evaluate(self, candidate: StrategyCandidate) -> PromotionDecision:
        if candidate.trades < self.min_trades:
            return PromotionDecision(candidate.strategy_id, candidate.version, False, 0.0, "insufficient sample size")
        if candidate.out_of_sample_score < self.min_oos_score:
            return PromotionDecision(candidate.strategy_id, candidate.version, False, candidate.out_of_sample_score, "out-of-sample threshold failed")
        if candidate.robustness_score < self.min_robustness:
            return PromotionDecision(candidate.strategy_id, candidate.version, False, candidate.robustness_score, "robustness threshold failed")
        score = 0.5 * candidate.out_of_sample_score + 0.3 * candidate.robustness_score + 0.2 * candidate.in_sample_score
        return PromotionDecision(candidate.strategy_id, candidate.version, True, score, "research promotion candidate passed gates")

    def select(self, candidates: list[StrategyCandidate]) -> PromotionDecision | None:
        decisions = [self.evaluate(c) for c in candidates]
        passed = [d for d in decisions if d.promoted]
        return max(passed, key=lambda d: d.score) if passed else None
