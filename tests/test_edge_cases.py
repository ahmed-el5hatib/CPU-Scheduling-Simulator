"""Edge cases and input validation tests.

Author signature: Eng Ahmed El-khatib
"""

import pytest

from scheduling.engine import run_simulation, validate_processes
from scheduling.models import Process, Segment


def test_empty_process_list_raises_value_error() -> None:
    """Empty process list -> engine raises a clear ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        run_simulation("fcfs", [])


def test_duplicate_pids_rejected() -> None:
    """Duplicate PIDs -> rejected at model/validation level."""
    p1 = Process("P1", arrival_time=0, burst_time=5)
    p2 = Process("P1", arrival_time=2, burst_time=3)
    with pytest.raises(ValueError, match="Duplicate PID"):
        validate_processes([p1, p2])

    with pytest.raises(ValueError, match="Duplicate PID"):
        run_simulation("sjf", [p1, p2])


def test_invalid_process_models() -> None:
    with pytest.raises(ValueError, match="non-empty string"):
        Process("", arrival_time=0, burst_time=5)

    with pytest.raises(ValueError, match="arrival_time"):
        Process("P1", arrival_time=-1, burst_time=5)

    with pytest.raises(ValueError, match="burst_time"):
        Process("P1", arrival_time=0, burst_time=0)

    with pytest.raises(ValueError, match="burst_time"):
        Process("P1", arrival_time=0, burst_time=-4)

    with pytest.raises(ValueError, match="priority"):
        Process("P1", arrival_time=0, burst_time=5, priority="high")  # type: ignore[arg-type]


def test_invalid_segment_model() -> None:
    with pytest.raises(ValueError, match="start time"):
        Segment("P1", -1, 5)

    with pytest.raises(ValueError, match="end time"):
        Segment("P1", 5, 5)

    with pytest.raises(ValueError, match="end time"):
        Segment("P1", 5, 4)


def test_unknown_algorithm_raises() -> None:
    p = Process("P1", arrival_time=0, burst_time=3)
    with pytest.raises(ValueError, match="Unknown scheduling algorithm"):
        run_simulation("lottery_scheduler", [p])


def test_empty_process_direct_algorithms() -> None:
    from scheduling.algorithms.fcfs import schedule_fcfs
    from scheduling.algorithms.preemptive_priority import schedule_preemptive_priority
    from scheduling.algorithms.priority import schedule_priority
    from scheduling.algorithms.round_robin import schedule_round_robin
    from scheduling.algorithms.sjf import schedule_sjf
    from scheduling.algorithms.srtf import schedule_srtf

    for fn in [
        schedule_fcfs,
        schedule_sjf,
        schedule_priority,
        schedule_srtf,
        schedule_round_robin,
        schedule_preemptive_priority,
    ]:
        with pytest.raises(ValueError, match="cannot be empty"):
            fn([])


def test_validate_processes_type_error() -> None:
    with pytest.raises(TypeError, match="Expected Process instance"):
        validate_processes([{"pid": "P1"}])  # type: ignore[list-item]


def test_run_simulation_display_name_lookup() -> None:
    p = Process("P1", arrival_time=0, burst_time=3)
    res = run_simulation("First-Come First-Served (FCFS)", [p])
    assert res.span == 3



def test_large_idle_gap_before_first_arrival() -> None:
    """Large idle gap before first arrival."""
    p = Process("P1", arrival_time=100, burst_time=10)
    for algo in ["fcfs", "sjf", "priority", "srtf", "round_robin", "preemptive_priority"]:
        res = run_simulation(algo, [p], quantum=5)
        # Should start with an idle block from 0 to 100
        assert res.timeline[0].is_idle
        assert res.timeline[0].start == 0
        assert res.timeline[0].end == 100
        assert res.process_metrics[0].start_time == 100
        assert res.process_metrics[0].completion_time == 110
        assert res.span == 10  # max(CT) - min(AT) = 110 - 100
        assert res.busy_time == 10
        assert res.idle_time == 0
