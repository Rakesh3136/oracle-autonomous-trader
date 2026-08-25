"""Bybit V5 public REST market-data adapter.

Only public market-data endpoints live here. Trading/account endpoints will be
added behind separate authenticated interfaces after paper execution exists.
"""
from datetime import datetime, timezone
from typing import Any, cast

import httpx

from oracle.exchange.base import ExchangeAdapter
from oracle.market.models import Candle, DerivativesState, OrderBook, OrderBookLevel


class BybitPublicRest(ExchangeAdapter):
    CATEGORY = "linear"

    def __init__(self, *, testnet: bool = True, timeout: float = 10.0) -> None:
        self.base_url = "https://api-testnet.bybit.com" if testnet else "https://api.bybit.com"
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        response = await self._client.get(path, params=params)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise TypeError("Bybit API returned a non-object response")
        if payload.get("retCode") != 0:
            raise RuntimeError(f"Bybit API error: {payload.get('retCode')} {payload.get('retMsg')}")
        result = payload.get("result")
        if not isinstance(result, dict):
            raise TypeError("Bybit API response has an invalid result")
        return cast(dict[str, Any], result)

    async def get_candles(self, symbol: str, interval: str, limit: int = 200) -> list[Candle]:
        result = await self._get(
            "/v5/market/kline",
            {"category": self.CATEGORY, "symbol": symbol.upper(), "interval": interval, "limit": limit},
        )
        rows = result.get("list", [])
        if not isinstance(rows, list):
            raise TypeError("Bybit kline result has an invalid list")
        candles: list[Candle] = []
        for row in reversed(rows):
            if not isinstance(row, list) or len(row) < 6:
                raise RuntimeError("Bybit kline row has an invalid shape")
            candles.append(
                Candle(
                    symbol=symbol.upper(),
                    interval=interval,
                    timestamp=datetime.fromtimestamp(int(row[0]) / 1000, tz=timezone.utc),
                    open=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                    volume=float(row[5]),
                )
            )
        return candles

    async def get_order_book(self, symbol: str, depth: int = 50) -> OrderBook:
        result = await self._get(
            "/v5/market/orderbook",
            {"category": self.CATEGORY, "symbol": symbol.upper(), "limit": depth},
        )
        bids = result.get("b", [])
        asks = result.get("a", [])
        if not isinstance(bids, list) or not isinstance(asks, list):
            raise TypeError("Bybit order book result has an invalid shape")
        return OrderBook(
            symbol=symbol.upper(),
            timestamp=datetime.fromtimestamp(int(result["ts"]) / 1000, tz=timezone.utc),
            bids=tuple(OrderBookLevel(float(price), float(qty)) for price, qty in bids),
            asks=tuple(OrderBookLevel(float(price), float(qty)) for price, qty in asks),
        )

    async def get_derivatives(self, symbol: str) -> DerivativesState:
        symbol = symbol.upper()
        ticker = await self._get(
            "/v5/market/tickers", {"category": self.CATEGORY, "symbol": symbol}
        )
        items = ticker.get("list", [])
        if not isinstance(items, list) or not items:
            raise RuntimeError("Bybit ticker result is empty")
        item = items[0]
        if not isinstance(item, dict):
            raise TypeError("Bybit ticker item has an invalid shape")
        funding = item.get("fundingRate")
        open_interest = item.get("openInterest")
        return DerivativesState(
            symbol=symbol,
            timestamp=datetime.now(timezone.utc),
            funding_rate=float(funding) if funding not in (None, "") else None,
            open_interest=float(open_interest) if open_interest not in (None, "") else None,
            mark_price=float(item["markPrice"]) if item.get("markPrice") else None,
            index_price=float(item["indexPrice"]) if item.get("indexPrice") else None,
        )

    async def health(self) -> bool:
        try:
            await self._get("/v5/market/time", {})
            return True
        except (httpx.HTTPError, RuntimeError, TypeError, KeyError, ValueError):
            return False

    async def close(self) -> None:
        await self._client.aclose()
