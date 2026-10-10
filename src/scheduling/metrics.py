"""Metrics computation for CPU scheduling simulation.

Author signature: Eng Ahmed El-khatib
This module MUST NOT import PySide6 or matplotlib. Pure Python only.

Definitions (strictly adhering to Section 8 of specification):
    span          = max(CT) - min(AT)  (0 if no processes)
    busy_time     = sum of all non-IDLE segment durations
    idle_time     = span - busy_time
    utilization   = busy_time / span           (0.0 if span == 0)
    throughput    = n_completed / span         (proc per time-unit; 0.0 if span == 0)
    avg WT, avg TAT, avg RT = arithmetic means over all processes.
"""

from __future__ import annotations

from typing import Any

from scheduling.models import Process, ProcessMetrics, Segment, SimResult


def compute_metrics(
    processes: list[Process],
    timeline: list[Segment],
    algorithm_name: str,
    config: dict[str, Any] | None = None,
) -> SimResult:
    """Computes all simulation metrics from the timeline and process definitions.

    Metrics are never hardcoded; they are calculated purely from the resulting timeline.
    """
    if config is None:
        config = {}

    if not processes:
        return SimResult(
            algorithm_name=algorithm_name,
            config=config,
            timeline=list(timeline),
            process_metrics=[],
            busy_time=0,
            idle_time=0,
            span=0,
            cpu_utilization=0.0,
            throughput=0.0,
            avg_turnaround_time=0.0,
            avg_waiting_time=0.0,
            avg_response_time=0.0,
        )

    # Collect first start time and completion time for each process
    first_starts: dict[str, int] = {}
    last_ends: dict[str, int] = {}
    total_burst_in_timeline: dict[str, int] = {p.pid: 0 for p in processes}

    for seg in timeline:
        if seg.pid is not None:
            if seg.pid not in first_starts:
                first_starts[seg.pid] = seg.start
            last_ends[seg.pid] = seg.end
            total_burst_in_timeline[seg.pid] = (
                total_burst_in_timeline.get(seg.pid, 0) + seg.duration
            )

    proc_metrics_list: list[ProcessMetrics] = []
    for p in processes:
        if p.pid not in first_starts or p.pid not in last_ends:
            raise ValueError(f"Process {p.pid} did not execute in the timeline.")

        st = first_starts[p.pid]
        ct = last_ends[p.pid]
        tat = ct - p.arrival_time
        wt = tat - p.burst_time
        rt = st - p.arrival_time

        proc_metrics_list.append(
            ProcessMetrics(
                pid=p.pid,
                arrival_time=p.arrival_time,
                burst_time=p.burst_time,
                priority=p.priority,
                start_time=st,
                completion_time=ct,
                turnaround_time=tat,
                waiting_time=wt,
                response_time=rt,
            )
        )

    # Section 8 Definitions:
    min_at = min(p.arrival_time for p in processes)
    max_ct = max(m.completion_time for m in proc_metrics_list)
    span = max_ct - min_at if processes else 0

    busy_time = sum(seg.duration for seg in timeline if seg.pid is not None)
    idle_time = span - busy_time
    utilization = (busy_time / span) if span > 0 else 0.0
    throughput = (len(processes) / span) if span > 0 else 0.0

    n = len(proc_metrics_list)
    avg_tat = sum(m.turnaround_time for m in proc_metrics_list) / n if n > 0 else 0.0
    avg_wt = sum(m.waiting_time for m in proc_metrics_list) / n if n > 0 else 0.0
    avg_rt = sum(m.response_time for m in proc_metrics_list) / n if n > 0 else 0.0

    return SimResult(
        algorithm_name=algorithm_name,
        config=config,
        timeline=list(timeline),
        process_metrics=proc_metrics_list,
        busy_time=busy_time,
        idle_time=idle_time,
        span=span,
        cpu_utilization=utilization,
        throughput=throughput,
        avg_turnaround_time=avg_tat,
        avg_waiting_time=avg_wt,
        avg_response_time=avg_rt,
    )
