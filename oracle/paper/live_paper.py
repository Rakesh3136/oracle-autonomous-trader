"""Live Bybit market-data -> AI signal -> paper execution loop.

This module deliberately has no authenticated trading client and cannot place
an exchange order. Bybit is used only as a public market-data source.
"""
import asyncio
from dataclasses import dataclass
from typing import Protocol

from oracle.ai.council import TraderCouncil
from oracle.core.trader import Action
from oracle.execution.order_intent import OrderIntent, OrderType, Side
from oracle.execution.simulator import ExecutionSimulator, SimulatedFill
from oracle.market.models import Candle, MarketSnapshot
from oracle.paper.performance import PaperPerformance, PerformanceReport


class CandleFeed(Protocol):
    async def get_candles(self, symbol: str, interval: str, limit: int = 200) -> list[Candle]: ...

    async def close(self) -> None: ...


@dataclass(frozen=True)
class PaperStep:
    timestamp: object
    price: float
    action: Action
    confidence: float
    opened: bool
    closed: bool


class LivePaperTrader:
    """Consumes fresh Bybit candles and executes every decision only in simulation."""

    def __init__(
        self,
        feed: CandleFeed,
        council: TraderCouncil,
        *,
        symbol: str = "BTCUSDT",
        interval: str = "1",
        quantity: float = 0.001,
        starting_equity: float = 10_000.0,
        slippage_bps: float = 2.0,
        fee_per_trade: float = 0.0,
    ) -> None:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        self.feed = feed
        self.council = council
        self.symbol = symbol.upper()
        self.interval = interval
        self.quantity = quantity
        self.fee_per_trade = fee_per_trade
        self.simulator = ExecutionSimulator(slippage_bps)
        self.performance = PaperPerformance(starting_equity)
        self.position: SimulatedFill | None = None
        self.last_candle_timestamp: object | None = None

    async def step(self) -> PaperStep:
        candles = await self.feed.get_candles(self.symbol, self.interval, 200)
        if len(candles) < 2:
            raise RuntimeError("live paper trader needs at least two candles")
        candle = candles[-1]
        if self.last_candle_timestamp == candle.timestamp:
            return PaperStep(candle.timestamp, candle.close, Action.NO_TRADE, 0.0, False, False)
        self.last_candle_timestamp = candle.timestamp
        snapshot = MarketSnapshot(self.symbol, candle.timestamp, tuple(candles))
        decision = self.council.deliberate(snapshot)
        target_side = (
            Side.BUY if decision.action is Action.LONG
            else Side.SELL if decision.action is Action.SHORT
            else None
        )
        closed = False
        opened = False
        if self.position is not None and (target_side is None or self.position.side is not target_side):
            self.performance.record(
                PaperPerformance.close_fill(self.position, candle.close, self.fee_per_trade)
            )
            self.position = None
            closed = True
        if target_side is not None and self.position is None:
            intent = OrderIntent.make(self.symbol, target_side, OrderType.MARKET, self.quantity)
            self.position = self.simulator.submit(intent, candle.close)
            opened = True
        return PaperStep(candle.timestamp, candle.close, decision.action, decision.confidence, opened, closed)

    def report(self) -> PerformanceReport:
        return self.performance.report()

    async def run_forever(self, poll_seconds: float = 5.0) -> None:
        if poll_seconds <= 0:
            raise ValueError("poll_seconds must be positive")
        try:
            while True:
                await self.step()
                await asyncio.sleep(poll_seconds)
        finally:
            await self.feed.close()
