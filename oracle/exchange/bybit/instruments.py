"""Exchange instrument constraints used before order construction."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN

@dataclass(frozen=True)
class Instrument:
    symbol: str
    tick_size: Decimal
    qty_step: Decimal
    min_qty: Decimal
    min_notional: Decimal
    max_leverage: Decimal

class InstrumentRules:
    def __init__(self, instrument: Instrument) -> None:
        self.instrument = instrument

    def quantize_qty(self, quantity: Decimal) -> Decimal:
        if quantity < self.instrument.min_qty:
            return Decimal("0")
        steps = (quantity / self.instrument.qty_step).to_integral_value(rounding=ROUND_DOWN)
        return steps * self.instrument.qty_step

    def quantize_price(self, price: Decimal) -> Decimal:
        steps = (price / self.instrument.tick_size).to_integral_value(rounding=ROUND_DOWN)
        return steps * self.instrument.tick_size

    def validate_notional(self, quantity: Decimal, price: Decimal) -> bool:
        return quantity * price >= self.instrument.min_notional
