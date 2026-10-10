"""Simulator View: All-in-one unified simulation cockpit with animated execution.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

import random
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.widgets.live_execution_panel import LiveExecutionPanel
from app.widgets.metrics_table import MetricsTableWidget
from app.widgets.process_table import ProcessTableWidget
from scheduling.engine import ALGORITHMS, run_simulation
from scheduling.models import Process, SimResult
from storage.export import export_results_to_csv
from visualization.gantt_chart import GanttChartWidget


class SimulatorView(QWidget):
    """All-in-one unified cockpit integrating workload setup, live CPU animation, Gantt chart, and metrics."""

    processes_updated = Signal(list)  # Emits list[Process] when user modifies workload

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._processes: list[Process] = []
        self._current_result: SimResult | None = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        # Main Horizontal Splitter: Left (Workload Config) & Right (Live Execution & Analytics)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            "QSplitter::handle { background-color: #CBD5E1; width: 4px; border-radius: 2px; }"
        )

        # ══════════════════════════════════════════════════════════════
        # LEFT PANE: WORKLOAD MANAGEMENT & CONFIGURATION
        # ══════════════════════════════════════════════════════════════
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 6, 0)
        left_layout.setSpacing(10)

        left_card = QFrame()
        left_card.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 8px;"
        )
        lc_layout = QVBoxLayout(left_card)
        lc_layout.setContentsMargins(12, 12, 12, 12)
        lc_layout.setSpacing(10)

        # Header Title
        lbl_workload_title = QLabel("⚙️ Workload Processes")
        lbl_workload_title.setStyleSheet("font-size: 13pt; font-weight: 700; color: #0B1F3A;")
        lc_layout.addWidget(lbl_workload_title)

        # Quick Benchmarks 2x2 Grid
        presets_grid = QGridLayout()
        presets_grid.setSpacing(6)

        self.btn_ex1 = QPushButton("⚡ Benchmark 1")
        self.btn_ex1.setToolTip("Standard textbook benchmark: 4 processes")
        self.btn_ex1.setStyleSheet(
            "background-color: #F1F5F9; color: #0F172A; border: 1px solid #CBD5E1; padding: 6px 10px; border-radius: 4px; font-weight: 600; font-size: 9pt;"
        )
        self.btn_ex1.clicked.connect(self._load_benchmark_1)

        self.btn_ex2 = QPushButton("⚡ Benchmark 2")
        self.btn_ex2.setToolTip("Gapped benchmark (forces IDLE cycles and preemption)")
        self.btn_ex2.setStyleSheet(
            "background-color: #F1F5F9; color: #0F172A; border: 1px solid #CBD5E1; padding: 6px 10px; border-radius: 4px; font-weight: 600; font-size: 9pt;"
        )
        self.btn_ex2.clicked.connect(self._load_benchmark_2)

        self.btn_rand = QPushButton("🎲 Random (5)")
        self.btn_rand.setStyleSheet(
            "background-color: #F1F5F9; color: #0F172A; border: 1px solid #CBD5E1; padding: 6px 10px; border-radius: 4px; font-weight: 600; font-size: 9pt;"
        )
        self.btn_rand.clicked.connect(self._generate_random)

        self.btn_clear = QPushButton("🗑️ Clear All")
        self.btn_clear.setStyleSheet(
            "background-color: #FEE2E2; color: #B91C1C; border: 1px solid #FECACA; padding: 6px 10px; border-radius: 4px; font-weight: 600; font-size: 9pt;"
        )
        self.btn_clear.clicked.connect(self._clear_workload)

        presets_grid.addWidget(self.btn_ex1, 0, 0)
        presets_grid.addWidget(self.btn_ex2, 0, 1)
        presets_grid.addWidget(self.btn_rand, 1, 0)
        presets_grid.addWidget(self.btn_clear, 1, 1)
        lc_layout.addLayout(presets_grid)

        # Quick Add Process Form Card
        add_frame = QFrame()
        add_frame.setStyleSheet(
            "background-color: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 6px; padding: 10px;"
        )
        af_layout = QVBoxLayout(add_frame)
        af_layout.setContentsMargins(4, 4, 4, 4)
        af_layout.setSpacing(8)

        lbl_add_title = QLabel("Add New Process")
        lbl_add_title.setStyleSheet("font-size: 10pt; font-weight: 700; color: #334155;")
        af_layout.addWidget(lbl_add_title)

        inputs_grid = QGridLayout()
        inputs_grid.setSpacing(8)

        # Row 0: PID & Priority
        lbl_pid = QLabel("PID:")
        lbl_pid.setStyleSheet("color: #475569; font-weight: 600;")
        self.input_pid = QLineEdit("P1")
        self.input_pid.setFixedWidth(80)

        lbl_pri = QLabel("Priority:")
        lbl_pri.setStyleSheet("color: #475569; font-weight: 600;")
        self.spin_pri = QSpinBox()
        self.spin_pri.setRange(1, 999)
        self.spin_pri.setValue(1)
        self.spin_pri.setFixedWidth(80)

        inputs_grid.addWidget(lbl_pid, 0, 0)
        inputs_grid.addWidget(self.input_pid, 0, 1)
        inputs_grid.addWidget(lbl_pri, 0, 2)
        inputs_grid.addWidget(self.spin_pri, 0, 3)

        # Row 1: Arrival & Burst
        lbl_at = QLabel("Arrival:")
        lbl_at.setStyleSheet("color: #475569; font-weight: 600;")
        self.spin_at = QSpinBox()
        self.spin_at.setRange(0, 999)
        self.spin_at.setValue(0)
        self.spin_at.setFixedWidth(80)

        lbl_bt = QLabel("Burst:")
        lbl_bt.setStyleSheet("color: #475569; font-weight: 600;")
        self.spin_bt = QSpinBox()
        self.spin_bt.setRange(1, 999)
        self.spin_bt.setValue(4)
        self.spin_bt.setFixedWidth(80)

        inputs_grid.addWidget(lbl_at, 1, 0)
        inputs_grid.addWidget(self.spin_at, 1, 1)
        inputs_grid.addWidget(lbl_bt, 1, 2)
        inputs_grid.addWidget(self.spin_bt, 1, 3)

        af_layout.addLayout(inputs_grid)

        self.btn_add_proc = QPushButton("➕ Add Process to Workload")
        self.btn_add_proc.setStyleSheet(
            "background-color: #1E6FBA; color: white; border-radius: 4px; padding: 6px; font-weight: bold; font-size: 10pt;"
        )
        self.btn_add_proc.clicked.connect(self._add_inline_process)
        af_layout.addWidget(self.btn_add_proc)

        lc_layout.addWidget(add_frame)

        # Process Table
        self.process_table = ProcessTableWidget()
        self.process_table.delete_requested.connect(self._delete_process)
        lc_layout.addWidget(self.process_table, 1)

        # Workload Summary Label
        self.lbl_workload_stats = QLabel("Total: 0 processes")
        self.lbl_workload_stats.setStyleSheet("color: #64748B; font-weight: 600; font-size: 9.5pt;")
        lc_layout.addWidget(self.lbl_workload_stats)

        left_layout.addWidget(left_card)
        left_widget.setMinimumWidth(380)
        splitter.addWidget(left_widget)

        # ══════════════════════════════════════════════════════════════
        # RIGHT PANE: SIMULATION CONTROLS, ANIMATION, GANTT & METRICS
        # ══════════════════════════════════════════════════════════════
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.Shape.NoFrame)
        right_scroll.setStyleSheet("background-color: transparent;")

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(6, 0, 0, 0)
        right_layout.setSpacing(10)

        # 1. Algorithm Selection & Execution Toolbar Card
        top_ctrl_card = QFrame()
        top_ctrl_card.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 8px;"
        )
        tc_layout = QHBoxLayout(top_ctrl_card)
        tc_layout.setContentsMargins(14, 10, 14, 10)
        tc_layout.setSpacing(12)

        lbl_algo = QLabel("Algorithm:")
        lbl_algo.setStyleSheet("font-weight: 700; color: #0B1F3A; font-size: 11pt;")
        self.combo_algo = QComboBox()
        for key, info in ALGORITHMS.items():
            self.combo_algo.addItem(info["name"], key)
        self.combo_algo.currentIndexChanged.connect(self._on_algorithm_changed)
        self.combo_algo.setMinimumWidth(200)

        self.lbl_quantum = QLabel("Quantum (q):")
        self.lbl_quantum.setStyleSheet("font-weight: 600; color: #0B1F3A;")
        self.spin_quantum = QSpinBox()
        self.spin_quantum.setRange(1, 999)
        self.spin_quantum.setValue(2)
        self.spin_quantum.setFixedWidth(65)

        self.btn_run = QPushButton("▶ Run Simulation")
        self.btn_run.setStyleSheet(
            "background-color: #1E6FBA; color: white; padding: 7px 16px; border-radius: 6px; font-weight: bold; font-size: 10.5pt;"
        )
        self.btn_run.clicked.connect(self.run_current_simulation)

        self.btn_export_png = QPushButton("🖼️ PNG")
        self.btn_export_png.setToolTip("Export Gantt Chart to PNG Image")
        self.btn_export_png.setStyleSheet(
            "background-color: #F8FAFC; color: #0F172A; padding: 6px 10px; border: 1px solid #CBD5E1; border-radius: 6px; font-weight: 600;"
        )
        self.btn_export_png.clicked.connect(self._on_export_gantt_png)

        self.btn_export_csv = QPushButton("📑 CSV")
        self.btn_export_csv.setToolTip("Export Performance Metrics to CSV File")
        self.btn_export_csv.setStyleSheet(
            "background-color: #F8FAFC; color: #0F172A; padding: 6px 10px; border: 1px solid #CBD5E1; border-radius: 6px; font-weight: 600;"
        )
        self.btn_export_csv.clicked.connect(self._on_export_results_csv)

        tc_layout.addWidget(lbl_algo)
        tc_layout.addWidget(self.combo_algo)
        tc_layout.addWidget(self.lbl_quantum)
        tc_layout.addWidget(self.spin_quantum)
        tc_layout.addWidget(self.btn_run)
        tc_layout.addStretch()
        tc_layout.addWidget(self.btn_export_png)
        tc_layout.addWidget(self.btn_export_csv)

        right_layout.addWidget(top_ctrl_card)

        # 2. Live Execution Animation Panel (Clock, CPU Box, Ready Queue, Controls, Event Feed)
        self.live_panel = LiveExecutionPanel()
        self.live_panel.tick_changed.connect(self._on_tick_changed)
        right_layout.addWidget(self.live_panel)

        # 3. Gantt Chart Visualization Card
        gantt_card = QFrame()
        gantt_card.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 8px;"
        )
        gc_layout = QVBoxLayout(gantt_card)
        gc_layout.setContentsMargins(12, 12, 12, 12)
        gc_layout.setSpacing(6)

        lbl_gantt_title = QLabel("📊 Execution Timeline (Gantt Chart)")
        lbl_gantt_title.setStyleSheet("font-size: 11pt; font-weight: 700; color: #0B1F3A;")
        gc_layout.addWidget(lbl_gantt_title)

        self.gantt_chart = GanttChartWidget()
        gc_layout.addWidget(self.gantt_chart)

        right_layout.addWidget(gantt_card)

        # 4. Comprehensive Performance Metrics (KPI Cards + Process Metrics Table)
        self.metrics_widget = MetricsTableWidget()
        right_layout.addWidget(self.metrics_widget)

        right_scroll.setWidget(right_container)
        splitter.addWidget(right_scroll)

        # Set initial splitter proportions (38% left, 62% right)
        splitter.setSizes([420, 800])
        main_layout.addWidget(splitter)

        self._on_algorithm_changed()

    def set_processes(self, processes: list[Process]) -> None:
        """Sets workload processes and refreshes table and simulation."""
        self._processes = list(processes)
        self.process_table.set_processes(self._processes)
        self._update_proc_stats()

        # Update inline adder suggestion
        next_idx = len(self._processes) + 1
        self.input_pid.setText(f"P{next_idx}")
        max_at = max((p.arrival_time for p in self._processes), default=0)
        self.spin_at.setValue(max_at + 1 if self._processes else 0)

        # Auto-run simulation if we already have an active simulation
        if self._current_result is not None:
            self.run_current_simulation()

    def _update_proc_stats(self) -> None:
        total_bt = sum(p.burst_time for p in self._processes)
        count = len(self._processes)
        self.lbl_workload_stats.setText(
            f"Configured: {count} processes | Cumulative burst: {total_bt} units"
        )

    def _sync_workload(self) -> None:
        self.process_table.set_processes(self._processes)
        self._update_proc_stats()
        self.processes_updated.emit(list(self._processes))
        if self._processes:
            self.run_current_simulation()
        else:
            self.gantt_chart.render_empty_state("No processes to schedule. Add processes or load a benchmark.")
            self.metrics_widget.set_result(None)

    def _add_inline_process(self) -> None:
        pid = self.input_pid.text().strip()
        if not pid:
            pid = f"P{len(self._processes) + 1}"
        if any(p.pid == pid for p in self._processes):
            pid = f"{pid}_new"

        proc = Process(
            pid=pid,
            arrival_time=self.spin_at.value(),
            burst_time=self.spin_bt.value(),
            priority=self.spin_pri.value(),
        )
        self._processes.append(proc)
        self.input_pid.setText(f"P{len(self._processes) + 1}")
        self.spin_at.setValue(proc.arrival_time + 1)
        self._sync_workload()

    def _delete_process(self, pid: str) -> None:
        self._processes = [p for p in self._processes if p.pid != pid]
        self._sync_workload()

    def _clear_workload(self) -> None:
        self._processes.clear()
        self.input_pid.setText("P1")
        self.spin_at.setValue(0)
        self._sync_workload()

    def _load_benchmark_1(self) -> None:
        """Section 6 Benchmark 1: P1(0,5,2), P2(1,3,1), P3(2,8,3), P4(4,6,4)."""
        self._processes = [
            Process("P1", arrival_time=0, burst_time=5, priority=2),
            Process("P2", arrival_time=1, burst_time=3, priority=1),
            Process("P3", arrival_time=2, burst_time=8, priority=3),
            Process("P4", arrival_time=4, burst_time=6, priority=4),
        ]
        self._sync_workload()

    def _load_benchmark_2(self) -> None:
        """Section 6 Benchmark 2: Gapped arrival with preemption P1(0,2,1), P2(5,3,2), P3(5,1,1), P4(7,4,3)."""
        self._processes = [
            Process("P1", arrival_time=0, burst_time=2, priority=1),
            Process("P2", arrival_time=5, burst_time=3, priority=2),
            Process("P3", arrival_time=5, burst_time=1, priority=1),
            Process("P4", arrival_time=7, burst_time=4, priority=3),
        ]
        self._sync_workload()

    def _generate_random(self) -> None:
        count = 5
        procs: list[Process] = []
        curr_at = 0
        for i in range(1, count + 1):
            if i > 1:
                curr_at += random.choice([0, 1, 2, 3])
            bt = random.randint(2, 7)
            pri = random.randint(1, 5)
            procs.append(Process(pid=f"P{i}", arrival_time=curr_at, burst_time=bt, priority=pri))
        self._processes = procs
        self._sync_workload()

    def _on_algorithm_changed(self) -> None:
        algo_key = self.combo_algo.currentData()
        is_rr = algo_key == "round_robin"
        self.lbl_quantum.setVisible(is_rr)
        self.spin_quantum.setVisible(is_rr)

    def run_current_simulation(self) -> None:
        """Executes simulation on active processes with selected scheduling algorithm."""
        if not self._processes:
            self.gantt_chart.render_empty_state("No processes to schedule. Add processes or load a benchmark.")
            self.metrics_widget.set_result(None)
            return

        algo_key = self.combo_algo.currentData()
        config: dict[str, Any] = {}
        if algo_key == "round_robin":
            config["quantum"] = self.spin_quantum.value()

        try:
            result = run_simulation(algo_key, self._processes, **config)
            self._current_result = result

            # Render Gantt chart & metrics & live stepper
            self.gantt_chart.render_timeline(result, current_time=0)
            self.metrics_widget.set_result(result)
            self.live_panel.load_simulation(self._processes, result)
        except Exception as e:
            self.gantt_chart.render_empty_state(f"Error executing simulation: {e}")
            self.metrics_widget.set_result(None)

    def _on_tick_changed(self, tick: int) -> None:
        """Synchronizes Gantt chart live scrubber cursor with the CPU animation clock."""
        if self._current_result is not None:
            self.gantt_chart.render_timeline(self._current_result, current_time=tick)

    def _on_export_gantt_png(self) -> None:
        if self._current_result is None or not self._current_result.timeline:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Gantt Chart", "gantt_chart.png", "PNG Images (*.png)"
        )
        if path:
            self.gantt_chart.export_image(path)

    def _on_export_results_csv(self) -> None:
        if self._current_result is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Results CSV", "results.csv", "CSV Files (*.csv)"
        )
        if path:
            export_results_to_csv(self._current_result, path)
