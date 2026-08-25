from oracle.execution.reconciliation import (
    ExecutionSafetyGate,
    LocalOrder,
    LocalPosition,
    ReconciliationStatus,
    Reconciler,
    RemoteOrder,
    RemotePosition,
)


def test_matching_orders_and_positions_allow_new_orders() -> None:
    local_orders = [LocalOrder("o1", "BTCUSDT", "filled", 2.0)]
    remote_orders = [RemoteOrder("o1", "BTCUSDT", "filled", 2.0)]
    local_positions = [LocalPosition("BTCUSDT", "Buy", 2.0)]
    remote_positions = [RemotePosition("BTCUSDT", "Buy", 2.0)]

    result = Reconciler().reconcile(
        local_orders, remote_orders, local_positions, remote_positions
    )

    assert result.status is ReconciliationStatus.MATCH
    assert result.issues == ()
    assert ExecutionSafetyGate().allow_new_order(result)


def test_missing_remote_order_blocks_new_orders() -> None:
    result = Reconciler().reconcile(
        [LocalOrder("o1", "BTCUSDT", "acknowledged", 1.0)],
        [],
        [],
        [],
    )

    assert result.status is ReconciliationStatus.MISMATCH
    assert result.issues == ("missing_remote:o1",)
    assert not ExecutionSafetyGate().allow_new_order(result)


def test_unexpected_remote_position_blocks_new_orders() -> None:
    result = Reconciler().reconcile(
        [],
        [],
        [],
        [RemotePosition("BTCUSDT", "Buy", 1.0)],
    )

    assert result.status is ReconciliationStatus.MISMATCH
    assert "position_mismatch:BTCUSDT:Buy" in result.issues
    assert not ExecutionSafetyGate().allow_new_order(result)


def test_position_tolerance_does_not_create_false_mismatch() -> None:
    result = Reconciler().reconcile(
        [LocalOrder("o1", "BTCUSDT", "filled", 1.0)],
        [RemoteOrder("o1", "BTCUSDT", "filled", 1.0)],
        [LocalPosition("BTCUSDT", "Buy", 1.0)],
        [RemotePosition("BTCUSDT", "Buy", 1.0 + 5e-9)],
    )

    assert result.status is ReconciliationStatus.MATCH
