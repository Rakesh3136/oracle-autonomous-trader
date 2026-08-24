"""Backtest performance analytics with explicit trade-level accounting."""
from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=True)
class TradeRecord:
    symbol: str
    entry_price: float
    exit_price: float
    quantity: float
    side: str
    fees: float = 0.0
    slippage: float = 0.0

    @property
    def gross_pnl(self) -> float:
        direction = 1.0 if self.side.lower() == "long" else -1.0
        return (self.exit_price - self.entry_price) * self.quantity * direction

    @property
    def net_pnl(self) -> float:
        return self.gross_pnl - self.fees - self.slippage

@dataclass(frozen=True)
class PerformanceReport:
    starting_equity: float
    ending_equity: float
    total_return: float
    total_trades: int
    win_rate: float
    profit_factor: float | None
    max_drawdown: float
    sharpe_like: float | None

class PerformanceAnalyzer:
    def analyze(self, starting_equity: float, trades: list[TradeRecord]) -> PerformanceReport:
        if starting_equity <= 0:
            raise ValueError("starting_equity must be positive")
        pnl = [t.net_pnl for t in trades]
        equity = starting_equity
        peak = equity
        max_dd = 0.0
        for value in pnl:
            equity += value
            peak = max(peak, equity)
            max_dd = max(max_dd, (peak - equity) / peak if peak else 0.0)
        wins = sum(v > 0 for v in pnl)
        gross_profit = sum(v for v in pnl if v > 0)
        gross_loss = -sum(v for v in pnl if v < 0)
        profit_factor = gross_profit / gross_loss if gross_loss else None
        if len(pnl) > 1:
            avg = sum(pnl) / len(pnl)
            variance = sum((v - avg) ** 2 for v in pnl) / (len(pnl) - 1)
            std = variance ** 0.5
            sharpe_like = avg / std * sqrt(len(pnl)) if std else None
        else:
            sharpe_like = None
        return PerformanceReport(starting_equity, equity, equity / starting_equity - 1,
                                len(trades), wins / len(trades) if trades else 0.0,
                                profit_factor, max_dd, sharpe_like)
