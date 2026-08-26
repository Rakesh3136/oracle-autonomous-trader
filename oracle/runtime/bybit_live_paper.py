"""Live-market-data paper trader for Bybit public data.

This service uses public Bybit market data only. It retrains the transparent
baseline on labels whose future outcomes are already known, then predicts the
newest candle using features available at that candle. Orders are always sent
to the local paper simulator; this module has no authenticated order client.
"""
import asyncio
from dataclasses import dataclass

from oracle.exchange.bybit.public_rest import BybitPublicRest
from oracle.execution.order_intent import OrderIntent, OrderType, Side
from oracle.execution.simulator import ExecutionSimulator, SimulatedFill
from oracle.learning.dataset import Candle as LearningCandle
from oracle.learning.dataset_builder import TrainingDatasetBuilder
from oracle.learning.features import FeatureEngine
from oracle.learning.model import LogisticBaseline
from oracle.learning.economics import TradeEconomicsEngine
from oracle.paper.performance import PaperPerformance, PerformanceReport


@dataclass(frozen=True)
class LivePaperSnapshot:
    symbol: str
    price: float
    probability_up: float
    approved: bool
    reason: str
    report: PerformanceReport


class BybitLivePaperTrader:
    """Retrain on known historical outcomes and paper-trade the newest data."""

    def __init__(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "1",
        starting_equity: float = 10_000.0,
        poll_seconds: float = 60.0,
        testnet_public: bool = True,
    ) -> None:
        if poll_seconds <= 0:
            raise ValueError("poll_seconds must be positive")
        self.symbol = symbol.upper()
        self.interval = interval
        self.poll_seconds = poll_seconds
        self.exchange = BybitPublicRest(testnet=testnet_public)
        self.model = LogisticBaseline()
        self.dataset = TrainingDatasetBuilder()
        self.features = FeatureEngine()
        self.economics = TradeEconomicsEngine()
        self.simulator = ExecutionSimulator(slippage_bps=2.0)
        self.performance = PaperPerformance(starting_equity)
        self.open_fill: SimulatedFill | None = None

    @staticmethod
    def _learning_candles(candles: list[object]) -> list[LearningCandle]:
        return [
            LearningCandle(
                timestamp=c.timestamp,
                symbol=c.symbol,
                open=c.open,
                high=c.high,
                low=c.low,
                close=c.close,
                volume=c.volume,
            )
            for c in candles
        ]

    async def cycle(self) -> LivePaperSnapshot:
        candles = await self.exchange.get_candles(self.symbol, self.interval, 200)
        if len(candles) < 60:
            raise RuntimeError("not enough live candles for paper model")

        learning_candles = self._learning_candles(candles)
        rows = self.dataset.build(learning_candles, horizon=5, regime_window=20)
        if len(rows) < 40:
            raise RuntimeError("not enough labeled historical candles for training")

        # The newest candle has no known future outcome. Train only on older
        # labeled rows, then infer on the newest feature row without using its label.
        self.model.fit(rows[:-1])
        feature_rows = self.features.transform(learning_candles)
        latest_feature = feature_rows[-1]
        probability = self.model.probability_up(latest_feature)
        price = candles[-1].close

        target_return = 0.006
        stop_return = 0.004
        economics = self.economics.evaluate(probability, target_return, stop_return)
        approved = economics.trade_allowed
        reason = economics.reason

        if self.open_fill is not None:
            self.performance.record(
                PaperPerformance.close_fill(self.open_fill, price, fees=0.0006 * self.open_fill.quantity * self.open_fill.fill_price)
            )
            self.open_fill = None

        if approved:
            side = Side.BUY if probability >= 0.5 else Side.SELL
            intent = OrderIntent.make(self.symbol, side, OrderType.MARKET, 1.0)
            self.open_fill = self.simulator.submit(intent, price)

        return LivePaperSnapshot(
            self.symbol,
            price,
            probability,
            approved,
            reason,
            self.performance.report(),
        )

    async def run_forever(self) -> None:
        try:
            while True:
                snapshot = await self.cycle()
                print(
                    f"{snapshot.symbol} price={snapshot.price:.2f} "
                    f"p_up={snapshot.probability_up:.3f} approved={snapshot.approved} "
                    f"trades={snapshot.report.trades} "
                    f"win_rate={snapshot.report.win_rate:.2%} "
                    f"equity={snapshot.report.equity:.2f} "
                    f"drawdown={snapshot.report.max_drawdown:.2f}"
                )
                await asyncio.sleep(self.poll_seconds)
        finally:
            await self.exchange.close()
