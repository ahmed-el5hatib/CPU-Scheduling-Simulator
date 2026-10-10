"""CSV Export utility for CPU scheduling simulator data and results.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

import csv
from typing import Sequence

from scheduling.models import Process, SimResult


def export_processes_to_csv(processes: Sequence[Process], file_path: str) -> None:
    """Exports process inputs to a CSV file."""
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["PID", "Arrival Time (AT)", "Burst Time (BT)", "Priority"])
        for p in processes:
            writer.writerow([p.pid, p.arrival_time, p.burst_time, p.priority])


def export_results_to_csv(result: SimResult, file_path: str) -> None:
    """Exports simulation results (per-process metrics and summary) to CSV."""
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Summary Header
        writer.writerow(["# CPU Scheduling Simulation Results"])
        writer.writerow(["Algorithm", result.algorithm_name])
        writer.writerow(["Author", "Eng Ahmed El-khatib"])
        writer.writerow(["Schedule Span", result.span])
        writer.writerow(["Busy Time", result.busy_time])
        writer.writerow(["Idle Time", result.idle_time])
        writer.writerow(["CPU Utilization", f"{result.cpu_utilization * 100:.2f}%"])
        writer.writerow(["Throughput", f"{result.throughput:.4f} proc/time-unit"])
        writer.writerow(["Average Turnaround Time", f"{result.avg_turnaround_time:.2f}"])
        writer.writerow(["Average Waiting Time", f"{result.avg_waiting_time:.2f}"])
        writer.writerow(["Average Response Time", f"{result.avg_response_time:.2f}"])
        writer.writerow([])

        # Per-Process Metrics Table
        writer.writerow([
            "PID",
            "Arrival Time (AT)",
            "Burst Time (BT)",
            "Priority",
            "Start Time (ST)",
            "Completion Time (CT)",
            "Turnaround Time (TAT)",
            "Waiting Time (WT)",
            "Response Time (RT)",
        ])
        for m in result.process_metrics:
            writer.writerow([
                m.pid,
                m.arrival_time,
                m.burst_time,
                m.priority,
                m.start_time,
                m.completion_time,
                m.turnaround_time,
                m.waiting_time,
                m.response_time,
            ])
        writer.writerow([])

        # Timeline Segments
        writer.writerow(["# Execution Timeline"])
        writer.writerow(["Segment Index", "PID", "Start Time", "End Time", "Duration"])
        for idx, seg in enumerate(result.timeline):
            writer.writerow([
                idx,
                seg.pid if seg.pid is not None else "IDLE",
                seg.start,
                seg.end,
                seg.duration,
            ])


def export_comparison_to_csv(results: Sequence[SimResult], file_path: str) -> None:
    """Exports comparative metrics across multiple algorithms to CSV."""
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["# CPU Scheduling Algorithm Comparison Benchmark"])
        writer.writerow(["Author", "Eng Ahmed El-khatib"])
        writer.writerow([])
        writer.writerow([
            "Algorithm",
            "Preemptive?",
            "Avg Turnaround Time",
            "Avg Waiting Time",
            "Avg Response Time",
            "CPU Utilization (%)",
            "Throughput (proc/unit)",
            "Schedule Span",
            "Busy Time",
            "Idle Time",
        ])
        for r in results:
            algo_key = r.algorithm_name.lower()
            if "non-preemptive" in algo_key or "fcfs" in algo_key or "sjf" in algo_key:
                is_preempt = "No"
            elif "preemptive" in algo_key or "srtf" in algo_key or "round robin" in algo_key:
                is_preempt = "Yes"
            else:
                is_preempt = "No"

            writer.writerow([
                r.algorithm_name,
                is_preempt,
                f"{r.avg_turnaround_time:.2f}",
                f"{r.avg_waiting_time:.2f}",
                f"{r.avg_response_time:.2f}",
                f"{r.cpu_utilization * 100:.2f}%",
                f"{r.throughput:.4f}",
                r.span,
                r.busy_time,
                r.idle_time,
            ])

