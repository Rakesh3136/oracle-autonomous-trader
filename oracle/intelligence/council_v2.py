"""Evidence-weighted specialist council with explicit disagreement handling.

This is a research/decision layer only. Risk and execution gates remain authoritative.
"""
from dataclasses import dataclass
from enum import Enum

from oracle.intelligence.specialists import SpecialistView


class Bias(str, Enum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


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
            try:
                bias = Bias(view.bias.value)
            except ValueError:
                bias = Bias.NEUTRAL
            scores[bias] += min(1.0, max(0.0, view.confidence))
        directional = scores[Bias.LONG] + scores[Bias.SHORT]
        if directional == 0 or scores[Bias.LONG] == scores[Bias.SHORT]:
            return CouncilDecision(
                Bias.NEUTRAL,
                0.0,
                0.0,
                tuple(views),
                tuple(v for v in views if v.bias.value != Bias.NEUTRAL.value),
            )
        winner = Bias.LONG if scores[Bias.LONG] > scores[Bias.SHORT] else Bias.SHORT
        agreement = sum(1 for v in views if v.bias.value == winner.value) / max(
            1, sum(1 for v in views if v.bias.value != Bias.NEUTRAL.value)
        )
        confidence = scores[winner] / directional
        dissent = tuple(v for v in views if v.bias.value not in {winner.value, Bias.NEUTRAL.value})
        return CouncilDecision(winner, confidence, agreement, tuple(views), dissent)
