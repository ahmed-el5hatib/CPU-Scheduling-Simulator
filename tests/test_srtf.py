"""Tests for Shortest Remaining Time First (SRTF Preemptive) scheduling.

Author signature: Eng Ahmed El-khatib
"""

from scheduling.algorithms.srtf import schedule_srtf
from scheduling.models import Process, Segment


def test_srtf_example_dataset_1() -> None:
    procs = [
        Process("P1", arrival_time=0, burst_time=5, priority=2),
        Process("P2", arrival_time=1, burst_time=3, priority=1),
        Process("P3", arrival_time=2, burst_time=8, priority=3),
        Process("P4", arrival_time=4, burst_time=6, priority=4),
    ]
    res = schedule_srtf(procs)

    expected_timeline = [
        Segment("P1", 0, 1),
        Segment("P2", 1, 4),
        Segment("P1", 4, 8),
        Segment("P4", 8, 14),
        Segment("P3", 14, 22),
    ]
    assert res.timeline == expected_timeline

    metrics = {m.pid: m for m in res.process_metrics}
    # P1: first started at 0, completed at 8, BT=5, AT=0
    assert metrics["P1"].start_time == 0
    assert metrics["P1"].completion_time == 8
    assert metrics["P1"].turnaround_time == 8
    assert metrics["P1"].waiting_time == 3
    assert metrics["P1"].response_time == 0

    # P2: started at 1, completed at 4, BT=3, AT=1
    assert metrics["P2"].start_time == 1
    assert metrics["P2"].completion_time == 4
    assert metrics["P2"].turnaround_time == 3
    assert metrics["P2"].waiting_time == 0
    assert metrics["P2"].response_time == 0


def test_srtf_strict_shorter_preemption_equal_remaining_no_preempt() -> None:
    """Invariant: strict-shorter preemption only; equal remaining -> no preempt."""
    # P1 starts at t=0, BT=4.
    # At t=2, P1 has remaining 2.
    # P2 arrives at t=2 with BT=2 (remaining 2).
    # Since 2 is NOT < 2, P1 MUST NOT be preempted! P1 continues to completion at t=4.
    procs = [
        Process("P1", arrival_time=0, burst_time=4),
        Process("P2", arrival_time=2, burst_time=2),
    ]
    res = schedule_srtf(procs)
    # P1 runs [0, 4) uninterrupted, then P2 runs [4, 6)
    assert res.timeline == [
        Segment("P1", 0, 4),
        Segment("P2", 4, 6),
    ]
