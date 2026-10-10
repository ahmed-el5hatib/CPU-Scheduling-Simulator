"""Simulation Stepper: Cycle-by-cycle state tracker for live animation.

Author signature: Eng Ahmed El-khatib
Pure Python - GUI free.
"""

from __future__ import annotations

from dataclasses import dataclass

from scheduling.models import Process, Segment, SimResult


@dataclass(frozen=True)
class StepState:
    """Represents the complete instantaneous state of the CPU and queues at clock tick t.

    Attributes:
        time: Current clock tick (integer >= 0).
        running_pid: PID of the process currently occupying the CPU, or None if IDLE.
        ready_queue: Ordered list of PIDs currently waiting in the ready queue.
        remaining_bursts: Mapping of PID to remaining CPU burst cycles at time t.
        completed_pids: List of PIDs that have completed execution at or before time t.
        event_message: Descriptive log of what is occurring at this clock instant.
    """

    time: int
    running_pid: str | None
    ready_queue: list[str]
    remaining_bursts: dict[str, int]
    completed_pids: list[str]
    event_message: str


class SimulationStepper:
    """Computes cycle-by-cycle simulation states from the processes and timeline."""

    def __init__(self, processes: list[Process], sim_result: SimResult) -> None:
        self.processes = list(processes)
        self.sim_result = sim_result
        self.states: list[StepState] = self._build_states()

    @property
    def total_ticks(self) -> int:
        return len(self.states)

    def get_state(self, tick: int) -> StepState:
        if not self.states:
            return StepState(
                time=0,
                running_pid=None,
                ready_queue=[],
                remaining_bursts={},
                completed_pids=[],
                event_message="No simulation active.",
            )
        idx = max(0, min(tick, len(self.states) - 1))
        return self.states[idx]

    def _build_states(self) -> list[StepState]:
        timeline = self.sim_result.timeline
        if not timeline or not self.processes:
            return []

        t_end = timeline[-1].end
        proc_by_pid = {p.pid: p for p in self.processes}
        states: list[StepState] = []

        # Track execution duration for each process
        executed_so_far: dict[str, int] = {p.pid: 0 for p in self.processes}

        for t in range(0, t_end + 1):
            # Check segment active at [t, t+1)
            active_seg: Segment | None = None
            if t < t_end:
                for seg in timeline:
                    if seg.start <= t < seg.end:
                        active_seg = seg
                        break

            running_pid = active_seg.pid if active_seg is not None else None

            # Calculate remaining burst for each process at start of cycle t
            remaining = {}
            for p in self.processes:
                rem = max(0, p.burst_time - executed_so_far[p.pid])
                remaining[p.pid] = rem

            completed = [p.pid for p in self.processes if remaining[p.pid] == 0]

            # Ready queue: arrived at or before t, has remaining burst, and is not running
            ready = []
            for p in self.processes:
                if p.arrival_time <= t and remaining[p.pid] > 0 and p.pid != running_pid:
                    ready.append(p.pid)

            # Sort ready queue by algorithm convention
            algo_key = self.sim_result.algorithm_name.lower()
            if "shortest" in algo_key or "sjf" in algo_key or "srtf" in algo_key:
                ready.sort(key=lambda pid: (remaining[pid], proc_by_pid[pid].arrival_time))
            elif "priority" in algo_key:
                ready.sort(key=lambda pid: (proc_by_pid[pid].priority, proc_by_pid[pid].arrival_time))
            else:
                ready.sort(key=lambda pid: proc_by_pid[pid].arrival_time)

            # Build descriptive event message
            events: list[str] = []
            # Check arrivals at instant t
            new_arrivals = [p.pid for p in self.processes if p.arrival_time == t]
            if new_arrivals:
                events.append(f"Arrival: {', '.join(new_arrivals)} entered system")

            # Check completions at instant t
            completions_at_t = [
                seg.pid for seg in timeline if seg.end == t and seg.pid is not None
            ]
            if completions_at_t:
                events.append(f"Completed: {', '.join(completions_at_t)}")

            if t < t_end:
                if running_pid is not None:
                    rem_after = remaining[running_pid]
                    events.append(f"CPU: Running {running_pid} (Burst remaining: {rem_after})")
                else:
                    events.append("CPU: IDLE (No processes ready)")
            else:
                events.append("Simulation finished: All processes completed.")

            event_str = " | ".join(events)

            states.append(
                StepState(
                    time=t,
                    running_pid=running_pid if t < t_end else None,
                    ready_queue=ready,
                    remaining_bursts=dict(remaining),
                    completed_pids=completed,
                    event_message=event_str,
                )
            )

            # Advance execution count for active process
            if running_pid is not None and t < t_end:
                executed_so_far[running_pid] += 1

        return states
