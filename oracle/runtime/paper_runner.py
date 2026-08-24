"""Safe paper runner composing the decision pipeline with simulated execution."""
from dataclasses import dataclass
from oracle.runtime.pipeline import TraderPipeline
from oracle.execution.order_intent import OrderIntent, OrderType, Side
from oracle.execution.simulator import ExecutionSimulator, SimulatedFill

@dataclass(frozen=True)
class PaperRunResult:
    approved: bool
    reason: str
    fill: SimulatedFill | None

class PaperRunner:
    def __init__(self, slippage_bps: float = 2.0) -> None:
        self.pipeline = TraderPipeline()
        self.simulator = ExecutionSimulator(slippage_bps)

    def run_once(self, symbol: str, closes: list[float], equity: float,
                 entry: float, stop: float, target: float | None = None) -> PaperRunResult:
        decision = self.pipeline.evaluate(symbol, closes, equity, entry, stop, target)
        if not decision.approved or decision.thesis is None or decision.position is None:
            return PaperRunResult(False, decision.reason, None)
        side = Side.BUY if decision.thesis.direction.value == "long" else Side.SELL
        intent = OrderIntent.make(symbol, side, OrderType.MARKET, decision.position.quantity)
        fill = self.simulator.submit(intent, entry)
        return PaperRunResult(True, decision.reason, fill)
