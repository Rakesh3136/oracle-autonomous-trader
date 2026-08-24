"""Regime-conditioned trading memory for research and evaluation."""
from dataclasses import dataclass
from collections import defaultdict

@dataclass(frozen=True)
class RegimeOutcome:
    regime: str
    strategy: str
    trades: int
    wins: int
    pnl: float

    @property
    def win_rate(self) -> float:
        return self.wins / self.trades if self.trades else 0.0

class RegimeMemory:
    def summarize(self, observations: list[tuple[str, str, float]]) -> tuple[RegimeOutcome, ...]:
        groups: dict[tuple[str, str], list[float]] = defaultdict(list)
        for regime, strategy, pnl in observations:
            groups[(regime, strategy)].append(pnl)
        result = []
        for (regime, strategy), pnls in sorted(groups.items()):
            result.append(RegimeOutcome(regime, strategy, len(pnls), sum(p > 0 for p in pnls), sum(pnls)))
        return tuple(result)

    def preferred_strategy(self, regime: str, outcomes: tuple[RegimeOutcome, ...], min_trades: int = 20) -> str | None:
        candidates = [o for o in outcomes if o.regime == regime and o.trades >= min_trades]
        if not candidates:
            return None
        return max(candidates, key=lambda o: (o.pnl, o.win_rate)).strategy
