"""Tests for scenario JSON IO and CSV export.

Author signature: Eng Ahmed El-khatib
"""

from pathlib import Path

import pytest

from scheduling.engine import run_simulation
from scheduling.models import Process
from storage.export import (
    export_comparison_to_csv,
    export_processes_to_csv,
    export_results_to_csv,
)
from storage.scenario_io import load_scenario_from_json, save_scenario_to_json


def test_scenario_json_roundtrip(tmp_path: Path) -> None:
    procs = [
        Process("P1", arrival_time=0, burst_time=5, priority=2),
        Process("P2", arrival_time=1, burst_time=3, priority=1),
    ]
    file_path = str(tmp_path / "test_scenario.json")
    save_scenario_to_json(procs, file_path, "Test")

    loaded = load_scenario_from_json(file_path)
    assert len(loaded) == 2
    assert loaded[0].pid == "P1"
    assert loaded[0].burst_time == 5
    assert loaded[1].pid == "P2"
    assert loaded[1].priority == 1


def test_scenario_json_invalid(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.json"
    bad_file.write_text('{"missing": "processes"}', encoding="utf-8")
    with pytest.raises(ValueError, match="missing 'processes'"):
        load_scenario_from_json(str(bad_file))


def test_export_processes_and_results_csv(tmp_path: Path) -> None:
    procs = [
        Process("P1", arrival_time=0, burst_time=4, priority=1),
        Process("P2", arrival_time=2, burst_time=2, priority=2),
    ]
    csv_proc_path = str(tmp_path / "processes.csv")
    export_processes_to_csv(procs, csv_proc_path)
    assert Path(csv_proc_path).exists()
    content = Path(csv_proc_path).read_text(encoding="utf-8")
    assert "PID,Arrival Time (AT),Burst Time (BT),Priority" in content
    assert "P1,0,4,1" in content

    res = run_simulation("fcfs", procs)
    csv_res_path = str(tmp_path / "results.csv")
    export_results_to_csv(res, csv_res_path)
    assert Path(csv_res_path).exists()
    res_content = Path(csv_res_path).read_text(encoding="utf-8")
    assert "Eng Ahmed El-khatib" in res_content
    assert "First-Come First-Served (FCFS)" in res_content
    assert "P1,0,4,1,0,4,4,0,0" in res_content


def test_export_comparison_csv(tmp_path: Path) -> None:
    procs = [
        Process("P1", arrival_time=0, burst_time=4, priority=1),
        Process("P2", arrival_time=1, burst_time=2, priority=2),
    ]
    res1 = run_simulation("fcfs", procs)
    res2 = run_simulation("sjf", procs)
    csv_comp_path = str(tmp_path / "comparison.csv")
    export_comparison_to_csv([res1, res2], csv_comp_path)
    assert Path(csv_comp_path).exists()
    comp_content = Path(csv_comp_path).read_text(encoding="utf-8")
    assert "CPU Scheduling Algorithm Comparison Benchmark" in comp_content
    assert "Eng Ahmed El-khatib" in comp_content
    assert "First-Come First-Served (FCFS)" in comp_content
    assert "Shortest Job First (SJF)" in comp_content

