"""Simulation engine and algorithm registry for CPU scheduling.

Author signature: Eng Ahmed El-khatib
This module MUST NOT import PySide6 or matplotlib. Pure Python only.
"""

from __future__ import annotations

from typing import Any, Callable

from scheduling.algorithms.fcfs import schedule_fcfs
from scheduling.algorithms.preemptive_priority import schedule_preemptive_priority
from scheduling.algorithms.priority import schedule_priority
from scheduling.algorithms.round_robin import schedule_round_robin
from scheduling.algorithms.sjf import schedule_sjf
from scheduling.algorithms.srtf import schedule_srtf
from scheduling.models import Process, SimResult

SchedulerFn = Callable[..., SimResult]

ALGORITHMS: dict[str, dict[str, Any]] = {
    "fcfs": {
        "name": "First-Come First-Served (FCFS)",
        "func": schedule_fcfs,
        "is_preemptive": False,
        "requires_priority": False,
        "requires_quantum": False,
        "description": "Executes processes in the exact order of their arrival.",
    },
    "sjf": {
        "name": "Shortest Job First (SJF)",
        "func": schedule_sjf,
        "is_preemptive": False,
        "requires_priority": False,
        "requires_quantum": False,
        "description": "Non-preemptive scheduling prioritizing processes with the shortest burst time.",
    },
    "priority": {
        "name": "Priority (Non-preemptive)",
        "func": schedule_priority,
        "is_preemptive": False,
        "requires_priority": True,
        "requires_quantum": False,
        "description": "Non-preemptive scheduling prioritizing lower numerical priority values.",
    },
    "srtf": {
        "name": "Shortest Remaining Time First (SRTF)",
        "func": schedule_srtf,
        "is_preemptive": True,
        "requires_priority": False,
        "requires_quantum": False,
        "description": "Preemptive SJF scheduling strictly preempting on shorter remaining burst.",
    },
    "round_robin": {
        "name": "Round Robin (RR)",
        "func": schedule_round_robin,
        "is_preemptive": True,
        "requires_priority": False,
        "requires_quantum": True,
        "description": "Time-sliced cyclic scheduling with fixed quantum duration.",
    },
    "preemptive_priority": {
        "name": "Preemptive Priority",
        "func": schedule_preemptive_priority,
        "is_preemptive": True,
        "requires_priority": True,
        "requires_quantum": False,
        "description": "Preemptive scheduling prioritizing lower numerical priority values.",
    },
}


def validate_processes(processes: list[Process]) -> None:
    """Validates the input list of processes.

    Raises:
        ValueError: If processes list is empty or contains duplicate PIDs.
    """
    if not processes:
        raise ValueError("Process list cannot be empty.")

    seen_pids: set[str] = set()
    for p in processes:
        if not isinstance(p, Process):
            raise TypeError(f"Expected Process instance, got: {type(p).__name__}")
        if p.pid in seen_pids:
            raise ValueError(f"Duplicate PID detected: {p.pid!r}")
        seen_pids.add(p.pid)


def run_simulation(
    algorithm: str,
    processes: list[Process],
    **config: Any,
) -> SimResult:
    """Executes a CPU scheduling simulation for the selected algorithm.

    Args:
        algorithm: Algorithm key (e.g. 'fcfs', 'sjf', 'priority', 'srtf', 'round_robin', 'preemptive_priority').
        processes: List of Process instances to schedule.
        **config: Algorithm configuration (e.g. quantum=2 for round_robin).

    Returns:
        SimResult containing execution timeline and calculated metrics.

    Raises:
        ValueError: If algorithm is unknown or processes list is invalid.
    """
    validate_processes(processes)

    key = algorithm.strip().lower()
    if key not in ALGORITHMS:
        # Also check display names
        matched_key = None
        for k, info in ALGORITHMS.items():
            if info["name"].lower() == key:
                matched_key = k
                break
        if matched_key:
            key = matched_key
        else:
            valid_keys = ", ".join(repr(k) for k in ALGORITHMS.keys())
            raise ValueError(
                f"Unknown scheduling algorithm: {algorithm!r}. Valid options: {valid_keys}"
            )

    scheduler_fn: SchedulerFn = ALGORITHMS[key]["func"]
    return scheduler_fn(processes, **config)
