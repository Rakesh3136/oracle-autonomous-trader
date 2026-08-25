"""Deterministic paper-trading ledger and equity accounting."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LedgerEntry:
    timestamp: datetime
    trade_id: str
    symbol: str
    side: int
    quantity: float
    entry_price: float
    exit_price: float
    gross_pnl: float
    fees: float
    net_pnl: float


@dataclass(frozen=True)
class EquityPoint:
    timestamp: datetime
    equity: float
    realized_pnl: float
    fees: float


@dataclass(frozen=True)
class LedgerSummary:
    starting_equity: float
    ending_equity: float
    realized_pnl: float
    fees: float
    trades: int
    wins: int
    losses: int

    @property
    def return_pct(self) -> float:
        if self.starting_equity == 0:
            return 0.0
        return (self.ending_equity / self.starting_equity - 1.0) * 100.0


class TradeLedger:
    """Append-only realized-trade ledger with deterministic equity snapshots."""

    def __init__(self, starting_equity: float) -> None:
        if starting_equity <= 0:
            raise ValueError("starting equity must be positive")
        self.starting_equity = starting_equity
        self._entries: list[LedgerEntry] = []
        self._equity: list[EquityPoint] = []

    def record(
        self,
        timestamp: datetime,
        trade_id: str,
        symbol: str,
        side: int,
        quantity: float,
        entry_price: float,
        exit_price: float,
        fees: float = 0.0,
    ) -> LedgerEntry:
        if side not in {-1, 1}:
            raise ValueError("side must be 1 for long or -1 for short")
        if quantity <= 0 or entry_price <= 0 or exit_price <= 0:
            raise ValueError("quantity and prices must be positive")
        if fees < 0:
            raise ValueError("fees cannot be negative")
        if any(entry.trade_id == trade_id for entry in self._entries):
            raise ValueError(f"duplicate trade id: {trade_id}")
        gross = (exit_price - entry_price) * quantity * side
        entry = LedgerEntry(
            timestamp,
            trade_id,
            symbol,
            side,
            quantity,
            entry_price,
            exit_price,
            gross,
            fees,
            gross - fees,
        )
        self._entries.append(entry)
        previous = self._equity[-1].equity if self._equity else self.starting_equity
        realized = sum(item.gross_pnl for item in self._entries)
        total_fees = sum(item.fees for item in self._entries)
        self._equity.append(EquityPoint(timestamp, previous + entry.net_pnl, realized, total_fees))
        return entry

    def entries(self) -> tuple[LedgerEntry, ...]:
        return tuple(self._entries)

    def equity_curve(self) -> tuple[EquityPoint, ...]:
        return tuple(self._equity)

    def summary(self) -> LedgerSummary:
        realized = sum(entry.net_pnl for entry in self._entries)
        fees = sum(entry.fees for entry in self._entries)
        ending = self.starting_equity + realized
        wins = sum(entry.net_pnl > 0 for entry in self._entries)
        losses = sum(entry.net_pnl < 0 for entry in self._entries)
        return LedgerSummary(
            self.starting_equity,
            ending,
            realized,
            fees,
            len(self._entries),
            wins,
            losses,
        )
