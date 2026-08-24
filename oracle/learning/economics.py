"""Trade-economics gate: costs, risk/reward, and conservative expected value."""
from dataclasses import dataclass

@dataclass(frozen=True)
class TradeEconomics:
    gross_edge: float
    fees: float
    funding: float
    slippage: float
    net_edge: float
    reward_risk: float
    expected_value: float
    trade_allowed: bool
    reason: str

class TradeEconomicsEngine:
    def evaluate(self, probability_win: float, target_return: float,
                 stop_return: float, fee_rate: float = 0.0006,
                 funding_rate: float = 0.0, slippage_rate: float = 0.0003,
                 min_expected_value: float = 0.0,
                 min_reward_risk: float = 1.2) -> TradeEconomics:
        if not 0 <= probability_win <= 1:
            raise ValueError("probability_win must be between 0 and 1")
        if target_return <= 0 or stop_return <= 0:
            raise ValueError("target_return and stop_return must be positive")
        costs = max(0.0, fee_rate) + abs(funding_rate) + max(0.0, slippage_rate)
        gross_edge = probability_win * target_return - (1.0 - probability_win) * stop_return
        net_edge = gross_edge - costs
        reward_risk = target_return / stop_return
        expected_value = net_edge
        allowed = expected_value > min_expected_value and reward_risk >= min_reward_risk
        reason = "positive net expectancy" if allowed else "insufficient net expectancy or reward/risk"
        return TradeEconomics(gross_edge, fee_rate, funding_rate, slippage_rate,
                              net_edge, reward_risk, expected_value, allowed, reason)
