"""Explicit environment gates prevent accidental live execution."""
from enum import Enum

class Environment(str, Enum):
    PAPER = "paper"
    TESTNET = "testnet"
    LIVE = "live"

class EnvironmentGate:
    def __init__(self, environment: Environment = Environment.PAPER) -> None:
        self.environment = environment

    def allows_live_orders(self) -> bool:
        return self.environment is Environment.LIVE

    def assert_allowed(self, live_order: bool) -> None:
        if live_order and not self.allows_live_orders():
            raise PermissionError(f"live order blocked in {self.environment.value} environment")
