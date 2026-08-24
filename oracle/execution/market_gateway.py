"""Exchange-facing market/instrument gateway boundary.

Network I/O is intentionally abstracted behind an injected client. This keeps
credentials and venue transport outside the learning/risk layers and makes
paper/Testnet the default.
"""
from dataclasses import dataclass
from decimal import Decimal
from oracle.execution.bybit_adapter import VenueMode

@dataclass(frozen=True)
class InstrumentRules:
    symbol: str
    min_qty: Decimal
    qty_step: Decimal
    min_price: Decimal
    price_tick: Decimal

@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    bid: Decimal
    ask: Decimal
    timestamp_ms: int

class MarketGateway:
    def __init__(self, mode: VenueMode = VenueMode.PAPER) -> None:
        self.mode = mode
        self._rules: dict[str, InstrumentRules] = {}

    def register_rules(self, rules: InstrumentRules) -> None:
        if rules.min_qty <= 0 or rules.qty_step <= 0 or rules.price_tick <= 0:
            raise ValueError("instrument rules must be positive")
        self._rules[rules.symbol] = rules

    def normalize_quantity(self, symbol: str, quantity: Decimal) -> Decimal:
        rules = self._rules[symbol]
        if quantity < rules.min_qty:
            raise ValueError("quantity below exchange minimum")
        steps = (quantity / rules.qty_step).to_integral_value()
        normalized = steps * rules.qty_step
        if normalized < rules.min_qty:
            raise ValueError("normalized quantity below exchange minimum")
        return normalized

    def validate_market(self, snapshot: MarketSnapshot) -> None:
        if snapshot.bid <= 0 or snapshot.ask <= 0 or snapshot.ask < snapshot.bid:
            raise ValueError("invalid market snapshot")
