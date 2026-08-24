from datetime import datetime, timezone

import pytest

from oracle.market.features import order_book_imbalance, returns
from oracle.market.models import Candle, OrderBook, OrderBookLevel


def candle(close: float) -> Candle:
    return Candle(
        symbol="BTCUSDT",
        interval="1m",
        timestamp=datetime.now(timezone.utc),
        open=close,
        high=close,
        low=close,
        close=close,
        volume=1.0,
    )


def test_returns() -> None:
    assert returns([candle(100), candle(110)]) == pytest.approx(0.1)


def test_order_book_imbalance() -> None:
    book = OrderBook(
        symbol="BTCUSDT",
        timestamp=datetime.now(timezone.utc),
        bids=(OrderBookLevel(100, 30),),
        asks=(OrderBookLevel(101, 10),),
    )
    assert order_book_imbalance(book) == pytest.approx(0.5)
