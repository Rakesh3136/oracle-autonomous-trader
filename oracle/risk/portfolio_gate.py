"""Fail-closed portfolio risk gate for order intents."""
from dataclasses import dataclass

@dataclass(frozen=True)
class PortfolioSnapshot:
    equity: float
    daily_pnl: float
    drawdown: float
    gross_exposure: float
    open_positions: int

@dataclass(frozen=True)
class RiskApproval:
    approved: bool
    risk_amount: float
    quantity: float
    reason: str

class PortfolioRiskGate:
    def __init__(self, risk_per_trade: float = 0.005, max_daily_loss: float = 0.02,
                 max_drawdown: float = 0.10, max_exposure: float = 1.0,
                 max_positions: int = 5) -> None:
        if not 0 < risk_per_trade <= 0.05:
            raise ValueError("risk_per_trade must be between 0 and 5%")
        self.risk_per_trade = risk_per_trade
        self.max_daily_loss = max_daily_loss
        self.max_drawdown = max_drawdown
        self.max_exposure = max_exposure
        self.max_positions = max_positions

    def approve(self, snapshot: PortfolioSnapshot, stop_distance: float,
                price: float, requested_exposure: float = 0.0) -> RiskApproval:
        if snapshot.equity <= 0 or price <= 0 or stop_distance <= 0:
            return RiskApproval(False, 0.0, 0.0, "invalid portfolio or trade parameters")
        if snapshot.daily_pnl <= -snapshot.equity * self.max_daily_loss:
            return RiskApproval(False, 0.0, 0.0, "daily loss limit reached")
        if snapshot.drawdown >= self.max_drawdown:
            return RiskApproval(False, 0.0, 0.0, "maximum drawdown reached")
        if snapshot.open_positions >= self.max_positions:
            return RiskApproval(False, 0.0, 0.0, "maximum open positions reached")
        if snapshot.gross_exposure + max(0.0, requested_exposure) > self.max_exposure:
            return RiskApproval(False, 0.0, 0.0, "portfolio exposure limit reached")
        risk_amount = snapshot.equity * self.risk_per_trade
        quantity = risk_amount / stop_distance
        return RiskApproval(True, risk_amount, quantity, "portfolio risk approved")
