"""Preemptive Priority CPU Scheduling Algorithm.

Author signature: Eng Ahmed El-khatib
Pure Python implementation - no GUI or matplotlib imports.

Convention & Preemption rules:
    - Priority convention: smaller integer = higher priority.
    - Preempt if a newly arrived process has strictly higher priority (smaller int).
    - If priorities are equal, do NOT preempt (running process continues).
    - Ready queue tie on priority -> earlier arrival, then insertion order.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scheduling.metrics import compute_metrics
from scheduling.models import Process, Segment, SimResult


@dataclass
class _PrioProcess:
    index: int
    process: Process
    remaining_time: int


def schedule_preemptive_priority(processes: list[Process], **config: Any) -> SimResult:
    """Schedules processes using Preemptive Priority Scheduling.

    Args:
        processes: List of processes to schedule.
        **config: Additional configuration options.

    Returns:
        SimResult containing timeline, metrics, and summary stats.
    """
    if not processes:
        raise ValueError("Process list cannot be empty.")

    proc_list = [
        _PrioProcess(index=idx, process=p, remaining_time=p.burst_time)
        for idx, p in enumerate(processes)
    ]

    timeline: list[Segment] = []
    current_time = 0
    running: _PrioProcess | None = None
    chunk_start = 0

    while any(p.remaining_time > 0 for p in proc_list) or running is not None:
        if running is None:
            available = [
                p
                for p in proc_list
                if p.process.arrival_time <= current_time and p.remaining_time > 0
            ]
            if not available:
                unstarted = [
                    p
                    for p in proc_list
                    if p.remaining_time > 0 and p.process.arrival_time > current_time
                ]
                next_arrival = min(p.process.arrival_time for p in unstarted)
                timeline.append(Segment(pid=None, start=current_time, end=next_arrival))
                current_time = next_arrival
                continue

            # Pick best: min (priority, arrival_time, index)
            best = min(
                available,
                key=lambda p: (
                    p.process.priority,
                    p.process.arrival_time,
                    p.index,
                ),
            )
            running = best
            chunk_start = current_time

        finish_time = current_time + running.remaining_time

        future_arrivals = [
            p.process.arrival_time
            for p in proc_list
            if p.remaining_time > 0 and p.process.arrival_time > current_time
        ]

        if not future_arrivals or min(future_arrivals) >= finish_time:
            timeline.append(Segment(pid=running.process.pid, start=chunk_start, end=finish_time))
            current_time = finish_time
            running.remaining_time = 0
            running = None
        else:
            next_event_time = min(future_arrivals)
            time_advanced = next_event_time - current_time
            running.remaining_time -= time_advanced
            current_time = next_event_time

            available = [
                p
                for p in proc_list
                if p.process.arrival_time <= current_time and p.remaining_time > 0
            ]
            best = min(
                available,
                key=lambda p: (
                    p.process.priority,
                    p.process.arrival_time,
                    p.index,
                ),
            )

            # Strict preemption: only preempt if strictly higher priority (smaller integer)
            if best.process.priority < running.process.priority:
                timeline.append(
                    Segment(pid=running.process.pid, start=chunk_start, end=current_time)
                )
                running = best
                chunk_start = current_time

    return compute_metrics(
        processes=processes,
        timeline=timeline,
        algorithm_name="Preemptive Priority",
        config=config,
    )
