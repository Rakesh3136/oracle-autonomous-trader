"""Bybit V5 REST authentication signing primitives.

Secrets are passed in at runtime; this module never persists credentials.
"""
import hashlib
import hmac
from dataclasses import dataclass

@dataclass(frozen=True)
class BybitCredentials:
    api_key: str
    api_secret: str

class BybitSigner:
    def __init__(self, credentials: BybitCredentials, recv_window: int = 5000) -> None:
        self.credentials = credentials
        self.recv_window = recv_window

    def sign(self, timestamp_ms: int, payload: str) -> dict[str, str]:
        prehash = f"{timestamp_ms}{self.credentials.api_key}{self.recv_window}{payload}"
        signature = hmac.new(self.credentials.api_secret.encode(), prehash.encode(), hashlib.sha256).hexdigest()
        return {
            "X-BAPI-API-KEY": self.credentials.api_key,
            "X-BAPI-TIMESTAMP": str(timestamp_ms),
            "X-BAPI-RECV-WINDOW": str(self.recv_window),
            "X-BAPI-SIGN": signature,
        }
