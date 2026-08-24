"""Exchange account synchronization boundary for Testnet/paper operation."""
from dataclasses import dataclass
from oracle.execution.reconciliation import LocalOrder, RemoteOrder, LocalPosition, RemotePosition, ReconciliationResult, Reconciler

@dataclass(frozen=True)
class AccountSnapshot:
    equity: float
    available_balance: float
    orders: tuple[RemoteOrder, ...]
    positions: tuple[RemotePosition, ...]

class AccountSync:
    def __init__(self, reconciler: Reconciler | None = None) -> None:
        self.reconciler = reconciler or Reconciler()

    def reconcile(self, local_orders: list[LocalOrder], local_positions: list[LocalPosition],
                  remote: AccountSnapshot) -> ReconciliationResult:
        return self.reconciler.reconcile(
            local_orders, list(remote.orders), local_positions, list(remote.positions)
        )

    def validate_snapshot(self, snapshot: AccountSnapshot) -> None:
        if snapshot.equity < 0 or snapshot.available_balance < 0:
            raise ValueError("exchange account balances cannot be negative")
        if snapshot.available_balance > snapshot.equity + 1e-8:
            raise ValueError("available balance exceeds equity")
