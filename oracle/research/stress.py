"""Deterministic stress scenarios for research validation."""
from dataclasses import dataclass

@dataclass(frozen=True)
class StressScenario:
    name: str
    fee_multiplier: float = 1.0
    slippage_multiplier: float = 1.0
    return_shock: float = 0.0

DEFAULT_SCENARIOS = (
    StressScenario("baseline"),
    StressScenario("high_fees", fee_multiplier=2.0),
    StressScenario("poor_liquidity", slippage_multiplier=3.0),
    StressScenario("adverse_gap", return_shock=-0.05),
)
