"""Research performance metrics."""
from math import sqrt
from statistics import mean, pstdev


def total_return(initial: float, final: float) -> float:
    if initial <= 0:
        raise ValueError("initial equity must be positive")
    return final / initial - 1.0


def sharpe(returns: list[float], periods_per_year: float = 365.0) -> float:
    if len(returns) < 2:
        return 0.0
    deviation = pstdev(returns)
    if deviation == 0:
        return 0.0
    return mean(returns) / deviation * sqrt(periods_per_year)


def profit_factor(pnls: list[float]) -> float:
    gross_profit = sum(p for p in pnls if p > 0)
    gross_loss = -sum(p for p in pnls if p < 0)
    return float("inf") if gross_loss == 0 and gross_profit > 0 else (gross_profit / gross_loss if gross_loss else 0.0)
