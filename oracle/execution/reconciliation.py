"""Exchange-state reconciliation primitives."""
from dataclasses import dataclass

@dataclass(frozen=True)
class LocalOrder:
    order_id: str
    symbol: str
    status: str
    quantity: float

@dataclass(frozen=True)
class RemoteOrder:
    order_id: str
    symbol: str
    status: str
    quantity: float

class Reconciler:
    def compare(self, local: list[LocalOrder], remote: list[RemoteOrder]) -> tuple[str, ...]:
        local_by_id = {o.order_id: o for o in local}
        remote_by_id = {o.order_id: o for o in remote}
        issues: list[str] = []
        for order_id, order in local_by_id.items():
            remote_order = remote_by_id.get(order_id)
            if remote_order is None:
                issues.append(f"missing_remote:{order_id}")
            elif (order.status, order.quantity) != (remote_order.status, remote_order.quantity):
                issues.append(f"mismatch:{order_id}")
        for order_id in remote_by_id:
            if order_id not in local_by_id:
                issues.append(f"unexpected_remote:{order_id}")
        return tuple(issues)
