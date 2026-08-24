"""Bounded decision memory for audit and future learning."""
from dataclasses import dataclass
from datetime import datetime
from oracle.core.trader import Action

@dataclass(frozen=True)
class DecisionMemory:
    timestamp: datetime
    symbol: str
    action: Action
    confidence: float
    regime: str
    thesis: str
    outcome: float | None = None

class TraderMemory:
    def __init__(self, capacity: int = 10_000) -> None:
        self.capacity = capacity
        self.items: list[DecisionMemory] = []

    def remember(self, item: DecisionMemory) -> None:
        self.items.append(item)
        if len(self.items) > self.capacity:
            del self.items[:-self.capacity]
