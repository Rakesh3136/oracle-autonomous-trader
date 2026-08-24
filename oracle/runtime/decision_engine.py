"""Unified decision-to-order-intent chain with fail-closed behavior."""
from dataclasses import dataclass
from oracle.learning.council import TradingCouncil, CouncilDecision
from oracle.learning.economics import TradeEconomicsEngine, TradeEconomics

@dataclass(frozen=True)
class OrderIntent:
    symbol: str
    side: str
    probability_up: float
    expected_value: float
    reward_risk: float
    confidence: float
    approved: bool
    reason: str

class DecisionEngine:
    def __init__(self, council: TradingCouncil, economics: TradeEconomicsEngine | None = None) -> None:
        self.council = council
        self.economics = economics or TradeEconomicsEngine()

    def evaluate(self, symbol: str, row, target_return: float, stop_return: float,
                 fee_rate: float = 0.0006, funding_rate: float = 0.0,
                 slippage_rate: float = 0.0003) -> OrderIntent:
        council: CouncilDecision = self.council.decide(row)
        if not council.trade_allowed:
            return OrderIntent(symbol, "NONE", council.probability_up, 0.0, 0.0,
                               council.confidence, False, council.reason)
        economics: TradeEconomics = self.economics.evaluate(
            council.probability_up, target_return, stop_return,
            fee_rate, funding_rate, slippage_rate)
        if not economics.trade_allowed:
            return OrderIntent(symbol, "NONE", council.probability_up,
                               economics.expected_value, economics.reward_risk,
                               council.confidence, False, economics.reason)
        side = "BUY" if council.probability_up >= 0.5 else "SELL"
        return OrderIntent(symbol, side, council.probability_up,
                           economics.expected_value, economics.reward_risk,
                           council.confidence, True, "council + economics approved")
