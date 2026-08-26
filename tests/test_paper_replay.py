from datetime import datetime, timedelta, timezone
import pytest
from oracle.paper.replay import ReplayBar, WalkForwardPaperReplay

def bars(count: int) -> list[ReplayBar]:
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    return [ReplayBar(start + timedelta(minutes=i), 100.0 + i) for i in range(count)]

def test_walk_forward_keeps_training_data_out_of_test_decisions() -> None:
    result = WalkForwardPaperReplay(10_000.0, training_bars=5).run(bars(8))
    assert result.training_bars == 5
    assert result.test_bars == 3
    assert result.report.trades == 0

def test_replay_rejects_non_chronological_data() -> None:
    data = bars(6)
    data[3] = ReplayBar(data[2].timestamp, data[3].close)
    with pytest.raises(ValueError, match="strictly chronological"):
        WalkForwardPaperReplay(10_000.0, training_bars=5).run(data)

def test_replay_rejects_insufficient_test_window() -> None:
    with pytest.raises(ValueError, match="bars after the training window"):
        WalkForwardPaperReplay(10_000.0, training_bars=5).run(bars(5))
