"""Idempotency primitives for safe order submission."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Submission:
    client_order_id: str
    status: str

class IdempotencyRegistry:
    def __init__(self) -> None:
        self._submissions: dict[str, Submission] = {}

    def get(self, client_order_id: str) -> Submission | None:
        return self._submissions.get(client_order_id)

    def record(self, submission: Submission) -> Submission:
        existing = self._submissions.get(submission.client_order_id)
        if existing is not None:
            return existing
        self._submissions[submission.client_order_id] = submission
        return submission
