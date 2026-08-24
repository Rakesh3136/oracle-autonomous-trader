from oracle.core.trader import Action, TraderCore


def test_trader_forms_auditable_thesis() -> None:
    trader = TraderCore()
    trader.observe(regime="trend_up", evidence={"trend_strength": 0.8})

    thesis = trader.form_thesis(
        action=Action.LONG,
        confidence=0.78,
        evidence=("higher highs", "positive order-flow imbalance"),
        alternative="false breakout and return to range",
        invalidation=("break below structure",),
        expected_reward_risk=2.1,
    )

    assert thesis.action is Action.LONG
    assert trader.state.thesis == thesis
    assert trader.state.regime == "trend_up"
