import pytest

from oracle.execution.fills import FillAggregator
from oracle.execution.orders import OrderIntent, OrderStatus
from oracle.execution.paper_loop import PaperExecutionCoordinator


def make_intent() -> OrderIntent:
    return OrderIntent("client-1", "BTCUSDT", "Buy", 2.0, price=100.0)


def test_paper_order_lifecycle_supports_partial_and_full_fills() -> None:
    coordinator = PaperExecutionCoordinator()

    submitted = coordinator.submit(make_intent())
    assert submitted.accepted
    assert submitted.order.status is OrderStatus.ACKNOWLEDGED

    partial = coordinator.fill("client-1", 0.75, 100.0, fee=0.01)
    assert partial.status is OrderStatus.PARTIALLY_FILLED
    assert partial.filled_quantity == pytest.approx(0.75)
    assert partial.average_fill_price == pytest.approx(100.0)

    filled = coordinator.fill("client-1", 1.25, 102.0, fee=0.02)
    assert filled.status is OrderStatus.FILLED
    assert filled.filled_quantity == pytest.approx(2.0)
    assert filled.average_fill_price == pytest.approx(101.25)

    summary = FillAggregator().summarize(list(coordinator.fills()))
    assert summary.quantity == pytest.approx(2.0)
    assert summary.average_price == pytest.approx(101.25)
    assert summary.fees == pytest.approx(0.03)


def test_paper_submission_is_idempotent() -> None:
    coordinator = PaperExecutionCoordinator()
    first = coordinator.submit(make_intent())
    second = coordinator.submit(make_intent())

    assert first.order == second.order
    assert len(coordinator.fills()) == 0


def test_paper_cancel_blocks_later_fill() -> None:
    coordinator = PaperExecutionCoordinator()
    coordinator.submit(make_intent())
    canceled = coordinator.cancel("client-1")

    assert canceled.status is OrderStatus.CANCELED
    with pytest.raises(ValueError, match="not active"):
        coordinator.fill("client-1", 1.0, 100.0)


def test_paper_reject_blocks_later_fill() -> None:
    coordinator = PaperExecutionCoordinator()
    coordinator.submit(make_intent())
    rejected = coordinator.reject("client-1")

    assert rejected.status is OrderStatus.REJECTED
    with pytest.raises(ValueError, match="not active"):
        coordinator.fill("client-1", 1.0, 100.0)


def test_paper_fill_cannot_exceed_order_quantity() -> None:
    coordinator = PaperExecutionCoordinator()
    coordinator.submit(make_intent())

    with pytest.raises(ValueError, match="exceeds order quantity"):
        coordinator.fill("client-1", 2.1, 100.0)
