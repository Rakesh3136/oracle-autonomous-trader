"""Deterministic event-driven backtest primitives."""
from dataclasses import dataclass
from collections.abc import Sequence
from oracle.market.models import Candle

@dataclass(frozen=True)
class BacktestConfig:
    initial_equity: float = 10_000.0
    fee_rate: float = 0.0006
    slippage_bps: float = 2.0

@dataclass(frozen=True)
class BacktestTrade:
    symbol: str
    entry: float
    exit: float
    quantity: float
    gross_pnl: float
    fees: float
    net_pnl: float

@dataclass(frozen=True)
class BacktestResult:
    initial_equity: float
    final_equity: float
    trades: tuple[BacktestTrade, ...]
    max_drawdown: float

class BacktestEngine:
    """Simple event-driven baseline; intentionally no look-ahead execution."""
    def __init__(self, config: BacktestConfig | None = None) -> None:
        self.config = config or BacktestConfig()

    def round_trip(self, candles: Sequence[Candle], entry_index: int, exit_index: int, quantity: float) -> BacktestTrade:
        if not (0 <= entry_index < exit_index < len(candles)):
            raise ValueError("invalid trade indices")
        entry = candles[entry_index].close * (1 + self.config.slippage_bps / 100_000)
        exit = candles[exit_index].close * (1 - self.config.slippage_bps / 100_000)
        gross = (exit - entry) * quantity
        fees = (entry * quantity + exit * quantity) * self.config.fee_rate
        return BacktestTrade(candles[0].symbol, entry, exit, quantity, gross, fees, gross - fees)

    def run_round_trips(self, candles: Sequence[Candle], trades: Sequence[tuple[int, int, float]]) -> BacktestResult:
        equity = self.config.initial_equity
        peak = equity
        max_dd = 0.0
        results: list[BacktestTrade] = []
        for entry, exit, qty in trades:
            trade = self.round_trip(candles, entry, exit, qty)
            equity += trade.net_pnl
            peak = max(peak, equity)
            max_dd = max(max_dd, (peak - equity) / peak)
            results.append(trade)
        return BacktestResult(self.config.initial_equity, equity, tuple(results), max_dd)
