"""Shortest Remaining Time First (SRTF Preemptive) CPU Scheduling Algorithm.

Author signature: Eng Ahmed El-khatib
Pure Python implementation - no GUI or matplotlib imports.

Tie-breaking & Preemption rules:
    - SRTF tie on remaining -> keep running (do NOT preempt on equal).
    - Ready queue tie on remaining -> earlier arrival, then insertion order.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scheduling.metrics import compute_metrics
from scheduling.models import Process, Segment, SimResult


@dataclass
class _SRTFProcess:
    index: int
    process: Process
    remaining_time: int


def schedule_srtf(processes: list[Process], **config: Any) -> SimResult:
    """Schedules processes using Shortest Remaining Time First (SRTF).

    Args:
        processes: List of processes to schedule.
        **config: Additional configuration options.

    Returns:
        SimResult containing timeline, metrics, and summary stats.
    """
    if not processes:
        raise ValueError("Process list cannot be empty.")

    proc_list = [
        _SRTFProcess(index=idx, process=p, remaining_time=p.burst_time)
        for idx, p in enumerate(processes)
    ]

    timeline: list[Segment] = []
    current_time = 0
    running: _SRTFProcess | None = None
    chunk_start = 0

    while any(p.remaining_time > 0 for p in proc_list) or running is not None:
        # Check if CPU is currently idle
        if running is None:
            available = [
                p
                for p in proc_list
                if p.process.arrival_time <= current_time and p.remaining_time > 0
            ]
            if not available:
                # Idle gap until next arrival
                unstarted = [
                    p
                    for p in proc_list
                    if p.remaining_time > 0 and p.process.arrival_time > current_time
                ]
                next_arrival = min(p.process.arrival_time for p in unstarted)
                timeline.append(Segment(pid=None, start=current_time, end=next_arrival))
                current_time = next_arrival
                continue

            # Pick best: min (remaining_time, arrival_time, index)
            best = min(
                available,
                key=lambda p: (
                    p.remaining_time,
                    p.process.arrival_time,
                    p.index,
                ),
            )
            running = best
            chunk_start = current_time

        # Running process is active. Determine next event time.
        # Event 1: running process completes at current_time + running.remaining_time
        finish_time = current_time + running.remaining_time

        # Event 2: next arrival strictly after current_time
        future_arrivals = [
            p.process.arrival_time
            for p in proc_list
            if p.remaining_time > 0 and p.process.arrival_time > current_time
        ]

        if not future_arrivals or min(future_arrivals) >= finish_time:
            # Runs to completion without interruption
            timeline.append(Segment(pid=running.process.pid, start=chunk_start, end=finish_time))
            current_time = finish_time
            running.remaining_time = 0
            running = None
        else:
            # An arrival happens before finish_time
            next_event_time = min(future_arrivals)
            time_advanced = next_event_time - current_time
            running.remaining_time -= time_advanced
            current_time = next_event_time

            # Check if any newly arrived process strictly beats running
            # Rule: do NOT preempt on equal remaining time
            available = [
                p
                for p in proc_list
                if p.process.arrival_time <= current_time and p.remaining_time > 0
            ]
            best = min(
                available,
                key=lambda p: (
                    p.remaining_time,
                    p.process.arrival_time,
                    p.index,
                ),
            )

            if best.remaining_time < running.remaining_time:
                # Preemption!
                timeline.append(
                    Segment(pid=running.process.pid, start=chunk_start, end=current_time)
                )
                running = best
                chunk_start = current_time
            # else: running continues, chunk_start remains the same

    return compute_metrics(
        processes=processes,
        timeline=timeline,
        algorithm_name="Shortest Remaining Time First (SRTF)",
        config=config,
    )
