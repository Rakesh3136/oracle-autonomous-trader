from oracle.exchange.bybit.market_data import BybitPublicCandleParser


def test_bybit_public_candles_are_normalized_chronologically() -> None:
    payload = {
        "result": {
            "list": [
                ["2000", "101", "103", "100", "102", "12"],
                ["1000", "99", "101", "98", "100", "10"],
            ]
        }
    }
    candles = BybitPublicCandleParser().parse(payload)
    assert [c.close for c in candles] == [100.0, 102.0]
    assert all(c.timestamp.tzinfo is not None for c in candles)
