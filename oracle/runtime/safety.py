"""Runtime safety supervisor with fail-closed behavior."""
from dataclasses import dataclass

@dataclass(frozen=True)
class SafetyState:
    trading_allowed: bool
    reason: str

class SafetySupervisor:
    def __init__(self) -> None:
        self._state = SafetyState(True, "healthy")

    def trip(self, reason: str) -> None:
        if not reason.strip():
            raise ValueError("safety trip requires a reason")
        self._state = SafetyState(False, reason)

    def reset(self) -> None:
        self._state = SafetyState(True, "manually reset")

    def state(self) -> SafetyState:
        return self._state

    def assert_trading_allowed(self) -> None:
        if not self._state.trading_allowed:
            raise PermissionError(f"trading blocked: {self._state.reason}")
