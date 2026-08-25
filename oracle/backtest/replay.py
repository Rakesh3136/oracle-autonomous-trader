"""Chronological, deterministic market replay for paper-trading research."""
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Iterable

from oracle.backtest.ledger import LedgerSummary, TradeLedger


@dataclass(frozen=True)
class MarketTick:
    timestamp: datetime
    symbol: str
    price: float
    volume: float = 0.0


@dataclass(frozen=True)
class ReplayTrade:
    trade_id: str
    symbol: str
    side: int
    entry_index: int
    exit_index: int
    quantity: float
    entry_price: float
    exit_price: float
    fees: float = 0.0


@dataclass(frozen=True)
class ReplayResult:
    ticks: int
    decisions: int
    errors: tuple[str, ...]
    summary: LedgerSummary
    equity_curve: tuple[float, ...]


class MarketReplay:
    """Feeds supplied historical data strictly in order; never sorts or looks ahead."""

    def run(
        self,
        ticks: Iterable[MarketTick],
        on_tick: Callable[[MarketTick], bool],
        starting_equity: float = 10_000.0,
    ) -> ReplayResult:
        ordered = list(ticks)
        if not ordered:
            raise ValueError("replay requires at least one tick")
        ledger = TradeLedger(starting_equity)
        errors: list[str] = []
        decisions = 0
        previous: datetime | None = None
        symbol = ordered[0].symbol
        for tick in ordered:
            if tick.symbol != symbol:
                errors.append(f"symbol changed at {tick.timestamp.isoformat()}")
                continue
            if tick.price <= 0:
                errors.append(f"invalid price at {tick.timestamp.isoformat()}")
                continue
            if previous is not None and tick.timestamp <= previous:
                errors.append(f"non-monotonic timestamp at {tick.timestamp.isoformat()}")
                continue
            previous = tick.timestamp
            try:
                if on_tick(tick):
                    decisions += 1
            except Exception as exc:  # noqa: BLE001 — replay records callback failures.
                errors.append(f"tick handler error: {type(exc).__name__}")
        return ReplayResult(
            len(ordered),
            decisions,
            tuple(errors),
            ledger.summary(),
            tuple(point.equity for point in ledger.equity_curve()),
        )

    def record_trades(
        self,
        ticks: list[MarketTick],
        trades: Iterable[ReplayTrade],
        starting_equity: float = 10_000.0,
    ) -> ReplayResult:
        if not ticks:
            raise ValueError("replay requires at least one tick")
        ledger = TradeLedger(starting_equity)
        errors: list[str] = []
        ordered_trades = sorted(trades, key=lambda item: (item.exit_index, item.trade_id))
        for trade in ordered_trades:
            if not 0 <= trade.entry_index < trade.exit_index < len(ticks):
                errors.append(f"invalid trade indexes: {trade.trade_id}")
                continue
            if trade.symbol != ticks[trade.entry_index].symbol or trade.symbol != ticks[trade.exit_index].symbol:
                errors.append(f"trade symbol mismatch: {trade.trade_id}")
                continue
            ledger.record(
                ticks[trade.exit_index].timestamp,
                trade.trade_id,
                trade.symbol,
                trade.side,
                trade.quantity,
                trade.entry_price,
                trade.exit_price,
                trade.fees,
            )
        return ReplayResult(
            len(ticks),
            len(ordered_trades) - len(errors),
            tuple(errors),
            ledger.summary(),
            tuple(point.equity for point in ledger.equity_curve()),
        )
