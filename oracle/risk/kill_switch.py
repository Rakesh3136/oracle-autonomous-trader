from dataclasses import dataclass

@dataclass(frozen=True)
class SafetyState:
    trading_enabled: bool = False
    reason: str = "live trading disabled by default"

class KillSwitch:
    def __init__(self) -> None:
        self.state = SafetyState()

    def disable(self, reason: str) -> None:
        self.state = SafetyState(False, reason)

    def enable(self, explicit_reason: str) -> None:
        if not explicit_reason.strip():
            raise ValueError("explicit reason required")
        self.state = SafetyState(True, explicit_reason)

    def can_trade(self) -> bool:
        return self.state.trading_enabled
