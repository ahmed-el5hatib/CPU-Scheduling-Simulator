"""Data models for CPU scheduling simulation.

Author signature: Eng Ahmed El-khatib
This module MUST NOT import PySide6 or matplotlib. Pure Python only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Process:
    """Represents a process submitted to the CPU scheduler.

    Attributes:
        pid: Unique process identifier string (e.g. 'P1').
        arrival_time: Arrival time (AT >= 0).
        burst_time: CPU burst time (BT > 0).
        priority: Priority value (smaller integer = higher priority).
        color: Optional hex color string for visualization (e.g. '#1E6FBA').
    """

    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0
    color: str | None = None

    def __post_init__(self) -> None:
        if not self.pid or not isinstance(self.pid, str) or not self.pid.strip():
            raise ValueError(f"Process PID must be a non-empty string, got: {self.pid!r}")
        if not isinstance(self.arrival_time, int) or self.arrival_time < 0:
            raise ValueError(
                f"Process {self.pid} arrival_time must be an integer >= 0, got: {self.arrival_time}"
            )
        if not isinstance(self.burst_time, int) or self.burst_time <= 0:
            raise ValueError(
                f"Process {self.pid} burst_time must be an integer > 0, got: {self.burst_time}"
            )
        if not isinstance(self.priority, int):
            raise ValueError(
                f"Process {self.pid} priority must be an integer, got: {self.priority}"
            )


@dataclass(frozen=True)
class Segment:
    """Represents a contiguous block of CPU execution or idle time in the timeline.

    Attributes:
        pid: Process identifier string, or None if the CPU is IDLE.
        start: Start time of the segment (start >= 0).
        end: End time of the segment (end > start).
    """

    pid: str | None
    start: int
    end: int

    def __post_init__(self) -> None:
        if not isinstance(self.start, int) or self.start < 0:
            raise ValueError(f"Segment start time must be an integer >= 0, got: {self.start}")
        if not isinstance(self.end, int) or self.end <= self.start:
            raise ValueError(
                f"Segment end time must be an integer > start time ({self.start}), got: {self.end}"
            )

    @property
    def duration(self) -> int:
        """Returns duration of this segment."""
        return self.end - self.start

    @property
    def is_idle(self) -> bool:
        """Returns True if this segment represents CPU idle time."""
        return self.pid is None


@dataclass(frozen=True)
class ProcessMetrics:
    """Computed timing metrics for a single completed process.

    Attributes:
        pid: Process identifier.
        arrival_time: AT.
        burst_time: BT.
        priority: Priority.
        start_time: ST (first time process gained the CPU).
        completion_time: CT (time when process finished execution).
        turnaround_time: TAT = CT - AT.
        waiting_time: WT = TAT - BT.
        response_time: RT = ST - AT.
    """

    pid: str
    arrival_time: int
    burst_time: int
    priority: int
    start_time: int
    completion_time: int
    turnaround_time: int
    waiting_time: int
    response_time: int


@dataclass
class SimResult:
    """Complete simulation result returned by schedulers.

    Attributes:
        algorithm_name: Human-readable algorithm name.
        config: Configuration dictionary (e.g. {'quantum': 2}).
        timeline: List of execution/idle Segments.
        process_metrics: List of per-process computed metrics.
        busy_time: Sum of all non-IDLE segment durations.
        idle_time: span - busy_time.
        span: max(CT) - min(AT) (0 if no processes).
        cpu_utilization: busy_time / span (0.0 if span == 0).
        throughput: n_completed / span (proc/time-unit; 0.0 if span == 0).
        avg_turnaround_time: Arithmetic mean of TAT.
        avg_waiting_time: Arithmetic mean of WT.
        avg_response_time: Arithmetic mean of RT.
    """

    algorithm_name: str
    config: dict[str, Any]
    timeline: list[Segment] = field(default_factory=list)
    process_metrics: list[ProcessMetrics] = field(default_factory=list)
    busy_time: int = 0
    idle_time: int = 0
    span: int = 0
    cpu_utilization: float = 0.0
    throughput: float = 0.0
    avg_turnaround_time: float = 0.0
    avg_waiting_time: float = 0.0
    avg_response_time: float = 0.0
