"""Stateful multi-source market snapshot assembly."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from oracle.market.models import Candle, DerivativesState, MarketSnapshot, OrderBook
from oracle.market.orderbook import OrderBookBuilder

@dataclass
class MarketState:
    symbol: str
    candles: list[Candle] = field(default_factory=list)
    orderbook: OrderBookBuilder = field(default_factory=OrderBookBuilder)
    derivatives: DerivativesState | None = None

    def add_candle(self, candle: Candle, max_candles: int = 500) -> None:
        if candle.symbol != self.symbol:
            raise ValueError("candle symbol does not match market state")
        self.candles.append(candle)
        self.candles = self.candles[-max_candles:]

    def snapshot(self) -> MarketSnapshot:
        bids, asks = self.orderbook.levels()
        book = OrderBook(self.symbol, datetime.now(timezone.utc), bids, asks) if bids or asks else None
        return MarketSnapshot(self.symbol, datetime.now(timezone.utc), tuple(self.candles), book, self.derivatives)

    def data_quality(self) -> float:
        score = 0.0
        if self.candles:
            score += 0.5
        if self.orderbook.levels()[0] or self.orderbook.levels()[1]:
            score += 0.3
        if self.derivatives is not None:
            score += 0.2
        return score
