"""Exchange error classification used by retry and safety policies."""
from enum import Enum

class ErrorClass(str, Enum):
    RETRYABLE = "retryable"
    RATE_LIMIT = "rate_limit"
    AUTH = "auth"
    INVALID_REQUEST = "invalid_request"
    UNKNOWN = "unknown"

def classify(code: str | int) -> ErrorClass:
    value = str(code).lower()
    if value in {"10006", "429", "rate_limit"}:
        return ErrorClass.RATE_LIMIT
    if value in {"10003", "10004", "auth", "unauthorized"}:
        return ErrorClass.AUTH
    if value in {"invalid", "invalid_request", "10001"}:
        return ErrorClass.INVALID_REQUEST
    if value in {"timeout", "network", "temporarily_unavailable", "503"}:
        return ErrorClass.RETRYABLE
    return ErrorClass.UNKNOWN
