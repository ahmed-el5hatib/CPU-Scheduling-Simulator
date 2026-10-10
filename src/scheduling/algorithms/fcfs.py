"""First-Come First-Served (FCFS) CPU Scheduling Algorithm.

Author signature: Eng Ahmed El-khatib
Pure Python implementation - no GUI or matplotlib imports.

Tie-breaking rule:
    FCFS tie on arrival -> lower PID index (insertion order).
"""

from __future__ import annotations

from typing import Any

from scheduling.metrics import compute_metrics
from scheduling.models import Process, Segment, SimResult


def schedule_fcfs(processes: list[Process], **config: Any) -> SimResult:
    """Schedules processes using First-Come First-Served (FCFS).

    Args:
        processes: List of processes to schedule.
        **config: Additional algorithm configuration (unused for FCFS).

    Returns:
        SimResult containing timeline, metrics, and summary stats.
    """
    if not processes:
        raise ValueError("Process list cannot be empty.")

    # Track insertion order for tie-breaking: (arrival_time, insertion_index, Process)
    sorted_processes = sorted(
        enumerate(processes),
        key=lambda item: (item[1].arrival_time, item[0]),
    )

    timeline: list[Segment] = []
    current_time = 0

    for idx, p in sorted_processes:
        if current_time < p.arrival_time:
            # CPU is idle until process arrives
            timeline.append(Segment(pid=None, start=current_time, end=p.arrival_time))
            current_time = p.arrival_time

        start = current_time
        end = start + p.burst_time
        timeline.append(Segment(pid=p.pid, start=start, end=end))
        current_time = end

    return compute_metrics(
        processes=processes,
        timeline=timeline,
        algorithm_name="First-Come First-Served (FCFS)",
        config=config,
    )
