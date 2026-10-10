"""Shortest Job First (SJF Non-preemptive) CPU Scheduling Algorithm.

Author signature: Eng Ahmed El-khatib
Pure Python implementation - no GUI or matplotlib imports.

Tie-breaking rule:
    SJF tie on burst -> earlier arrival, then insertion order.
"""

from __future__ import annotations

from typing import Any

from scheduling.metrics import compute_metrics
from scheduling.models import Process, Segment, SimResult


def schedule_sjf(processes: list[Process], **config: Any) -> SimResult:
    """Schedules processes using non-preemptive Shortest Job First (SJF).

    Args:
        processes: List of processes to schedule.
        **config: Additional configuration options.

    Returns:
        SimResult containing timeline, metrics, and summary stats.
    """
    if not processes:
        raise ValueError("Process list cannot be empty.")

    # List of tuples: (insertion_index, Process)
    remaining = list(enumerate(processes))
    timeline: list[Segment] = []
    current_time = 0

    while remaining:
        # Arrived processes at current_time
        available = [item for item in remaining if item[1].arrival_time <= current_time]

        if not available:
            # Advance to earliest arrival among remaining
            next_arrival = min(item[1].arrival_time for item in remaining)
            timeline.append(Segment(pid=None, start=current_time, end=next_arrival))
            current_time = next_arrival
            continue

        # Tie-breaking: (burst_time, arrival_time, insertion_index)
        best_item = min(
            available,
            key=lambda item: (item[1].burst_time, item[1].arrival_time, item[0]),
        )

        remaining.remove(best_item)
        idx, p = best_item

        start = current_time
        end = start + p.burst_time
        timeline.append(Segment(pid=p.pid, start=start, end=end))
        current_time = end

    return compute_metrics(
        processes=processes,
        timeline=timeline,
        algorithm_name="Shortest Job First (SJF)",
        config=config,
    )
