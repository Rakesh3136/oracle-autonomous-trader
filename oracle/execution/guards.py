"""Production-oriented execution guards; all live paths remain opt-in."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ExecutionPolicy:
    live_enabled: bool = False
    max_order_notional: float = 1_000.0
    max_orders_per_minute: int = 10

class ExecutionGuard:
    def __init__(self, policy: ExecutionPolicy | None = None) -> None:
        self.policy = policy or ExecutionPolicy()
        self._orders = 0

    def authorize(self, notional: float) -> tuple[bool, str]:
        if not self.policy.live_enabled:
            return False, "live trading disabled"
        if notional <= 0:
            return False, "notional must be positive"
        if notional > self.policy.max_order_notional:
            return False, "order exceeds notional limit"
        if self._orders >= self.policy.max_orders_per_minute:
            return False, "order-rate limit reached"
        self._orders += 1
        return True, "approved"
