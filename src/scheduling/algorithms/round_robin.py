"""Round Robin (RR) CPU Scheduling Algorithm.

Author signature: Eng Ahmed El-khatib
Pure Python implementation - no GUI or matplotlib imports.

Rule & Invariant:
    - Time quantum must be an integer > 0 (otherwise raises ValueError).
    - Standard textbook rule: On quantum expiry AND new arrival at the same instant,
      the newly arrived process enters the ready queue BEFORE the preempted process.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any

from scheduling.metrics import compute_metrics
from scheduling.models import Process, Segment, SimResult


@dataclass
class _RRProcess:
    index: int
    process: Process
    remaining_time: int


def schedule_round_robin(processes: list[Process], **config: Any) -> SimResult:
    """Schedules processes using Round Robin (RR).

    Args:
        processes: List of processes to schedule.
        **config: Must contain 'quantum' (int > 0). Defaults to 2 if unspecified.

    Returns:
        SimResult containing timeline, metrics, and summary stats.

    Raises:
        ValueError: If processes is empty, or if quantum is <= 0 or not an int.
    """
    if not processes:
        raise ValueError("Process list cannot be empty.")

    quantum = config.get("quantum", 2)
    if not isinstance(quantum, int) or quantum <= 0:
        raise ValueError(
            f"Round Robin quantum must be a positive integer (> 0), got: {quantum!r}"
        )

    # Sort unarrived processes by (arrival_time, insertion_index)
    unarrived = sorted(
        [
            _RRProcess(index=idx, process=p, remaining_time=p.burst_time)
            for idx, p in enumerate(processes)
        ],
        key=lambda item: (item.process.arrival_time, item.index),
    )

    ready_queue: deque[_RRProcess] = deque()
    timeline: list[Segment] = []
    current_time = 0

    while ready_queue or unarrived:
        if not ready_queue:
            # CPU is idle until next process arrives
            next_arrival = unarrived[0].process.arrival_time
            if next_arrival > current_time:
                timeline.append(Segment(pid=None, start=current_time, end=next_arrival))
                current_time = next_arrival

            # Add all processes that have arrived at or before current_time
            while unarrived and unarrived[0].process.arrival_time <= current_time:
                ready_queue.append(unarrived.pop(0))

        # Pop from front of ready queue
        current_proc = ready_queue.popleft()
        duration = min(current_proc.remaining_time, quantum)
        start_time = current_time
        end_time = current_time + duration

        timeline.append(Segment(pid=current_proc.process.pid, start=start_time, end=end_time))
        current_time = end_time
        current_proc.remaining_time -= duration

        # TEXTBOOK RULE:
        # Check all processes that arrived strictly after start_time and up to end_time (including at end_time).
        # These newly arrived processes enter the ready queue BEFORE the preempted process.
        while unarrived and unarrived[0].process.arrival_time <= current_time:
            ready_queue.append(unarrived.pop(0))

        # If current process still has burst left, append it back to ready queue
        if current_proc.remaining_time > 0:
            ready_queue.append(current_proc)

    return compute_metrics(
        processes=processes,
        timeline=timeline,
        algorithm_name="Round Robin (RR)",
        config={"quantum": quantum},
    )
