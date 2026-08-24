"""Strategy contracts and normalized proposals."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from oracle.core.trader import Action
from oracle.market.models import MarketSnapshot

@dataclass(frozen=True)
class Signal:
    strategy: str
    action: Action
    confidence: float
    rationale: tuple[str, ...]
    invalidation: tuple[str, ...]
    expected_reward_risk: float | None = None

class Strategy(ABC):
    name: str
    @abstractmethod
    def evaluate(self, snapshot: MarketSnapshot) -> Signal: ...
