"""Hard fail-closed execution kill switch."""
from dataclasses import dataclass

@dataclass(frozen=True)
class KillSwitchState:
    enabled: bool
    reason: str

class KillSwitch:
    def __init__(self) -> None:
        self._state = KillSwitchState(False, "not triggered")

    @property
    def state(self) -> KillSwitchState:
        return self._state

    def trigger(self, reason: str) -> KillSwitchState:
        if not reason:
            raise ValueError("kill-switch reason is required")
        self._state = KillSwitchState(True, reason)
        return self._state

    def reset(self, explicit: bool = False) -> KillSwitchState:
        if not explicit:
            raise PermissionError("explicit reset required")
        self._state = KillSwitchState(False, "manually reset")
        return self._state

    def allow_execution(self) -> bool:
        return not self._state.enabled
