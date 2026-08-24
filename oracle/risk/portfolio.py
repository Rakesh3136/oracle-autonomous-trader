"""Portfolio-level capital allocation, concentration limits and kill switch."""
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class PortfolioRiskConfig:
    risk_per_trade: float = 0.005
    max_portfolio_heat: float = 0.02
    max_leverage: float = 5.0
    max_daily_loss: float = 0.03
    max_position_notional_fraction: float = 0.25
    max_total_notional_fraction: float = 0.50
    max_open_positions: int = 5
    max_drawdown: float = 0.10


@dataclass(frozen=True)
class PortfolioSnapshot:
    equity: float
    daily_pnl: float
    drawdown: float
    gross_exposure: float
    open_positions: int


@dataclass(frozen=True)
class SizingDecision:
    approved: bool
    quantity: float
    notional: float
    reasons: tuple[str, ...]


class PortfolioRisk:
    """Read-only portfolio gate used by the runtime decision boundary."""

    def __init__(self, config: PortfolioRiskConfig | None = None) -> None:
        self.config = config or PortfolioRiskConfig()
        self.reason = ""

    def evaluate(self, snapshot: PortfolioSnapshot) -> bool:
        if snapshot.equity <= 0 or not isfinite(snapshot.equity):
            self.reason = "invalid equity"
            return False
        if snapshot.daily_pnl <= -snapshot.equity * self.config.max_daily_loss:
            self.reason = "daily loss limit reached"
            return False
        if snapshot.drawdown >= self.config.max_drawdown:
            self.reason = "maximum drawdown reached"
            return False
        if snapshot.open_positions >= self.config.max_open_positions:
            self.reason = "maximum open positions reached"
            return False
        if snapshot.gross_exposure > snapshot.equity * self.config.max_total_notional_fraction:
            self.reason = "portfolio exposure limit reached"
            return False
        self.reason = "portfolio risk approved"
        return True


class PortfolioRiskManager:
    def __init__(self, config: PortfolioRiskConfig | None = None) -> None:
        self.config = config or PortfolioRiskConfig()
        self._halted = False
        self._halt_reason = ""

    def size(
        self,
        context: PortfolioContext,
        entry: float,
        stop: float,
        leverage: float = 1.0,
    ) -> SizingDecision:
        reasons: list[str] = []
        if self._halted:
            reasons.append(f"global kill switch: {self._halt_reason}")
        if context.equity <= 0 or not isfinite(context.equity):
            reasons.append("invalid equity")
        if entry <= 0 or stop <= 0 or entry == stop:
            reasons.append("invalid entry/stop")
        if context.daily_pnl_fraction <= -self.config.max_daily_loss:
            reasons.append("daily loss limit reached")
        if context.current_heat >= self.config.max_portfolio_heat:
            reasons.append("portfolio heat limit reached")
        if leverage <= 0 or leverage > self.config.max_leverage:
            reasons.append("leverage limit exceeded")
        if context.open_positions >= self.config.max_open_positions:
            reasons.append("maximum open positions reached")
        if context.peak_equity and context.equity <= context.peak_equity * (1 - self.config.max_drawdown):
            reasons.append("maximum drawdown reached")
        if reasons:
            return SizingDecision(False, 0.0, 0.0, tuple(reasons))
        risk_per_unit = abs(entry - stop)
        risk_budget = context.equity * self.config.risk_per_trade
        quantity = risk_budget / risk_per_unit
        max_position = context.equity * self.config.max_position_notional_fraction * leverage
        max_total = context.equity * self.config.max_total_notional_fraction * leverage
        quantity = min(
            quantity,
            max_position / entry,
            max(0.0, (max_total - context.existing_notional) / entry),
        )
        notional = quantity * entry
        if notional <= 0:
            return SizingDecision(False, 0.0, 0.0, ("portfolio exposure cap leaves zero size",))
        return SizingDecision(True, quantity, notional, ())

    def trip(self, reason: str) -> None:
        if not reason.strip():
            raise ValueError("kill switch requires a reason")
        self._halted = True
        self._halt_reason = reason

    def reset(self) -> None:
        self._halted = False
        self._halt_reason = ""

    @property
    def halted(self) -> bool:
        return self._halted

    @property
    def halt_reason(self) -> str:
        return self._halt_reason


@dataclass(frozen=True)
class PortfolioContext:
    equity: float
    current_heat: float = 0.0
    daily_pnl_fraction: float = 0.0
    existing_notional: float = 0.0
    open_positions: int = 0
    peak_equity: float | None = None
