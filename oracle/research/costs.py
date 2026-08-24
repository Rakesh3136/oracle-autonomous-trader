"""Research transaction-cost model."""
from dataclasses import dataclass

@dataclass(frozen=True)
class CostModel:
    fee_rate: float = 0.0006
    slippage_bps: float = 2.0
    funding_rate_per_interval: float = 0.0

    def round_trip_cost(self, entry_notional: float, exit_notional: float) -> float:
        fees = (entry_notional + exit_notional) * self.fee_rate
        slippage = (entry_notional + exit_notional) * self.slippage_bps / 100_000
        return fees + slippage

    def funding_cost(self, notional: float, intervals: int, side: int) -> float:
        return notional * self.funding_rate_per_interval * intervals * side
