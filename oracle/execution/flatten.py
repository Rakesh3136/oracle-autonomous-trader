"""Emergency flattening contract; live transport remains intentionally injectable."""
from dataclasses import dataclass

@dataclass(frozen=True)
class FlattenRequest:
    reason: str
    symbols: tuple[str, ...] = ()

class EmergencyFlatten:
    def build_requests(self, symbols: list[str], reason: str) -> tuple[FlattenRequest, ...]:
        if not reason.strip():
            raise ValueError("flatten reason is required")
        return tuple(FlattenRequest(reason, (symbol,)) for symbol in symbols)
