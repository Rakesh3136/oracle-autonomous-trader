"""Authoritative exchange-vs-local reconciliation models."""
from dataclasses import dataclass
from enum import Enum

class DiscrepancyType(str, Enum):
    MISSING_LOCAL_ORDER = "missing_local_order"
    MISSING_EXCHANGE_ORDER = "missing_exchange_order"
    STATUS_MISMATCH = "status_mismatch"
    QUANTITY_MISMATCH = "quantity_mismatch"
    POSITION_MISMATCH = "position_mismatch"
    UNEXPECTED_POSITION = "unexpected_position"

@dataclass(frozen=True)
class ReconciliationFinding:
    kind: DiscrepancyType
    symbol: str
    reference: str
    local_value: str
    exchange_value: str
    severity: str = "high"
