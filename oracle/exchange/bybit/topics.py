"""Centralized Bybit V5 topic builders."""
def public_topics(symbol: str) -> tuple[str, ...]:
    return (
        f"tickers.{symbol}",
        f"orderbook.50.{symbol}",
        f"kline.1.{symbol}",
    )

def private_topics() -> tuple[str, ...]:
    return ("order", "execution", "position", "wallet")
