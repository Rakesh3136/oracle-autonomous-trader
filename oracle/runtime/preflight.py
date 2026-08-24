"""Operational preflight gate for paper/Testnet deployment.

This gate intentionally refuses mainnet. A future live gate must be a separate,
reviewed change with explicit controls and independent verification.
"""
from dataclasses import dataclass
from enum import Enum

class RuntimeMode(str, Enum):
    PAPER = "paper"
    TESTNET = "testnet"
    MAINNET = "mainnet"

@dataclass(frozen=True)
class PreflightReport:
    approved: bool
    mode: RuntimeMode
    checks: tuple[str, ...]
    failures: tuple[str, ...]

class PreflightGate:
    def check(self, mode: RuntimeMode, *, api_key_present: bool,
              api_secret_present: bool, risk_configured: bool,
              reconciliation_enabled: bool, kill_switch_ready: bool) -> PreflightReport:
        checks = ("credentials", "risk", "reconciliation", "kill_switch")
        failures: list[str] = []
        if mode is RuntimeMode.MAINNET:
            failures.append("mainnet is disabled by preflight")
        if mode is RuntimeMode.TESTNET and not (api_key_present and api_secret_present):
            failures.append("Testnet credentials are missing")
        if not risk_configured:
            failures.append("risk configuration is not ready")
        if not reconciliation_enabled:
            failures.append("reconciliation is disabled")
        if not kill_switch_ready:
            failures.append("kill switch is not ready")
        return PreflightReport(not failures, mode, checks, tuple(failures))
