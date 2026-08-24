"""Bounded retry policy for exchange transport failures."""
from dataclasses import dataclass
from oracle.exchange.errors import ErrorClass

@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 8.0

    def delay(self, attempt: int) -> float:
        return min(self.max_delay_seconds, self.base_delay_seconds * (2 ** max(0, attempt - 1)))

    def should_retry(self, error_class: ErrorClass, attempt: int) -> bool:
        return attempt < self.max_attempts and error_class in {ErrorClass.RETRYABLE, ErrorClass.RATE_LIMIT}
