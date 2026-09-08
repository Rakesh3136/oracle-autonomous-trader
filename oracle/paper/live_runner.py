"""Live Bybit public-market-data to paper-decision runner."""
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Protocol, Sequence

from oracle.execution.order_intent import OrderIntent, OrderType, Side
from oracle.execution.simulator import ExecutionSimulator, SimulatedFill
from oracle.intelligence.thesis import Direction
from oracle.market.models import Candle
from oracle.risk.portfolio import PortfolioSnapshot
from oracle.runtime.runtime_service import OracleRuntime


class CandleSource(Protocol):
    async def get_candles(self, symbol: str, interval: str, limit: int = 200) -> Sequence[Candle]: ...


@dataclass(frozen=True)
class PaperCycle:
    timestamp: datetime
    symbol: str
    close: float
    approved: bool
    reason: str
    side: Side | None = None
    quantity: float = 0.0
    fill: SimulatedFill | None = None


class LivePaperRunner:
    """Poll completed public candles and route them through paper execution only."""

    def __init__(self, source: CandleSource, *, symbol: str = "BTCUSDT", interval: str = "1",
                 equity: float = 10_000.0, history_size: int = 200, slippage_bps: float = 2.0,
                 event_log: str | Path | None = None) -> None:
        if equity <= 0 or history_size < 20:
            raise ValueError("equity must be positive and history_size must be at least 20")
        self.source = source
        self.symbol = symbol.upper()
        self.interval = interval
        self.equity = equity
        self.history: deque[Candle] = deque(maxlen=history_size)
        self.runtime = OracleRuntime()
        self.simulator = ExecutionSimulator(slippage_bps)
        self.event_log = Path(event_log) if event_log is not None else None
        self._last_processed: datetime | None = None

    async def step(self, now: datetime | None = None) -> PaperCycle | None:
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        candles = await self.source.get_candles(self.symbol, self.interval, self.history.maxlen)
        completed = [c for c in candles if c.timestamp + self._interval_delta() <= current]
        completed.sort(key=lambda candle: candle.timestamp)
        if not completed:
            return None
        new_candles = [c for c in completed if self._last_processed is None or c.timestamp > self._last_processed]
        if not new_candles:
            return None
        for candle in new_candles[:-1]:
            self._append_unique(candle)
        candle = new_candles[-1]
        self._last_processed = candle.timestamp
        self._append_unique(candle)
        closes = [item.close for item in self.history]
        if len(closes) < 20:
            return self._record(PaperCycle(candle.timestamp, self.symbol, candle.close, False, "warming up"))
        preliminary = self.runtime.pipeline.evaluate(
            self.symbol, closes, self.equity, candle.close, candle.close * 0.99
        )
        if not preliminary.approved or preliminary.thesis is None:
            return self._record(PaperCycle(candle.timestamp, self.symbol, candle.close, False, preliminary.reason))
        stop = candle.close * (1.01 if preliminary.thesis.direction is Direction.SHORT else 0.99)
        snapshot = PortfolioSnapshot(self.equity, 0.0, 0.0, 0.0, 0)
        result = self.runtime.evaluate(self.symbol, closes, self.equity, candle.close, stop,
                                       snapshot, [], "crypto")
        if not result.approved or preliminary.position is None:
            return self._record(PaperCycle(candle.timestamp, self.symbol, candle.close, False, result.reason))
        side = Side.BUY if preliminary.thesis.direction is Direction.LONG else Side.SELL
        intent = OrderIntent.make(self.symbol, side, OrderType.MARKET, preliminary.position.quantity)
        fill = self.simulator.submit(intent, candle.close)
        return self._record(PaperCycle(candle.timestamp, self.symbol, candle.close, True,
                                       result.reason, side, preliminary.position.quantity, fill))

    def _append_unique(self, candle: Candle) -> None:
        if not self.history or candle.timestamp > self.history[-1].timestamp:
            self.history.append(candle)

    def _interval_delta(self) -> timedelta:
        if self.interval == "D":
            return timedelta(days=1)
        if self.interval == "W":
            return timedelta(days=7)
        if self.interval == "M":
            return timedelta(days=30)
        return timedelta(minutes=int(self.interval))

    def _record(self, cycle: PaperCycle) -> PaperCycle:
        if self.event_log is None:
            return cycle
        self.event_log.parent.mkdir(parents=True, exist_ok=True)
        payload = {"timestamp": cycle.timestamp.isoformat(), "symbol": cycle.symbol,
                   "close": cycle.close, "approved": cycle.approved, "reason": cycle.reason,
                   "side": cycle.side.value if cycle.side else None, "quantity": cycle.quantity,
                   "fill_price": cycle.fill.fill_price if cycle.fill else None}
        with self.event_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, separators=(",", ":")) + "\n")
        return cycle
