"""Replay-driven paper runtime combining market replay and paper execution."""
from dataclasses import dataclass
from oracle.backtest.replay import MarketTick, MarketReplay
from oracle.runtime.paper_runner import PaperRunner

@dataclass(frozen=True)
class PaperReplayResult:
    ticks: int
    approved: int
    errors: tuple[str, ...]

class PaperReplayRunner:
    def __init__(self, slippage_bps: float = 2.0) -> None:
        self.runner = PaperRunner(slippage_bps)

    def run(self, ticks: list[MarketTick], equity: float, stop_distance: float) -> PaperReplayResult:
        prices: list[float] = []
        approved = 0
        errors: list[str] = []

        def on_tick(tick: MarketTick) -> bool:
            nonlocal approved
            prices.append(tick.price)
            if len(prices) < 20:
                return False
            try:
                result = self.runner.run_once(tick.symbol, prices[-100:], equity,
                                              tick.price, max(0.0000001, tick.price - stop_distance))
                if result.approved:
                    approved += 1
                    return True
            except Exception as exc:  # noqa: BLE001 — paper replay records strategy failures.
                errors.append(type(exc).__name__)
            return False

        replay = MarketReplay().run(ticks, on_tick)
        errors.extend(replay.errors)
        return PaperReplayResult(replay.ticks, approved, tuple(errors))
