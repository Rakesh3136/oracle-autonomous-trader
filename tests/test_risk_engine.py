from oracle.core.trader import Action, Thesis
from oracle.risk.engine import RiskContext, RiskDecision, RiskEngine, RiskLimits


def make_thesis(action: Action = Action.LONG, rr: float = 2.0) -> Thesis:
    return Thesis(
        action=action,
        confidence=0.8,
        evidence=("test evidence",),
        alternative="invalid thesis",
        invalidation=("test invalidation",),
        expected_reward_risk=rr,
    )


def test_risk_approves_valid_proposal() -> None:
    result = RiskEngine().evaluate(
        make_thesis(),
        RiskContext(equity=10_000, daily_pnl=0, drawdown=0.01, proposed_notional=500, leverage=2),
    )
    assert result.decision is RiskDecision.APPROVE


def test_risk_rejects_excessive_drawdown() -> None:
    result = RiskEngine().evaluate(
        make_thesis(),
        RiskContext(equity=10_000, daily_pnl=0, drawdown=0.20, proposed_notional=500, leverage=2),
    )
    assert result.decision is RiskDecision.REJECT
    assert "maximum drawdown reached" in result.reasons


def test_no_trade_is_never_executed() -> None:
    result = RiskEngine(RiskLimits()).evaluate(
        make_thesis(Action.NO_TRADE),
        RiskContext(equity=10_000, daily_pnl=0, drawdown=0, proposed_notional=0, leverage=0),
    )
    assert result.decision is RiskDecision.REJECT
