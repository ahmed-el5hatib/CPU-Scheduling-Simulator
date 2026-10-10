"""JSON Scenario persistence (save/load) for CPU Scheduling Simulator.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

import json
from typing import Any

from scheduling.models import Process


def save_scenario_to_json(
    processes: list[Process],
    file_path: str,
    scenario_name: str = "Custom Scenario",
) -> None:
    """Saves a list of Process objects to a JSON file."""
    data: dict[str, Any] = {
        "scenario_name": scenario_name,
        "author": "Eng Ahmed El-khatib",
        "version": "1.0.0",
        "processes": [
            {
                "pid": p.pid,
                "arrival_time": p.arrival_time,
                "burst_time": p.burst_time,
                "priority": p.priority,
                "color": p.color,
            }
            for p in processes
        ],
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_scenario_from_json(file_path: str) -> list[Process]:
    """Loads a list of Process objects from a JSON scenario file.

    Raises:
        ValueError: If file content is invalid or missing required fields.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict) or "processes" not in data:
        raise ValueError("Invalid scenario file format: missing 'processes' list.")

    proc_list = data["processes"]
    if not isinstance(proc_list, list):
        raise ValueError("Scenario 'processes' field must be a list.")

    processes: list[Process] = []
    for item in proc_list:
        if not isinstance(item, dict):
            raise ValueError(f"Invalid process entry: {item}")
        processes.append(
            Process(
                pid=str(item["pid"]),
                arrival_time=int(item["arrival_time"]),
                burst_time=int(item["burst_time"]),
                priority=int(item.get("priority", 0)),
                color=item.get("color"),
            )
        )
    return processes
