"""Execution coordinator joining intents, lifecycle state, and reconciliation hooks.

The coordinator is exchange-agnostic: a venue adapter supplies submission and
query callbacks. Unknown outcomes fail closed and require reconciliation before
execution can continue.
"""
from dataclasses import dataclass
from typing import Callable
from oracle.execution.order_intent import OrderIntent, IntentRegistry
from oracle.execution.state_machine import OrderState, OrderStateMachine

@dataclass(frozen=True)
class ExecutionResult:
    intent_id: str
    state: OrderState
    message: str

class ExecutionCoordinator:
    def __init__(self, registry: IntentRegistry | None = None) -> None:
        self.registry = registry or IntentRegistry()
        self._machines: dict[str, OrderStateMachine] = {}
        self._halted = False

    def submit(self, intent: OrderIntent, send: Callable[[OrderIntent], bool]) -> ExecutionResult:
        if self._halted:
            return ExecutionResult(intent.intent_id, OrderState.UNKNOWN, "execution halted")
        if self.registry.seen(intent.intent_id):
            machine = self._machines[intent.intent_id]
            return ExecutionResult(intent.intent_id, machine.state, "duplicate intent suppressed")
        machine = OrderStateMachine()
        self._machines[intent.intent_id] = machine
        try:
            accepted = bool(send(intent))
        except Exception:
            machine.transition(OrderState.UNKNOWN)
            self._halted = True
            return ExecutionResult(intent.intent_id, machine.state, "submission exception; reconciliation required")
        if not accepted:
            machine.transition(OrderState.REJECTED)
            return ExecutionResult(intent.intent_id, machine.state, "exchange adapter rejected submission")
        machine.transition(OrderState.SUBMITTED)
        self.registry.mark_submitted(intent.intent_id)
        return ExecutionResult(intent.intent_id, machine.state, "submitted; awaiting exchange acknowledgement")

    def reconcile(self, intent_id: str, authoritative_state: OrderState) -> ExecutionResult:
        machine = self._machines.get(intent_id)
        if machine is None:
            return ExecutionResult(intent_id, OrderState.UNKNOWN, "unknown intent; manual reconciliation required")
        try:
            machine.transition(authoritative_state)
        except ValueError:
            self._halted = True
            return ExecutionResult(intent_id, OrderState.UNKNOWN, "invalid reconciliation transition; execution halted")
        return ExecutionResult(intent_id, machine.state, "reconciled")

    @property
    def halted(self) -> bool:
        return self._halted
