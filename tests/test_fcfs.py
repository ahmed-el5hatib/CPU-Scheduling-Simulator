"""Tests for First-Come First-Served (FCFS) scheduling.

Author signature: Eng Ahmed El-khatib
"""

from scheduling.algorithms.fcfs import schedule_fcfs
from scheduling.models import Process, Segment


def test_fcfs_example_dataset_1() -> None:
    """Example 1 from Section 6:

    P1 AT=0 BT=5 PRI=2
    P2 AT=1 BT=3 PRI=1
    P3 AT=2 BT=8 PRI=3
    P4 AT=4 BT=6 PRI=4
    """
    procs = [
        Process("P1", arrival_time=0, burst_time=5, priority=2),
        Process("P2", arrival_time=1, burst_time=3, priority=1),
        Process("P3", arrival_time=2, burst_time=8, priority=3),
        Process("P4", arrival_time=4, burst_time=6, priority=4),
    ]
    res = schedule_fcfs(procs)

    expected_timeline = [
        Segment("P1", 0, 5),
        Segment("P2", 5, 8),
        Segment("P3", 8, 16),
        Segment("P4", 16, 22),
    ]
    assert res.timeline == expected_timeline

    metrics_by_pid = {m.pid: m for m in res.process_metrics}
    # P1: AT=0, BT=5, ST=0, CT=5, TAT=5, WT=0, RT=0
    assert metrics_by_pid["P1"].start_time == 0
    assert metrics_by_pid["P1"].completion_time == 5
    assert metrics_by_pid["P1"].turnaround_time == 5
    assert metrics_by_pid["P1"].waiting_time == 0
    assert metrics_by_pid["P1"].response_time == 0

    # P2: AT=1, BT=3, ST=5, CT=8, TAT=7, WT=4, RT=4
    assert metrics_by_pid["P2"].start_time == 5
    assert metrics_by_pid["P2"].completion_time == 8
    assert metrics_by_pid["P2"].turnaround_time == 7
    assert metrics_by_pid["P2"].waiting_time == 4
    assert metrics_by_pid["P2"].response_time == 4

    # P3: AT=2, BT=8, ST=8, CT=16, TAT=14, WT=6, RT=6
    assert metrics_by_pid["P3"].start_time == 8
    assert metrics_by_pid["P3"].completion_time == 16
    assert metrics_by_pid["P3"].turnaround_time == 14
    assert metrics_by_pid["P3"].waiting_time == 6
    assert metrics_by_pid["P3"].response_time == 6

    # P4: AT=4, BT=6, ST=16, CT=22, TAT=18, WT=12, RT=12
    assert metrics_by_pid["P4"].start_time == 16
    assert metrics_by_pid["P4"].completion_time == 22
    assert metrics_by_pid["P4"].turnaround_time == 18
    assert metrics_by_pid["P4"].waiting_time == 12
    assert metrics_by_pid["P4"].response_time == 12

    assert res.span == 22
    assert res.busy_time == 22
    assert res.idle_time == 0
    assert res.cpu_utilization == 1.0


def test_fcfs_example_dataset_2_with_idle() -> None:
    """Example 2 from Section 6 with idle gaps:

    P1 AT=0 BT=2 PRI=1
    P2 AT=5 BT=3 PRI=2
    P3 AT=5 BT=1 PRI=1
    P4 AT=7 BT=4 PRI=3
    """
    procs = [
        Process("P1", arrival_time=0, burst_time=2, priority=1),
        Process("P2", arrival_time=5, burst_time=3, priority=2),
        Process("P3", arrival_time=5, burst_time=1, priority=1),
        Process("P4", arrival_time=7, burst_time=4, priority=3),
    ]
    res = schedule_fcfs(procs)

    # Idle between 2 and 5
    # P2 arrives before P3 in insertion order, so P2 runs at 5
    expected_timeline = [
        Segment("P1", 0, 2),
        Segment(None, 2, 5),
        Segment("P2", 5, 8),
        Segment("P3", 8, 9),
        Segment("P4", 9, 13),
    ]
    assert res.timeline == expected_timeline
    assert res.span == 13
    assert res.busy_time == 10
    assert res.idle_time == 3


def test_fcfs_tie_breaking_insertion_order() -> None:
    """Tie on arrival -> lower PID index (insertion order)."""
    procs = [
        Process("P_A", arrival_time=3, burst_time=4),
        Process("P_B", arrival_time=3, burst_time=2),
        Process("P_C", arrival_time=3, burst_time=1),
    ]
    res = schedule_fcfs(procs)
    order = [seg.pid for seg in res.timeline if seg.pid is not None]
    assert order == ["P_A", "P_B", "P_C"]


def test_fcfs_idle_before_first_arrival() -> None:
    """Large idle gap before first arrival."""
    procs = [Process("P1", arrival_time=25, burst_time=5)]
    res = schedule_fcfs(procs)
    assert res.timeline == [
        Segment(None, 0, 25),
        Segment("P1", 25, 30),
    ]
    assert res.span == 5  # max(CT) - min(AT) = 30 - 25 = 5
    assert res.busy_time == 5
    assert res.idle_time == 0
