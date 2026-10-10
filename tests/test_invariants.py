"""Parametric tests verifying all invariants (I1-I11) from Section 7.

Author signature: Eng Ahmed El-khatib

Invariants tested for every algorithm x every valid dataset:
  I1. Each process completes exactly once.
  I2. sum(segment durations for pid) == burst(pid).
  I3. No segment starts before its process's arrival.
  I4. No negative remaining time at any point.
  I5. CT >= AT for every process.
  I6. TAT == CT - AT.
  I7. WT == TAT - BT.
  I8. RT == first_start - AT.
  I9. busy_time + idle_time == span.
  I10. 0 <= CPU utilization <= 1 when span > 0.
  I11. throughput == n_completed / span.
"""

from typing import Any

import pytest

from scheduling.engine import ALGORITHMS, run_simulation
from scheduling.models import Process, SimResult

DATASETS: list[list[Process]] = [
    # Dataset 1: Section 6 Example 1
    [
        Process("P1", arrival_time=0, burst_time=5, priority=2),
        Process("P2", arrival_time=1, burst_time=3, priority=1),
        Process("P3", arrival_time=2, burst_time=8, priority=3),
        Process("P4", arrival_time=4, burst_time=6, priority=4),
    ],
    # Dataset 2: Section 6 Example 2 (forces idle time)
    [
        Process("P1", arrival_time=0, burst_time=2, priority=1),
        Process("P2", arrival_time=5, burst_time=3, priority=2),
        Process("P3", arrival_time=5, burst_time=1, priority=1),
        Process("P4", arrival_time=7, burst_time=4, priority=3),
    ],
    # Dataset 3: All arrive at t=0
    [
        Process("P1", arrival_time=0, burst_time=4, priority=3),
        Process("P2", arrival_time=0, burst_time=1, priority=1),
        Process("P3", arrival_time=0, burst_time=2, priority=2),
    ],
    # Dataset 4: Single process
    [
        Process("P_solo", arrival_time=0, burst_time=7, priority=1),
    ],
    # Dataset 5: Idle gaps between processes
    [
        Process("PA", arrival_time=0, burst_time=2, priority=1),
        Process("PB", arrival_time=10, burst_time=3, priority=2),
        Process("PC", arrival_time=20, burst_time=4, priority=1),
    ],
    # Dataset 6: Heavy interleaving
    [
        Process("P1", arrival_time=0, burst_time=3, priority=2),
        Process("P2", arrival_time=1, burst_time=4, priority=1),
        Process("P3", arrival_time=2, burst_time=2, priority=3),
        Process("P4", arrival_time=3, burst_time=5, priority=2),
    ],
]


@pytest.mark.parametrize("algo_key", list(ALGORITHMS.keys()))
@pytest.mark.parametrize("dataset_idx", range(len(DATASETS)))
def test_all_invariants(algo_key: str, dataset_idx: int) -> None:
    processes = DATASETS[dataset_idx]
    config: dict[str, Any] = {"quantum": 2} if algo_key == "round_robin" else {}
    result: SimResult = run_simulation(algo_key, processes, **config)

    proc_map = {p.pid: p for p in processes}
    metrics_map = {m.pid: m for m in result.process_metrics}

    # I1: Each process completes exactly once
    assert len(result.process_metrics) == len(processes)
    assert set(metrics_map.keys()) == set(proc_map.keys())

    # I2: sum(segment durations for pid) == burst(pid)
    for p in processes:
        dur = sum(seg.duration for seg in result.timeline if seg.pid == p.pid)
        assert dur == p.burst_time, f"Invariant I2 failed for {p.pid} in {algo_key}"

    # I3: No segment starts before its process's arrival
    for seg in result.timeline:
        if seg.pid is not None:
            p = proc_map[seg.pid]
            assert seg.start >= p.arrival_time, f"Invariant I3 failed for {seg} in {algo_key}"

    # I4: No negative remaining time at any point
    # Validated by tracking cumulative run times across timeline
    cum_dur: dict[str, int] = {p.pid: 0 for p in processes}
    for seg in result.timeline:
        if seg.pid is not None:
            cum_dur[seg.pid] += seg.duration
            remaining = proc_map[seg.pid].burst_time - cum_dur[seg.pid]
            assert remaining >= 0, f"Invariant I4 failed for {seg.pid} in {algo_key}"

    for m in result.process_metrics:
        p = proc_map[m.pid]
        # I5: CT >= AT for every process
        assert m.completion_time >= p.arrival_time, f"Invariant I5 failed for {m.pid}"

        # I6: TAT == CT - AT
        assert m.turnaround_time == m.completion_time - p.arrival_time, (
            f"Invariant I6 failed for {m.pid}"
        )

        # I7: WT == TAT - BT
        assert m.waiting_time == m.turnaround_time - p.burst_time, (
            f"Invariant I7 failed for {m.pid}"
        )

        # I8: RT == first_start - AT
        assert m.response_time == m.start_time - p.arrival_time, f"Invariant I8 failed for {m.pid}"

    # I9: busy_time + idle_time == span
    assert result.busy_time + result.idle_time == result.span, f"Invariant I9 failed in {algo_key}"

    # I10: 0 <= CPU utilization <= 1 when span > 0
    if result.span > 0:
        assert 0.0 <= result.cpu_utilization <= 1.0, f"Invariant I10 failed in {algo_key}"

    # I11: throughput == n_completed / span (document units: proc/time-unit)
    if result.span > 0:
        expected_tp = len(processes) / result.span
        assert result.throughput == pytest.approx(expected_tp), (
            f"Invariant I11 failed in {algo_key}"
        )
    else:
        assert result.throughput == 0.0
