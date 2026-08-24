"""Human-style trade thesis and explicit setup/playbook gate."""
from dataclasses import dataclass
from enum import Enum

class SetupType(str, Enum):
    NONE = "none"
    TREND_PULLBACK = "trend_pullback"
    BREAKOUT = "breakout"
    MEAN_REVERSION = "mean_reversion"
    REVERSAL = "reversal"

@dataclass(frozen=True)
class TradeThesis:
    symbol: str
    setup: SetupType
    direction: str
    rationale: tuple[str, ...]
    entry: float
    invalidation: float
    target: float
    confidence: float
    valid: bool

class PlaybookEngine:
    def build_thesis(self, symbol: str, setup: SetupType, direction: str,
                     rationale: list[str], entry: float, invalidation: float,
                     target: float, confidence: float) -> TradeThesis:
        if direction not in {"LONG", "SHORT"}:
            raise ValueError("direction must be LONG or SHORT")
        if not rationale:
            return TradeThesis(symbol, SetupType.NONE, direction, (), entry, invalidation, target, 0.0, False)
        if min(entry, invalidation, target) <= 0 or not 0 <= confidence <= 1:
            raise ValueError("invalid thesis parameters")
        if direction == "LONG":
            valid_geometry = invalidation < entry < target
        else:
            valid_geometry = target < entry < invalidation
        valid = setup != SetupType.NONE and valid_geometry and confidence >= 0.60
        return TradeThesis(symbol, setup, direction, tuple(rationale), entry, invalidation, target, confidence, valid)

    def should_wait(self, thesis: TradeThesis | None) -> bool:
        return thesis is None or not thesis.valid
