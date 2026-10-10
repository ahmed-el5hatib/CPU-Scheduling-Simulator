"""Process Manager View for configuring, editing, and managing workloads.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

import random

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.widgets.process_table import ProcessTableWidget
from scheduling.models import Process
from storage.export import export_processes_to_csv
from storage.scenario_io import load_scenario_from_json, save_scenario_to_json


class ProcessManagerView(QWidget):
    """View allowing users to add, edit, remove, import, and generate scheduling workloads."""

    processes_updated = Signal(list)  # Emits list[Process]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._processes: list[Process] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Title and description
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        title = QLabel("Process Manager")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #0B1F3A;")
        desc = QLabel(
            "Configure workload processes, load standard benchmark datasets, or generate random test cases."
        )
        desc.setStyleSheet("color: #64748B; font-size: 10.5pt;")
        header_layout.addWidget(title)
        header_layout.addWidget(desc)
        layout.addLayout(header_layout)

        # 1. Add Process Form Card
        form_card = QFrame()
        form_card.setProperty("class", "cardFrame")
        form_card.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 8px;"
        )
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(16, 14, 16, 14)

        form_title = QLabel("Add New Process")
        form_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #0B1F3A;")
        form_layout.addWidget(form_title)

        inputs_layout = QHBoxLayout()
        inputs_layout.setSpacing(16)

        # PID input
        v_pid = QVBoxLayout()
        v_pid.addWidget(QLabel("Process ID (PID):"))
        self.input_pid = QLineEdit("P1")
        self.input_pid.setFixedWidth(110)
        v_pid.addWidget(self.input_pid)
        inputs_layout.addLayout(v_pid)

        # Arrival Time
        v_at = QVBoxLayout()
        v_at.addWidget(QLabel("Arrival Time (AT ≥ 0):"))
        self.input_at = QSpinBox()
        self.input_at.setRange(0, 9999)
        self.input_at.setValue(0)
        self.input_at.setFixedWidth(130)
        v_at.addWidget(self.input_at)
        inputs_layout.addLayout(v_at)

        # Burst Time
        v_bt = QVBoxLayout()
        v_bt.addWidget(QLabel("Burst Time (BT > 0):"))
        self.input_bt = QSpinBox()
        self.input_bt.setRange(1, 9999)
        self.input_bt.setValue(4)
        self.input_bt.setFixedWidth(130)
        v_bt.addWidget(self.input_bt)
        inputs_layout.addLayout(v_bt)

        # Priority
        v_pri = QVBoxLayout()
        lbl_pri_desc = QLabel("Priority (Smaller = Higher):")
        lbl_pri_desc.setToolTip("Convention: smaller integer = higher priority (e.g. 1 is higher priority than 2).")
        v_pri.addWidget(lbl_pri_desc)
        self.input_pri = QSpinBox()
        self.input_pri.setRange(-999, 999)
        self.input_pri.setValue(1)
        self.input_pri.setFixedWidth(150)
        v_pri.addWidget(self.input_pri)
        inputs_layout.addLayout(v_pri)

        # Add Button
        v_btn = QVBoxLayout()
        v_btn.addStretch()
        self.btn_add = QPushButton("➕ Add Process")
        self.btn_add.setProperty("class", "primaryBtn")
        self.btn_add.setStyleSheet(
            "background-color: #1E6FBA; color: white; padding: 7px 18px; border-radius: 6px; font-weight: bold;"
        )
        self.btn_add.clicked.connect(self._on_add_process)
        v_btn.addWidget(self.btn_add)
        inputs_layout.addLayout(v_btn)

        inputs_layout.addStretch()
        form_layout.addLayout(inputs_layout)

        # Inline validation message
        self.lbl_form_error = QLabel("")
        self.lbl_form_error.setStyleSheet("color: #C0392B; font-weight: bold; font-size: 9.5pt;")
        form_layout.addWidget(self.lbl_form_error)

        layout.addWidget(form_card)

        # 2. Action Toolbar Card
        actions_card = QFrame()
        actions_card.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 8px;"
        )
        act_layout = QHBoxLayout(actions_card)
        act_layout.setContentsMargins(14, 10, 14, 10)
        act_layout.setSpacing(10)

        self.btn_ex1 = QPushButton("⚡ Load Example 1 (Standard)")
        self.btn_ex1.setStyleSheet("background-color: #F1F5F9; color: #0F172A; padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 5px; font-weight: 600;")
        self.btn_ex1.clicked.connect(self.load_example_1)

        self.btn_ex2 = QPushButton("⚡ Load Example 2 (Idle Gap & Preempt)")
        self.btn_ex2.setStyleSheet("background-color: #F1F5F9; color: #0F172A; padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 5px; font-weight: 600;")
        self.btn_ex2.clicked.connect(self.load_example_2)

        self.btn_rand = QPushButton("🎲 Random (4-6 Procs)")
        self.btn_rand.setStyleSheet("background-color: #F1F5F9; color: #0F172A; padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 5px; font-weight: 600;")
        self.btn_rand.clicked.connect(self.generate_random_workload)

        self.btn_clear = QPushButton("🗑️ Clear All")
        self.btn_clear.setStyleSheet("background-color: #FEE2E2; color: #991B1B; padding: 6px 12px; border: 1px solid #FCA5A5; border-radius: 5px; font-weight: 600;")
        self.btn_clear.clicked.connect(self.clear_all)

        act_layout.addWidget(self.btn_ex1)
        act_layout.addWidget(self.btn_ex2)
        act_layout.addWidget(self.btn_rand)
        act_layout.addWidget(self.btn_clear)
        act_layout.addStretch()

        self.btn_save = QPushButton("💾 Save JSON")
        self.btn_save.setStyleSheet("background-color: #F1F5F9; color: #0F172A; padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 5px;")
        self.btn_save.clicked.connect(self._on_save_scenario)

        self.btn_load = QPushButton("📂 Load JSON")
        self.btn_load.setStyleSheet("background-color: #F1F5F9; color: #0F172A; padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 5px;")
        self.btn_load.clicked.connect(self._on_load_scenario)

        self.btn_csv = QPushButton("📑 Export CSV")
        self.btn_csv.setStyleSheet("background-color: #F1F5F9; color: #0F172A; padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 5px;")
        self.btn_csv.clicked.connect(self._on_export_csv)

        act_layout.addWidget(self.btn_save)
        act_layout.addWidget(self.btn_load)
        act_layout.addWidget(self.btn_csv)

        layout.addWidget(actions_card)

        # 3. Process Table Card
        self.table_widget = ProcessTableWidget()
        self.table_widget.delete_requested.connect(self.delete_process)
        layout.addWidget(self.table_widget)

        # Initial default workload: load Example 1
        self.load_example_1()

    def _on_add_process(self) -> None:
        pid = self.input_pid.text().strip()
        at = self.input_at.value()
        bt = self.input_bt.value()
        pri = self.input_pri.value()

        if not pid:
            self.lbl_form_error.setText("Error: PID cannot be empty.")
            return

        if any(p.pid == pid for p in self._processes):
            self.lbl_form_error.setText(f"Error: Process '{pid}' already exists. Use a unique PID.")
            return

        self.lbl_form_error.setText("")
        new_proc = Process(pid=pid, arrival_time=at, burst_time=bt, priority=pri)
        self._processes.append(new_proc)
        self._sync_and_notify()

        # Auto-suggest next PID
        next_num = len(self._processes) + 1
        self.input_pid.setText(f"P{next_num}")
        self.input_at.setValue(at + 1)

    def delete_process(self, pid: str) -> None:
        self._processes = [p for p in self._processes if p.pid != pid]
        self._sync_and_notify()

    def clear_all(self) -> None:
        self._processes.clear()
        self._sync_and_notify()
        self.input_pid.setText("P1")
        self.input_at.setValue(0)

    def load_example_1(self) -> None:
        """Section 6 Example 1:

        P1 AT=0 BT=5 PRI=2
        P2 AT=1 BT=3 PRI=1
        P3 AT=2 BT=8 PRI=3
        P4 AT=4 BT=6 PRI=4
        """
        self._processes = [
            Process("P1", arrival_time=0, burst_time=5, priority=2),
            Process("P2", arrival_time=1, burst_time=3, priority=1),
            Process("P3", arrival_time=2, burst_time=8, priority=3),
            Process("P4", arrival_time=4, burst_time=6, priority=4),
        ]
        self._sync_and_notify()
        self.lbl_form_error.setText("Loaded Example 1 (Standard benchmark).")

    def load_example_2(self) -> None:
        """Section 6 Example 2 (Forces idle time and preemption):

        P1 AT=0 BT=2 PRI=1
        P2 AT=5 BT=3 PRI=2
        P3 AT=5 BT=1 PRI=1
        P4 AT=7 BT=4 PRI=3
        """
        self._processes = [
            Process("P1", arrival_time=0, burst_time=2, priority=1),
            Process("P2", arrival_time=5, burst_time=3, priority=2),
            Process("P3", arrival_time=5, burst_time=1, priority=1),
            Process("P4", arrival_time=7, burst_time=4, priority=3),
        ]
        self._sync_and_notify()
        self.lbl_form_error.setText("Loaded Example 2 (Forces idle gap [2, 5) and preemption).")

    def generate_random_workload(self) -> None:
        """Generates 4 to 6 random processes with varied AT, BT, and PRI."""
        n = random.randint(4, 6)
        procs: list[Process] = []
        curr_at = 0
        for i in range(1, n + 1):
            if i > 1 and random.random() < 0.3:
                curr_at += random.randint(1, 3)
            bt = random.randint(2, 9)
            pri = random.randint(1, 5)
            procs.append(Process(pid=f"P{i}", arrival_time=curr_at, burst_time=bt, priority=pri))
        self._processes = procs
        self._sync_and_notify()
        self.lbl_form_error.setText(f"Generated {n} random processes.")

    def _sync_and_notify(self) -> None:
        self.table_widget.set_processes(self._processes)
        self.processes_updated.emit(self.get_processes())

    def get_processes(self) -> list[Process]:
        return list(self._processes)

    def set_processes(self, processes: list[Process]) -> None:
        self._processes = list(processes)
        self.table_widget.set_processes(self._processes)

    def _on_save_scenario(self) -> None:
        if not self._processes:
            self.lbl_form_error.setText("No processes to save.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Scenario JSON", "scenario.json", "JSON Files (*.json)"
        )
        if path:
            save_scenario_to_json(self._processes, path)
            self.lbl_form_error.setText(f"Saved scenario to {path}")

    def _on_load_scenario(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Scenario JSON", "", "JSON Files (*.json)"
        )
        if path:
            try:
                loaded = load_scenario_from_json(path)
                self.set_processes(loaded)
                self.lbl_form_error.setText(f"Loaded {len(loaded)} processes from {path}")
            except Exception as e:
                self.lbl_form_error.setText(f"Error loading file: {e}")

    def _on_export_csv(self) -> None:
        if not self._processes:
            self.lbl_form_error.setText("No processes to export.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Processes CSV", "processes.csv", "CSV Files (*.csv)"
        )
        if path:
            export_processes_to_csv(self._processes, path)
            self.lbl_form_error.setText(f"Exported processes to {path}")
