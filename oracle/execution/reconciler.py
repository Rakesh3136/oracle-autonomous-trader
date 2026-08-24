"""Exchange-state reconciliation primitives."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ReconciliationResult:
    consistent: bool
    reasons: tuple[str, ...]

class PositionReconciler:
    def compare(self, internal_qty: float, exchange_qty: float, tolerance: float = 1e-8) -> ReconciliationResult:
        if abs(internal_qty - exchange_qty) <= tolerance:
            return ReconciliationResult(True, ())
        return ReconciliationResult(False, ("internal/exchange position mismatch",))
