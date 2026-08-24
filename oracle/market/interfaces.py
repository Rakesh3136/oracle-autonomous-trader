"""Interfaces separating market intelligence from exchange-specific code."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime

from oracle.market.models import Candle, DerivativesState, MarketSnapshot, OrderBook


class MarketDataProvider(ABC):
    """Provider contract consumed by ORACLE's market layer."""

    @abstractmethod
    async def candles(self, symbol: str, interval: str, limit: int = 200) -> list[Candle]:
        raise NotImplementedError

    @abstractmethod
    async def order_book(self, symbol: str, depth: int = 50) -> OrderBook:
        raise NotImplementedError

    @abstractmethod
    async def derivatives(self, symbol: str) -> DerivativesState:
        raise NotImplementedError

    @abstractmethod
    async def stream(self, symbols: list[str]) -> AsyncIterator[MarketSnapshot]:
        raise NotImplementedError

    @abstractmethod
    async def health(self) -> bool:
        raise NotImplementedError
