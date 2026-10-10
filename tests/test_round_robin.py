"""Tests for Round Robin (RR) scheduling.

Author signature: Eng Ahmed El-khatib
"""

import pytest

from scheduling.algorithms.round_robin import schedule_round_robin
from scheduling.models import Process, Segment


def test_rr_example_dataset_1() -> None:
    """Example 1 with quantum=2:

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
    res = schedule_round_robin(procs, quantum=2)

    expected_timeline = [
        Segment("P1", 0, 2),
        Segment("P2", 2, 4),
        Segment("P3", 4, 6),
        Segment("P1", 6, 8),
        Segment("P4", 8, 10),
        Segment("P2", 10, 11),
        Segment("P3", 11, 13),
        Segment("P1", 13, 14),
        Segment("P4", 14, 16),
        Segment("P3", 16, 18),
        Segment("P4", 18, 20),
        Segment("P3", 20, 22),
    ]
    assert res.timeline == expected_timeline

    metrics = {m.pid: m for m in res.process_metrics}
    assert metrics["P1"].completion_time == 14
    assert metrics["P2"].completion_time == 11
    assert metrics["P4"].completion_time == 20
    assert metrics["P3"].completion_time == 22


def test_rr_arrival_at_quantum_expiry_instant() -> None:
    """Textbook rule: On quantum expiry AND new arrival at same instant,

    the newly arrived process enters the ready queue BEFORE the preempted process.
    """
    # P1 arrives at 0, BT=4. Quantum=2.
    # P2 arrives at exactly 2, BT=3.
    # At t=2: P1's quantum expires. P2 arrives at t=2.
    # P2 MUST enter ready queue BEFORE P1!
    # Therefore, at t=2, P2 runs for quantum 2 [2, 4), then P1 resumes [4, 6).
    procs = [
        Process("P1", arrival_time=0, burst_time=4),
        Process("P2", arrival_time=2, burst_time=3),
    ]
    res = schedule_round_robin(procs, quantum=2)
    assert res.timeline == [
        Segment("P1", 0, 2),
        Segment("P2", 2, 4),
        Segment("P1", 4, 6),
        Segment("P2", 6, 7),
    ]


def test_rr_quantum_greater_than_burst() -> None:
    """RR with quantum > burst (acts like FCFS)."""
    procs = [
        Process("P1", arrival_time=0, burst_time=3),
        Process("P2", arrival_time=1, burst_time=2),
    ]
    res = schedule_round_robin(procs, quantum=10)
    assert res.timeline == [
        Segment("P1", 0, 3),
        Segment("P2", 3, 5),
    ]


def test_rr_quantum_equals_burst() -> None:
    """RR with quantum == burst."""
    procs = [
        Process("P1", arrival_time=0, burst_time=4),
        Process("P2", arrival_time=0, burst_time=4),
    ]
    res = schedule_round_robin(procs, quantum=4)
    assert res.timeline == [
        Segment("P1", 0, 4),
        Segment("P2", 4, 8),
    ]


def test_rr_quantum_less_than_burst() -> None:
    """RR with quantum < burst."""
    procs = [
        Process("P1", arrival_time=0, burst_time=6),
        Process("P2", arrival_time=0, burst_time=3),
    ]
    res = schedule_round_robin(procs, quantum=2)
    assert res.timeline == [
        Segment("P1", 0, 2),
        Segment("P2", 2, 4),
        Segment("P1", 4, 6),
        Segment("P2", 6, 7),
        Segment("P1", 7, 9),
    ]


def test_rr_quantum_one() -> None:
    """RR with quantum = 1."""
    procs = [
        Process("P1", arrival_time=0, burst_time=2),
        Process("P2", arrival_time=0, burst_time=2),
    ]
    res = schedule_round_robin(procs, quantum=1)
    assert res.timeline == [
        Segment("P1", 0, 1),
        Segment("P2", 1, 2),
        Segment("P1", 2, 3),
        Segment("P2", 3, 4),
    ]


@pytest.mark.parametrize("invalid_q", [0, -1, -5, "2", None])
def test_rr_quantum_invalid_raises(invalid_q: object) -> None:
    """RR: quantum invalid (0 or negative, non-int) -> raise ValueError."""
    procs = [Process("P1", arrival_time=0, burst_time=2)]
    with pytest.raises(ValueError):
        schedule_round_robin(procs, quantum=invalid_q)  # type: ignore[arg-type]
