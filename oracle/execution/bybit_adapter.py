"""Fail-closed Bybit adapter boundary.

Testnet/simulation translation is supported; live network submission remains
explicitly disabled. Secrets must come from environment variables, never source.
"""
from dataclasses import dataclass
from enum import Enum
from oracle.execution.order_intent import OrderIntent, OrderType, Side

class BybitEnvironment(str, Enum):
    TESTNET = "testnet"
    MAINNET = "mainnet"

@dataclass(frozen=True)
class BybitConfig:
    environment: BybitEnvironment = BybitEnvironment.TESTNET
    api_key_env: str = "BYBIT_API_KEY"
    api_secret_env: str = "BYBIT_API_SECRET"
    recv_window_ms: int = 5000

class LiveTradingDisabled(RuntimeError):
    pass

class BybitAdapter:
    def __init__(self, config: BybitConfig | None = None, enable_live: bool = False) -> None:
        self.config = config or BybitConfig()
        if self.config.recv_window_ms <= 0:
            raise ValueError("recv_window_ms must be positive")
        if self.config.environment is BybitEnvironment.MAINNET and not enable_live:
            raise LiveTradingDisabled("mainnet execution is disabled")
        self._enable_live = enable_live

    def translate(self, intent: OrderIntent) -> dict[str, str]:
        payload = {
            "category": "linear", "symbol": intent.symbol,
            "side": "Buy" if intent.side is Side.BUY else "Sell",
            "orderType": "Market" if intent.order_type is OrderType.MARKET else "Limit",
            "qty": str(intent.quantity),
            "reduceOnly": "true" if intent.reduce_only else "false",
        }
        if intent.limit_price is not None:
            payload["price"] = str(intent.limit_price)
        return payload

    def submit(self, intent: OrderIntent) -> bool:
        if not self._enable_live:
            raise LiveTradingDisabled("Bybit submission disabled; use Testnet/simulation")
        raise LiveTradingDisabled("live network submission is not implemented")
