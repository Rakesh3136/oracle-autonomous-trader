"""Small exchange adapter boundary; HTTP transport is injected by deployment code."""
from dataclasses import dataclass
from typing import Protocol

class HttpTransport(Protocol):
    def request(self, method: str, path: str, headers: dict[str, str], body: str = "") -> dict[str, object]: ...

@dataclass(frozen=True)
class BybitEnvironment:
    base_url: str
    testnet: bool = True

class BybitClient:
    def __init__(self, transport: HttpTransport, environment: BybitEnvironment) -> None:
        self.transport = transport
        self.environment = environment

    def request(self, method: str, path: str, headers: dict[str, str], body: str = "") -> dict[str, object]:
        if not path.startswith("/"):
            raise ValueError("path must begin with /")
        return self.transport.request(method, path, headers, body)
