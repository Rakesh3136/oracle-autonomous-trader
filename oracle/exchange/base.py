"""Exchange contracts. Business logic must depend on these interfaces, not Bybit payloads."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from oracle.market.models import Candle, DerivativesState, OrderBook


class ExchangeAdapter(ABC):
    @abstractmethod
    async def get_candles(self, symbol: str, interval: str, limit: int = 200) -> Sequence[Candle]:
        raise NotImplementedError

    @abstractmethod
    async def get_order_book(self, symbol: str, depth: int = 50) -> OrderBook:
        raise NotImplementedError

    @abstractmethod
    async def get_derivatives(self, symbol: str) -> DerivativesState:
        raise NotImplementedError

    @abstractmethod
    async def health(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError
