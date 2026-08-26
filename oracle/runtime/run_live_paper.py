"""CLI entry point for Bybit public-data paper trading."""
import argparse
import asyncio

from oracle.runtime.bybit_live_paper import BybitLivePaperTrader


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ORACLE on live Bybit market data in paper mode")
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--interval", default="1")
    parser.add_argument("--poll-seconds", type=float, default=60.0)
    parser.add_argument("--starting-equity", type=float, default=10_000.0)
    parser.add_argument(
        "--mainnet-data",
        action="store_true",
        help="use Bybit mainnet public market data; orders remain local paper orders",
    )
    args = parser.parse_args()
    trader = BybitLivePaperTrader(
        symbol=args.symbol,
        interval=args.interval,
        poll_seconds=args.poll_seconds,
        starting_equity=args.starting_equity,
        testnet_public=not args.mainnet_data,
    )
    asyncio.run(trader.run_forever())


if __name__ == "__main__":
    main()
