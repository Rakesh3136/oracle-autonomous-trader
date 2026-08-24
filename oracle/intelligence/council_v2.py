"""Evidence-weighted specialist council with explicit disagreement handling.

This is a research/decision layer only. Risk and execution gates remain authoritative.
"""
from dataclasses import dataclass
from enum import Enum

class Bias(str, Enum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"

@dataclass(frozen=True)
class SpecialistView:
    specialist: str
    bias: Bias
    confidence: float
    rationale: str

@dataclass(frozen=True)
class CouncilDecision:
    bias: Bias
    confidence: float
    agreement: float
    views: tuple[SpecialistView, ...]
    dissent: tuple[SpecialistView, ...]

class EvidenceCouncil:
    def deliberate(self, views: list[SpecialistView]) -> CouncilDecision:
        if not views:
            return CouncilDecision(Bias.NEUTRAL, 0.0, 0.0, (), ())
        scores = {Bias.LONG: 0.0, Bias.SHORT: 0.0, Bias.NEUTRAL: 0.0}
        for view in views:
            scores[view.bias] += min(1.0, max(0.0, view.confidence))
        directional = scores[Bias.LONG] + scores[Bias.SHORT]
        if directional == 0 or scores[Bias.LONG] == scores[Bias.SHORT]:
            return CouncilDecision(Bias.NEUTRAL, 0.0, 0.0, tuple(views), tuple(v for v in views if v.bias != Bias.NEUTRAL))
        winner = Bias.LONG if scores[Bias.LONG] > scores[Bias.SHORT] else Bias.SHORT
        opposing = Bias.SHORT if winner is Bias.LONG else Bias.LONG
        agreement = sum(1 for v in views if v.bias is winner) / max(1, sum(1 for v in views if v.bias is not Bias.NEUTRAL))
        confidence = scores[winner] / directional
        dissent = tuple(v for v in views if v.bias is opposing)
        return CouncilDecision(winner, confidence, agreement, tuple(views), dissent)
