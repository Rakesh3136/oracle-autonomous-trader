"""Trader Core: the stateful decision framework for ORACLE.

This module intentionally does not place exchange orders. It represents the
current trader state and converts validated strategy observations into an
explicit thesis that can be passed through the deterministic risk layer.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Mapping


class Action(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"
    CLOSE = "CLOSE"
    REDUCE = "REDUCE"
    HOLD = "HOLD"
    NO_TRADE = "NO_TRADE"


@dataclass(frozen=True)
class Thesis:
    """A trade hypothesis with explicit evidence and invalidation."""

    action: Action
    confidence: float
    evidence: tuple[str, ...]
    alternative: str
    invalidation: tuple[str, ...]
    expected_reward_risk: float | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.expected_reward_risk is not None and self.expected_reward_risk < 0:
            raise ValueError("expected_reward_risk cannot be negative")


@dataclass
class TraderState:
    """Persistent cognitive state; execution remains outside this object."""

    regime: str = "unknown"
    thesis: Thesis | None = None
    recent_decisions: list[Action] = field(default_factory=list)
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_thesis(self, thesis: Thesis) -> None:
        self.thesis = thesis
        self.recent_decisions.append(thesis.action)
        self.recent_decisions = self.recent_decisions[-50:]
        self.last_update = datetime.now(timezone.utc)


class TraderCore:
    """Coordinates market context and thesis formation without placing orders."""

    def __init__(self) -> None:
        self.state = TraderState()

    def observe(self, *, regime: str, evidence: Mapping[str, float]) -> None:
        """Update context; strategy/risk components decide what to do with it."""
        self.state.regime = regime
        self.state.last_update = datetime.now(timezone.utc)

    def form_thesis(
        self,
        *,
        action: Action,
        confidence: float,
        evidence: tuple[str, ...],
        alternative: str,
        invalidation: tuple[str, ...],
        expected_reward_risk: float | None = None,
    ) -> Thesis:
        """Create an auditable thesis; callers must still pass it to risk."""
        thesis = Thesis(
            action=action,
            confidence=confidence,
            evidence=evidence,
            alternative=alternative,
            invalidation=invalidation,
            expected_reward_risk=expected_reward_risk,
        )
        self.state.update_thesis(thesis)
        return thesis
