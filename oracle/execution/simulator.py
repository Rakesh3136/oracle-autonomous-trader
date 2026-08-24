"""Deterministic paper/Testnet-style execution simulator.

No network calls and no real orders. Useful for end-to-end integration tests,
state-machine testing, and replaying generated order intents.
"""
from dataclasses import dataclass
from oracle.execution.order_intent import OrderIntent, Side

@dataclass(frozen=True)
class SimulatedFill:
    intent_id: str
    symbol: str
    quantity: float
    fill_price: float
    side: Side

class ExecutionSimulator:
    def __init__(self, slippage_bps: float = 0.0) -> None:
        if slippage_bps < 0:
            raise ValueError("slippage_bps must be non-negative")
        self.slippage_bps = slippage_bps
        self.fills: list[SimulatedFill] = []

    def submit(self, intent: OrderIntent, market_price: float) -> SimulatedFill:
        if market_price <= 0:
            raise ValueError("market_price must be positive")
        factor = 1 + self.slippage_bps / 10_000
        fill_price = market_price * (factor if intent.side is Side.BUY else 2 - factor)
        fill = SimulatedFill(intent.intent_id, intent.symbol, intent.quantity, fill_price, intent.side)
        self.fills.append(fill)
        return fill
