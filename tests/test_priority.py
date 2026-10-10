"""Tests for Priority Scheduling (Non-preemptive).

Author signature: Eng Ahmed El-khatib
"""

from scheduling.algorithms.priority import schedule_priority
from scheduling.models import Process, Segment


def test_priority_example_dataset_1() -> None:
    procs = [
        Process("P1", arrival_time=0, burst_time=5, priority=2),
        Process("P2", arrival_time=1, burst_time=3, priority=1),
        Process("P3", arrival_time=2, burst_time=8, priority=3),
        Process("P4", arrival_time=4, burst_time=6, priority=4),
    ]
    res = schedule_priority(procs)

    expected_timeline = [
        Segment("P1", 0, 5),
        Segment("P2", 5, 8),
        Segment("P3", 8, 16),
        Segment("P4", 16, 22),
    ]
    assert res.timeline == expected_timeline


def test_priority_tie_breaking() -> None:
    """Priority tie -> earlier arrival, then insertion order."""
    procs = [
        Process("P_first", arrival_time=0, burst_time=2, priority=5),
        Process("P_later", arrival_time=2, burst_time=3, priority=1),
        Process("P_earlier", arrival_time=1, burst_time=3, priority=1),
    ]
    # P_first runs [0, 2).
    # At t=2, P_later (AT=2, PRI=1) and P_earlier (AT=1, PRI=1) are ready.
    # Tie broken by earlier arrival -> P_earlier runs next!
    res = schedule_priority(procs)
    order = [seg.pid for seg in res.timeline if seg.pid is not None]
    assert order == ["P_first", "P_earlier", "P_later"]

    # Tie on priority AND arrival -> insertion order
    procs2 = [
        Process("PX", arrival_time=0, burst_time=1, priority=1),
        Process("PY", arrival_time=1, burst_time=2, priority=2),
        Process("PZ", arrival_time=1, burst_time=2, priority=2),
    ]
    res2 = schedule_priority(procs2)
    order2 = [seg.pid for seg in res2.timeline if seg.pid is not None]
    assert order2 == ["PX", "PY", "PZ"]
