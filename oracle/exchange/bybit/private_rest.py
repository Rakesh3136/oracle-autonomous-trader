"""Authenticated Bybit V5 REST boundary.

Uses HMAC V5 signing, server-clock synchronization, and JSON request bodies.
Order submission is disabled unless explicitly enabled by the deployment layer.
"""
import json
from dataclasses import dataclass
from typing import Any
import httpx
from oracle.exchange.bybit.auth import BybitCredentials, BybitSigner
from oracle.exchange.bybit.time_sync import ServerClock

@dataclass(frozen=True)
class PrivateRestConfig:
    testnet: bool = True
    timeout: float = 10.0
    recv_window: int = 5000
    allow_order_submission: bool = False

class BybitPrivateRest:
    def __init__(self, credentials: BybitCredentials, config: PrivateRestConfig | None = None) -> None:
        self.config = config or PrivateRestConfig()
        self.base_url = "https://api-testnet.bybit.com" if self.config.testnet else "https://api.bybit.com"
        self.client = httpx.Client(base_url=self.base_url, timeout=self.config.timeout)
        self.signer = BybitSigner(credentials, self.config.recv_window)
        self.clock = ServerClock()

    def close(self) -> None:
        self.client.close()

    def _request(self, method: str, path: str, params: dict[str, Any] | None = None,
                 body: dict[str, Any] | None = None) -> dict[str, Any]:
        params = params or {}
        body = body or {}
        if method == "GET":
            query = "&".join(f"{k}={params[k]}" for k in sorted(params))
            payload = query
            response = self.client.get(path, params=params,
                                       headers=self.signer.sign(self.clock.now_ms(), payload))
        else:
            payload = json.dumps(body, separators=(",", ":"))
            headers = self.signer.sign(self.clock.now_ms(), payload)
            headers["Content-Type"] = "application/json"
            response = self.client.request(method, path, content=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        if result.get("retCode") != 0:
            raise RuntimeError(f"Bybit API error: {result.get('retCode')} {result.get('retMsg')}")
        return result.get("result", {})

    def wallet_balance(self, account_type: str = "UNIFIED", coin: str = "USDT") -> dict[str, Any]:
        return self._request("GET", "/v5/account/wallet-balance",
                             {"accountType": account_type, "coin": coin})

    def positions(self, category: str = "linear", settle_coin: str = "USDT") -> dict[str, Any]:
        return self._request("GET", "/v5/position/list",
                             {"category": category, "settleCoin": settle_coin})

    def open_orders(self, category: str = "linear", settle_coin: str = "USDT") -> dict[str, Any]:
        return self._request("GET", "/v5/order/realtime",
                             {"category": category, "settleCoin": settle_coin})

    def create_order(self, order: dict[str, Any]) -> dict[str, Any]:
        if not self.config.allow_order_submission:
            raise PermissionError("order submission disabled by deployment configuration")
        return self._request("POST", "/v5/order/create", body=order)

    def cancel_order(self, order: dict[str, Any]) -> dict[str, Any]:
        if not self.config.allow_order_submission:
            raise PermissionError("order submission disabled by deployment configuration")
        return self._request("POST", "/v5/order/cancel", body=order)
