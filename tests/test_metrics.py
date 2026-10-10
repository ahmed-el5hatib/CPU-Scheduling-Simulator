"""Tests for simulation metrics calculations.

Author signature: Eng Ahmed El-khatib
"""

import pytest

from scheduling.metrics import compute_metrics
from scheduling.models import Process, Segment


def test_metrics_empty_processes() -> None:
    res = compute_metrics([], [], "Empty")
    assert res.span == 0
    assert res.busy_time == 0
    assert res.idle_time == 0
    assert res.cpu_utilization == 0.0
    assert res.throughput == 0.0
    assert res.avg_turnaround_time == 0.0
    assert res.avg_waiting_time == 0.0
    assert res.avg_response_time == 0.0
    assert res.process_metrics == []


def test_metrics_exact_definitions() -> None:
    """Verifies Section 8 formulas:

    span = max(CT) - min(AT)
    busy_time = sum of all non-IDLE segment durations
    idle_time = span - busy_time
    utilization = busy_time / span
    throughput = n_completed / span
    avg WT, avg TAT, avg RT = arithmetic means.
    """
    procs = [
        Process("P1", arrival_time=0, burst_time=4, priority=1),
        Process("P2", arrival_time=2, burst_time=3, priority=2),
    ]
    timeline = [
        Segment("P1", 0, 4),
        Segment(None, 4, 6),
        Segment("P2", 6, 9),
    ]
    res = compute_metrics(procs, timeline, "TestAlgo")

    assert res.span == 9  # max(CT)=9 - min(AT)=0
    assert res.busy_time == 7  # 4 + 3
    assert res.idle_time == 2  # 9 - 7
    assert res.cpu_utilization == pytest.approx(7 / 9)
    assert res.throughput == pytest.approx(2 / 9)

    m1 = [m for m in res.process_metrics if m.pid == "P1"][0]
    assert m1.start_time == 0
    assert m1.completion_time == 4
    assert m1.turnaround_time == 4
    assert m1.waiting_time == 0
    assert m1.response_time == 0

    m2 = [m for m in res.process_metrics if m.pid == "P2"][0]
    assert m2.start_time == 6
    assert m2.completion_time == 9
    assert m2.turnaround_time == 7
    assert m2.waiting_time == 4
    assert m2.response_time == 4

    assert res.avg_turnaround_time == pytest.approx((4 + 7) / 2)
    assert res.avg_waiting_time == pytest.approx((0 + 4) / 2)
    assert res.avg_response_time == pytest.approx((0 + 4) / 2)


def test_process_missing_from_timeline_raises() -> None:
    procs = [Process("P1", arrival_time=0, burst_time=2)]
    with pytest.raises(ValueError, match="did not execute"):
        compute_metrics(procs, [], "Test")
