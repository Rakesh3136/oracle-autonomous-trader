from dataclasses import dataclass

@dataclass(frozen=True)
class StrategyScore:
    name: str
    net_return: float
    max_drawdown: float
    trades: int

    @property
    def score(self) -> float:
        return self.net_return - self.max_drawdown

class StrategyLeaderboard:
    def rank(self, scores: list[StrategyScore]) -> list[StrategyScore]:
        return sorted(scores, key=lambda s: s.score, reverse=True)
