"""Walk-forward research splitter preventing train/test leakage."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Window:
    train_start: int
    train_end: int
    test_start: int
    test_end: int

class WalkForward:
    def __init__(self, train_size: int, test_size: int, step: int | None = None) -> None:
        if min(train_size, test_size) <= 0:
            raise ValueError("window sizes must be positive")
        self.train_size = train_size
        self.test_size = test_size
        self.step = step or test_size

    def windows(self, length: int) -> tuple[Window, ...]:
        result: list[Window] = []
        start = 0
        while start + self.train_size + self.test_size <= length:
            train_end = start + self.train_size
            result.append(Window(start, train_end, train_end, train_end + self.test_size))
            start += self.step
        return tuple(result)
