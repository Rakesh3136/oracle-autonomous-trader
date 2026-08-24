"""Conservative USDT-perpetual accounting primitives for research simulations."""
from dataclasses import dataclass

@dataclass(frozen=True)
class PerpetualConfig:
    maintenance_margin_rate: float = 0.005
    funding_interval_hours: int = 8

@dataclass(frozen=True)
class PerpetualPosition:
    entry_price: float
    quantity: float
    leverage: float
    side: int  # +1 long, -1 short

    def unrealized_pnl(self, mark_price: float) -> float:
        return (mark_price - self.entry_price) * self.quantity * self.side

    def initial_margin(self) -> float:
        return abs(self.entry_price * self.quantity) / self.leverage

    def liquidation_buffer(self, mark_price: float, maintenance_rate: float) -> float:
        equity = self.initial_margin() + self.unrealized_pnl(mark_price)
        maintenance = abs(mark_price * self.quantity) * maintenance_rate
        return equity - maintenance

class FundingModel:
    def payment(self, notional: float, funding_rate: float, side: int) -> float:
        return -notional * funding_rate * side
