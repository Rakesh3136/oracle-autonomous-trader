"""Fail-closed exchange-state reconciliation primitives."""
from dataclasses import dataclass
from enum import Enum

class ReconciliationStatus(str, Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    UNKNOWN = "unknown"

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

@dataclass(frozen=True)
class LocalPosition:
    symbol: str
    side: str
    quantity: float

@dataclass(frozen=True)
class RemotePosition:
    symbol: str
    side: str
    quantity: float

@dataclass(frozen=True)
class ReconciliationResult:
    status: ReconciliationStatus
    issues: tuple[str, ...]

class Reconciler:
    def compare_orders(self, local: list[LocalOrder], remote: list[RemoteOrder]) -> tuple[str, ...]:
        local_by_id = {o.order_id: o for o in local}
        remote_by_id = {o.order_id: o for o in remote}
        issues: list[str] = []
        for order_id, order in local_by_id.items():
            remote_order = remote_by_id.get(order_id)
            if remote_order is None:
                issues.append(f"missing_remote:{order_id}")
            elif (order.symbol, order.status, order.quantity) != (remote_order.symbol, remote_order.status, remote_order.quantity):
                issues.append(f"mismatch:{order_id}")
        for order_id in remote_by_id:
            if order_id not in local_by_id:
                issues.append(f"unexpected_remote:{order_id}")
        return tuple(issues)

    def compare_positions(self, local: list[LocalPosition], remote: list[RemotePosition], tolerance: float = 1e-8) -> tuple[str, ...]:
        lm = {(p.symbol, p.side): p.quantity for p in local if abs(p.quantity) > tolerance}
        rm = {(p.symbol, p.side): p.quantity for p in remote if abs(p.quantity) > tolerance}
        issues: list[str] = []
        for key in set(lm) | set(rm):
            if abs(lm.get(key, 0.0) - rm.get(key, 0.0)) > tolerance:
                issues.append(f"position_mismatch:{key[0]}:{key[1]}")
        return tuple(issues)

    def reconcile(self, local_orders: list[LocalOrder], remote_orders: list[RemoteOrder],
                  local_positions: list[LocalPosition], remote_positions: list[RemotePosition]) -> ReconciliationResult:
        issues = self.compare_orders(local_orders, remote_orders) + self.compare_positions(local_positions, remote_positions)
        return ReconciliationResult(ReconciliationStatus.MISMATCH if issues else ReconciliationStatus.MATCH, issues)

class ExecutionSafetyGate:
    def allow_new_order(self, result: ReconciliationResult) -> bool:
        return result.status == ReconciliationStatus.MATCH
