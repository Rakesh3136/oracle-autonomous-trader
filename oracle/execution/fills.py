"""Fill aggregation and position-relevant execution accounting."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Fill:
    order_id: str
    quantity: float
    price: float
    fee: float = 0.0

@dataclass(frozen=True)
class FillSummary:
    quantity: float
    average_price: float | None
    fees: float

class FillAggregator:
    def summarize(self, fills: list[Fill]) -> FillSummary:
        quantity = sum(f.quantity for f in fills)
        fees = sum(f.fee for f in fills)
        average = (sum(f.quantity * f.price for f in fills) / quantity) if quantity else None
        return FillSummary(quantity, average, fees)
