"""Tests for Shortest Job First (SJF Non-preemptive) scheduling.

Author signature: Eng Ahmed El-khatib
"""

from scheduling.algorithms.sjf import schedule_sjf
from scheduling.models import Process, Segment


def test_sjf_example_dataset_1() -> None:
    procs = [
        Process("P1", arrival_time=0, burst_time=5, priority=2),
        Process("P2", arrival_time=1, burst_time=3, priority=1),
        Process("P3", arrival_time=2, burst_time=8, priority=3),
        Process("P4", arrival_time=4, burst_time=6, priority=4),
    ]
    res = schedule_sjf(procs)

    expected_timeline = [
        Segment("P1", 0, 5),
        Segment("P2", 5, 8),
        Segment("P4", 8, 14),
        Segment("P3", 14, 22),
    ]
    assert res.timeline == expected_timeline

    metrics = {m.pid: m for m in res.process_metrics}
    assert metrics["P2"].start_time == 5
    assert metrics["P2"].completion_time == 8
    assert metrics["P4"].start_time == 8
    assert metrics["P4"].completion_time == 14
    assert metrics["P3"].start_time == 14
    assert metrics["P3"].completion_time == 22


def test_sjf_tie_breaking() -> None:
    """SJF tie on burst -> earlier arrival, then insertion order."""
    # Tie on burst (all BT=4), different arrival
    procs = [
        Process("P1", arrival_time=2, burst_time=4),
        Process("P2", arrival_time=1, burst_time=4),
        Process("P3", arrival_time=0, burst_time=2),
    ]
    # At t=0, only P3 is ready. P3 runs [0, 2).
    # At t=2, P1 (AT=2) and P2 (AT=1) both ready, both BT=4.
    # Earlier arrival is P2 (AT=1). So P2 runs next!
    res = schedule_sjf(procs)
    order = [seg.pid for seg in res.timeline if seg.pid is not None]
    assert order == ["P3", "P2", "P1"]

    # Tie on burst AND arrival -> insertion order
    procs2 = [
        Process("PA", arrival_time=0, burst_time=1),
        Process("PB", arrival_time=0, burst_time=3),
        Process("PC", arrival_time=0, burst_time=3),
    ]
    res2 = schedule_sjf(procs2)
    order2 = [seg.pid for seg in res2.timeline if seg.pid is not None]
    assert order2 == ["PA", "PB", "PC"]
