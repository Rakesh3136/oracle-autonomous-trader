from dataclasses import dataclass

@dataclass(frozen=True)
class Position:
    symbol: str
    side: str
    quantity: float
    entry_price: float
    leverage: float = 1.0

@dataclass(frozen=True)
class PortfolioSnapshot:
    equity: float
    realized_pnl: float
    unrealized_pnl: float
    positions: tuple[Position, ...] = ()
