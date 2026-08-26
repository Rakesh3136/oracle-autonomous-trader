"""Walk-forward paper replay with a strict no-look-ahead boundary."""
from dataclasses import dataclass
from datetime import datetime
from oracle.paper.performance import PaperPerformance, PerformanceReport

@dataclass(frozen=True)
class ReplayBar:
    timestamp: datetime
    close: float

@dataclass(frozen=True)
class ReplayResult:
    training_bars: int
    test_bars: int
    report: PerformanceReport

class WalkForwardPaperReplay:
    def __init__(self, starting_equity: float, training_bars: int = 200) -> None:
        if training_bars < 1:
            raise ValueError("training_bars must be positive")
        self.training_bars = training_bars
        self.performance = PaperPerformance(starting_equity)

    def validate(self, bars: list[ReplayBar]) -> None:
        if len(bars) <= self.training_bars:
            raise ValueError("replay requires bars after the training window")
        for previous, current in zip(bars, bars[1:]):
            if current.timestamp <= previous.timestamp:
                raise ValueError("replay bars must be strictly chronological")
        if any(bar.close <= 0 for bar in bars):
            raise ValueError("replay prices must be positive")

    def run(self, bars: list[ReplayBar]) -> ReplayResult:
        self.validate(bars)
        # The first training_bars are context only. Decisions in the test period
        # may only use bars at or before the current timestamp.
        test_bars = bars[self.training_bars:]
        for index, bar in enumerate(test_bars):
            history = bars[: self.training_bars + index]
            if len(history) < self.training_bars:
                raise AssertionError("insufficient historical context")
            # Strategy integration is intentionally supplied by the caller later;
            # this stage validates the temporal boundary and accounting plumbing.
            _ = history, bar
        return ReplayResult(self.training_bars, len(test_bars), self.performance.report())
