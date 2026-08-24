"""Order-flow and derivatives context specialists.

Outputs evidence only; these components cannot submit orders.
"""
from dataclasses import dataclass
from enum import Enum

class Bias(str, Enum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"

@dataclass(frozen=True)
class SpecialistView:
    specialist: str
    bias: Bias
    confidence: float
    rationale: str

class LiquiditySpecialist:
    name = "liquidity"
    def evaluate(self, best_bid: float, best_ask: float, bid_size: float, ask_size: float) -> SpecialistView:
        if best_bid <= 0 or best_ask <= 0 or best_ask < best_bid:
            return SpecialistView(self.name, Bias.NEUTRAL, 0.0, "invalid order book")
        total = bid_size + ask_size
        if total <= 0:
            return SpecialistView(self.name, Bias.NEUTRAL, 0.0, "no displayed liquidity")
        imbalance = (bid_size - ask_size) / total
        bias = Bias.LONG if imbalance > 0 else Bias.SHORT if imbalance < 0 else Bias.NEUTRAL
        spread = (best_ask - best_bid) / ((best_ask + best_bid) / 2)
        confidence = min(1.0, abs(imbalance)) * max(0.0, 1.0 - min(1.0, spread * 100))
        return SpecialistView(self.name, bias, confidence, f"book_imbalance={imbalance:.4f}, spread={spread:.6f}")

class DerivativesSpecialist:
    name = "derivatives"
    def evaluate(self, funding_rate: float | None, open_interest_change: float | None) -> SpecialistView:
        if funding_rate is None or open_interest_change is None:
            return SpecialistView(self.name, Bias.NEUTRAL, 0.0, "missing derivatives context")
        # This is contextual pressure, not a standalone trade signal.
        pressure = -funding_rate * 10.0 + open_interest_change
        bias = Bias.LONG if pressure > 0 else Bias.SHORT if pressure < 0 else Bias.NEUTRAL
        confidence = min(1.0, abs(pressure))
        return SpecialistView(self.name, bias, confidence, f"funding={funding_rate:.6f}, oi_change={open_interest_change:.4f}")
