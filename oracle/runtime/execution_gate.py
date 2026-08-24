"""Final fail-closed execution gate. No exchange call is made here."""
from dataclasses import dataclass
from enum import Enum

class ExecutionMode(str, Enum):
    PAPER = "paper"
    TESTNET = "testnet"
    LIVE = "live"

class OrderState(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass(frozen=True)
class ExecutionConfig:
    mode: ExecutionMode = ExecutionMode.PAPER
    live_enabled: bool = False
    kill_switch: bool = True

@dataclass(frozen=True)
class ExecutionApproval:
    approved: bool
    state: OrderState
    reason: str

class ExecutionGate:
    """Prevents accidental live execution unless every explicit gate is open."""
    def __init__(self, config: ExecutionConfig | None = None) -> None:
        self.config = config or ExecutionConfig()

    def approve(self, decision_approved: bool, risk_approved: bool) -> ExecutionApproval:
        if self.config.kill_switch:
            return ExecutionApproval(False, OrderState.REJECTED, "kill switch active")
        if not decision_approved:
            return ExecutionApproval(False, OrderState.REJECTED, "decision not approved")
        if not risk_approved:
            return ExecutionApproval(False, OrderState.REJECTED, "portfolio risk not approved")
        if self.config.mode is ExecutionMode.LIVE and not self.config.live_enabled:
            return ExecutionApproval(False, OrderState.REJECTED, "live execution explicitly disabled")
        return ExecutionApproval(True, OrderState.APPROVED, f"approved for {self.config.mode.value} mode")

    def transition(self, current: OrderState, target: OrderState) -> OrderState:
        allowed = {
            OrderState.PROPOSED: {OrderState.APPROVED, OrderState.REJECTED, OrderState.CANCELLED},
            OrderState.APPROVED: {OrderState.SUBMITTED, OrderState.CANCELLED},
            OrderState.SUBMITTED: {OrderState.ACKNOWLEDGED, OrderState.REJECTED, OrderState.CANCELLED},
            OrderState.ACKNOWLEDGED: {OrderState.FILLED, OrderState.CANCELLED},
        }
        if target not in allowed.get(current, set()):
            raise ValueError(f"invalid order transition: {current.value} -> {target.value}")
        return target
