"""Trade and model evaluation metrics."""
from math import sqrt
from collections.abc import Sequence

def profit_factor(pnls: Sequence[float]) -> float:
    gains = sum(x for x in pnls if x > 0)
    losses = -sum(x for x in pnls if x < 0)
    return float("inf") if losses == 0 and gains > 0 else (gains / losses if losses else 0.0)

def sharpe(pnls: Sequence[float]) -> float:
    if len(pnls) < 2:
        return 0.0
    mean = sum(pnls) / len(pnls)
    variance = sum((x - mean) ** 2 for x in pnls) / (len(pnls) - 1)
    return mean / sqrt(variance) if variance else 0.0

def max_drawdown(equity_curve: Sequence[float]) -> float:
    peak = 0.0
    worst = 0.0
    for equity in equity_curve:
        peak = max(peak, equity)
        if peak > 0:
            worst = max(worst, (peak - equity) / peak)
    return worst
