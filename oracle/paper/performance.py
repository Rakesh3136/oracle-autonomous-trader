"""Paper-trading performance accounting."""
from dataclasses import dataclass
from oracle.execution.simulator import SimulatedFill
from oracle.execution.order_intent import Side

@dataclass(frozen=True)
class ClosedTrade:
    symbol: str
    side: Side
    quantity: float
    entry_price: float
    exit_price: float
    pnl: float
    fees: float

@dataclass(frozen=True)
class PerformanceReport:
    trades: int
    wins: int
    losses: int
    win_rate: float
    net_pnl: float
    fees: float
    equity: float
    max_drawdown: float

class PaperPerformance:
    def __init__(self, starting_equity: float) -> None:
        if starting_equity <= 0:
            raise ValueError("starting_equity must be positive")
        self.starting_equity = starting_equity
        self._trades: list[ClosedTrade] = []

    def record(self, trade: ClosedTrade) -> None:
        if trade.quantity <= 0 or trade.entry_price <= 0 or trade.exit_price <= 0:
            raise ValueError("trade values must be positive")
        self._trades.append(trade)

    def report(self) -> PerformanceReport:
        pnl = sum(t.pnl for t in self._trades)
        fees = sum(t.fees for t in self._trades)
        wins = sum(1 for t in self._trades if t.pnl - t.fees > 0)
        losses = sum(1 for t in self._trades if t.pnl - t.fees < 0)
        trades = len(self._trades)
        equity = self.starting_equity + pnl - fees
        running = self.starting_equity
        peak = running
        max_drawdown = 0.0
        for trade in self._trades:
            running += trade.pnl - trade.fees
            peak = max(peak, running)
            max_drawdown = max(max_drawdown, peak - running)
        return PerformanceReport(trades, wins, losses, wins / trades if trades else 0.0,
                                 pnl, fees, equity, max_drawdown)

    @staticmethod
    def close_fill(entry: SimulatedFill, exit_price: float, fees: float = 0.0) -> ClosedTrade:
        if exit_price <= 0 or fees < 0:
            raise ValueError("invalid exit price or fees")
        direction = 1.0 if entry.side is Side.BUY else -1.0
        pnl = (exit_price - entry.fill_price) * entry.quantity * direction
        return ClosedTrade(entry.symbol, entry.side, entry.quantity, entry.fill_price,
                           exit_price, pnl, fees)
