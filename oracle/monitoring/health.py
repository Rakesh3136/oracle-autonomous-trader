from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class HealthStatus:
    market_data: bool
    exchange: bool
    risk: bool
    timestamp: datetime

class HealthMonitor:
    def check(self, market_data: bool, exchange: bool, risk: bool) -> HealthStatus:
        return HealthStatus(market_data, exchange, risk, datetime.now(timezone.utc))
