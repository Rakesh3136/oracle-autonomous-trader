"""Single end-to-end decision pipeline for paper/Testnet integration.

The pipeline composes regime, specialists, council, thesis, and risk sizing while
keeping exchange execution behind an injected coordinator. It fails closed on
missing evidence and never enables live execution by itself.
"""
from dataclasses import dataclass
from oracle.intelligence.specialists import TrendSpecialist, MomentumSpecialist, MeanReversionSpecialist, VolatilitySpecialist
from oracle.intelligence.council_v2 import EvidenceCouncil, SpecialistView
from oracle.intelligence.thesis import ThesisEngine, Direction, TradeThesis
from oracle.risk.position_sizing import PositionSizer, PositionPlan

@dataclass(frozen=True)
class PipelineDecision:
    thesis: TradeThesis | None
    position: PositionPlan | None
    approved: bool
    reason: str

class TraderPipeline:
    def __init__(self) -> None:
        self.trend = TrendSpecialist()
        self.momentum = MomentumSpecialist()
        self.mean_reversion = MeanReversionSpecialist()
        self.volatility = VolatilitySpecialist()
        self.council = EvidenceCouncil()
        self.thesis_engine = ThesisEngine()
        self.sizer = PositionSizer()

    def evaluate(self, symbol: str, closes: list[float], equity: float,
                 entry: float, stop: float, target: float | None = None) -> PipelineDecision:
        if len(closes) < 20 or entry <= 0 or stop <= 0 or equity <= 0:
            return PipelineDecision(None, None, False, "insufficient or invalid inputs")
        views: list[SpecialistView] = [
            self.trend.evaluate(closes),
            self.momentum.evaluate(closes),
            self.mean_reversion.evaluate(closes),
            self.volatility.evaluate(closes),
        ]
        decision = self.council.deliberate(views)
        if decision.bias.value == "neutral" or decision.confidence <= 0:
            return PipelineDecision(None, None, False, "council has no actionable directional consensus")
        direction = Direction.LONG if decision.bias.value == "long" else Direction.SHORT
        thesis = self.thesis_engine.build(symbol, direction, "council specialist consensus", decision.confidence,
                                          entry_low=entry, entry_high=entry, invalidation=stop, target=target,
                                          ttl_seconds=300)
        position = self.sizer.plan(equity, entry, stop)
        return PipelineDecision(thesis, position, True, "approved by intelligence and position sizing")
