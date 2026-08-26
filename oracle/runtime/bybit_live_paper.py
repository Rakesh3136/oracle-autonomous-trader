"""Live-market-data paper trader for Bybit public data.

Public Bybit data drives the model, while every order remains local paper
execution. No authenticated order client is used here.
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
from oracle.market.models import Candle
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
    """Retrain on matured outcomes and paper-trade each newly closed candle."""

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
        self.last_processed_timestamp = None

    @staticmethod
    def _learning_candles(candles: list[Candle]) -> list[LearningCandle]:
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

        # Bybit's final REST kline can still be forming. Use the previous candle
        # as the only fully closed bar so the model never trains/predicts on a
        # partially formed candle.
        closed_candle = candles[-2]
        if self.last_processed_timestamp == closed_candle.timestamp:
            return LivePaperSnapshot(
                self.symbol,
                closed_candle.close,
                0.5,
                False,
                "waiting for a new closed candle",
                self.performance.report(),
            )

        learning_candles = self._learning_candles(candles[:-1])
        rows = self.dataset.build(learning_candles, horizon=5, regime_window=20)
        if len(rows) < 40:
            raise RuntimeError("not enough labeled historical candles for training")

        # All training rows have matured future outcomes. The newest closed
        # candle is prediction-only and its future label is not used.
        self.model.fit(rows)
        feature_rows = self.features.transform(learning_candles)
        latest_feature = feature_rows[-1]
        probability = self.model.probability_up(latest_feature)
        price = closed_candle.close

        economics = self.economics.evaluate(probability, 0.006, 0.004)
        approved = economics.trade_allowed
        reason = economics.reason

        if self.open_fill is not None:
            self.performance.record(
                PaperPerformance.close_fill(
                    self.open_fill,
                    price,
                    fees=0.0006 * self.open_fill.quantity * self.open_fill.fill_price,
                )
            )
            self.open_fill = None

        if approved:
            side = Side.BUY if probability >= 0.5 else Side.SELL
            intent = OrderIntent.make(self.symbol, side, OrderType.MARKET, 1.0)
            self.open_fill = self.simulator.submit(intent, price)

        self.last_processed_timestamp = closed_candle.timestamp
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
