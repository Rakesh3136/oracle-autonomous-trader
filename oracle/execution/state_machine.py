"""Deterministic order lifecycle state machine.

Exchange adapters translate venue-specific events into these states. Invalid
transitions fail closed instead of silently changing execution state.
"""
from enum import Enum

class OrderState(str, Enum):
    NEW = "new"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"
    UNKNOWN = "unknown"

_TERMINAL = {OrderState.FILLED, OrderState.CANCELED, OrderState.REJECTED}
_ALLOWED = {
    OrderState.NEW: {OrderState.SUBMITTED, OrderState.CANCELED},
    OrderState.SUBMITTED: {OrderState.ACKNOWLEDGED, OrderState.PARTIAL, OrderState.FILLED, OrderState.CANCELED, OrderState.REJECTED, OrderState.UNKNOWN},
    OrderState.ACKNOWLEDGED: {OrderState.PARTIAL, OrderState.FILLED, OrderState.CANCELED, OrderState.REJECTED, OrderState.UNKNOWN},
    OrderState.PARTIAL: {OrderState.PARTIAL, OrderState.FILLED, OrderState.CANCELED, OrderState.UNKNOWN},
    OrderState.FILLED: set(),
    OrderState.CANCELED: set(),
    OrderState.REJECTED: set(),
    OrderState.UNKNOWN: {OrderState.ACKNOWLEDGED, OrderState.PARTIAL, OrderState.FILLED, OrderState.CANCELED, OrderState.REJECTED, OrderState.UNKNOWN},
}

class OrderStateMachine:
    def __init__(self, state: OrderState = OrderState.NEW) -> None:
        self.state = state

    def transition(self, new_state: OrderState) -> OrderState:
        if self.state in _TERMINAL:
            if new_state != self.state:
                raise ValueError(f"terminal order cannot transition from {self.state} to {new_state}")
            return self.state
        if new_state not in _ALLOWED[self.state]:
            raise ValueError(f"invalid order transition: {self.state} -> {new_state}")
        self.state = new_state
        return self.state
