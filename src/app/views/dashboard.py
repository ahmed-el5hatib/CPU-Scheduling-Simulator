"""Dashboard View: Overview, quick start shortcuts, and algorithm cards.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from scheduling.engine import ALGORITHMS
from scheduling.models import Process


class DashboardView(QWidget):
    """Landing dashboard view introducing features and providing quick navigation shortcuts."""

    navigate_requested = Signal(int)  # Page index
    run_algo_requested = Signal(str)  # Algorithm key to run in simulator
    processes_updated = Signal(list)  # Emits list[Process]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._processes: list[Process] = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        # 1. Welcome Hero Banner
        hero = QFrame()
        hero.setStyleSheet(
            "background-color: #0B1F3A; border-radius: 10px; border-bottom: 3px solid #1E6FBA;"
        )
        h_layout = QVBoxLayout(hero)
        h_layout.setContentsMargins(20, 18, 20, 18)
        h_layout.setSpacing(8)

        title = QLabel("CPU Scheduling Simulator & Visual Laboratory")
        title.setStyleSheet("color: #FFFFFF; font-size: 18pt; font-weight: bold;")
        subtitle = QLabel(
            "An interactive educational simulator for Operating Systems students and researchers. "
            "Experiment with non-preemptive and preemptive CPU scheduling algorithms, visualize Gantt timelines, "
            "and inspect deterministic performance metrics."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #CBD5E1; font-size: 10.5pt; line-height: 1.4;")

        # Feature badges strip
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(10)
        badge_items = [
            ("⚡ 6 Deterministic Algorithms", "#1E6FBA"),
            ("🎬 Real-Time Clock & Animation", "#17A2A2"),
            ("📐 11 Formal OS Invariants", "#059669"),
            ("📊 Side-by-Side Benchmarking", "#7C3AED"),
        ]
        for text, bg_col in badge_items:
            b_lbl = QLabel(text)
            b_lbl.setStyleSheet(
                f"background-color: {bg_col}; color: white; padding: 4px 10px; border-radius: 4px; font-weight: 600; font-size: 9pt;"
            )
            badges_layout.addWidget(b_lbl)
        badges_layout.addStretch()

        h_layout.addWidget(title)
        h_layout.addWidget(subtitle)
        h_layout.addLayout(badges_layout)
        layout.addWidget(hero)

        # 2. Workload Quick Status Card
        status_card = QFrame()
        status_card.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 8px;"
        )
        s_layout = QVBoxLayout(status_card)
        s_layout.setContentsMargins(16, 14, 16, 14)
        s_layout.setSpacing(10)

        top_s_layout = QHBoxLayout()
        self.lbl_workload_info = QLabel("Active Workload: 4 processes loaded")
        self.lbl_workload_info.setStyleSheet("font-size: 11pt; font-weight: bold; color: #0B1F3A;")

        btn_goto_pm = QPushButton("📋 Manage Processes")
        btn_goto_pm.setStyleSheet(
            "background-color: #F1F5F9; color: #0F172A; padding: 6px 14px; border: 1px solid #CBD5E1; border-radius: 6px; font-weight: 600;"
        )
        btn_goto_pm.clicked.connect(lambda: self.navigate_requested.emit(1))

        btn_goto_sim = QPushButton("⚙️ Open Simulator")
        btn_goto_sim.setStyleSheet(
            "background-color: #1E6FBA; color: white; padding: 6px 16px; border-radius: 6px; font-weight: 600;"
        )
        btn_goto_sim.clicked.connect(lambda: self.navigate_requested.emit(2))

        btn_goto_comp = QPushButton("📊 Compare All")
        btn_goto_comp.setStyleSheet(
            "background-color: #17A2A2; color: white; padding: 6px 16px; border-radius: 6px; font-weight: 600;"
        )
        btn_goto_comp.clicked.connect(lambda: self.navigate_requested.emit(3))

        top_s_layout.addWidget(self.lbl_workload_info)
        top_s_layout.addStretch()
        top_s_layout.addWidget(btn_goto_pm)
        top_s_layout.addWidget(btn_goto_sim)
        top_s_layout.addWidget(btn_goto_comp)
        s_layout.addLayout(top_s_layout)

        # Quick preset buttons strip
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(8)
        lbl_presets = QLabel("Quick Load Presets:")
        lbl_presets.setStyleSheet("color: #64748B; font-weight: 600; font-size: 9.5pt;")
        presets_layout.addWidget(lbl_presets)

        btn_load_b1 = QPushButton("⚡ Standard Benchmark")
        btn_load_b1.setStyleSheet(
            "background-color: #F8FAFC; color: #0F172A; padding: 4px 10px; border: 1px solid #CBD5E1; border-radius: 4px; font-size: 9pt; font-weight: 600;"
        )
        btn_load_b1.clicked.connect(self._load_b1)

        btn_load_b2 = QPushButton("⚡ Preemptive & Idle Benchmark")
        btn_load_b2.setStyleSheet(
            "background-color: #F8FAFC; color: #0F172A; padding: 4px 10px; border: 1px solid #CBD5E1; border-radius: 4px; font-size: 9pt; font-weight: 600;"
        )
        btn_load_b2.clicked.connect(self._load_b2)

        btn_load_rand = QPushButton("🎲 Random 5 Workload")
        btn_load_rand.setStyleSheet(
            "background-color: #F8FAFC; color: #0F172A; padding: 4px 10px; border: 1px solid #CBD5E1; border-radius: 4px; font-size: 9pt; font-weight: 600;"
        )
        btn_load_rand.clicked.connect(self._load_rand)

        presets_layout.addWidget(btn_load_b1)
        presets_layout.addWidget(btn_load_b2)
        presets_layout.addWidget(btn_load_rand)
        presets_layout.addStretch()
        s_layout.addLayout(presets_layout)

        layout.addWidget(status_card)


        # 3. Available Algorithms Grid
        grid_title = QLabel("Supported Scheduling Algorithms")
        grid_title.setStyleSheet("font-size: 13pt; font-weight: bold; color: #0B1F3A;")
        layout.addWidget(grid_title)

        grid = QGridLayout()
        grid.setSpacing(14)

        row, col = 0, 0
        for key, info in ALGORITHMS.items():
            card = self._create_algo_card(key, info)
            grid.addWidget(card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        layout.addLayout(grid)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _create_algo_card(self, key: str, info: dict[str, Any]) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 8px;"
        )
        cl = QVBoxLayout(card)
        cl.setContentsMargins(14, 14, 14, 14)
        cl.setSpacing(6)

        header = QHBoxLayout()
        name = QLabel(info["name"])
        name.setStyleSheet("font-size: 11pt; font-weight: bold; color: #0B1F3A;")

        badge = QLabel("PREEMPTIVE" if info["is_preemptive"] else "NON-PREEMPTIVE")
        badge_color = "#D97706" if info["is_preemptive"] else "#2563EB"
        badge.setStyleSheet(
            f"background-color: {badge_color}; color: white; font-size: 8pt; font-weight: bold; padding: 2px 6px; border-radius: 4px;"
        )

        header.addWidget(name)
        header.addStretch()
        header.addWidget(badge)
        cl.addLayout(header)

        desc = QLabel(info["description"])
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748B; font-size: 9.5pt;")
        cl.addWidget(desc)

        cl.addStretch()
        btn_run = QPushButton("Run in Simulator ▶")
        btn_run.setStyleSheet(
            "background-color: #F8FAFC; color: #1E6FBA; border: 1px solid #CBD5E1; padding: 6px 12px; border-radius: 5px; font-weight: 600;"
        )
        btn_run.clicked.connect(lambda _, k=key: self.run_algo_requested.emit(k))
        cl.addWidget(btn_run)

        return card

    def _load_b1(self) -> None:
        procs = [
            Process("P1", arrival_time=0, burst_time=5, priority=2),
            Process("P2", arrival_time=1, burst_time=3, priority=1),
            Process("P3", arrival_time=2, burst_time=8, priority=3),
            Process("P4", arrival_time=4, burst_time=6, priority=4),
        ]
        self.set_processes(procs)
        self.processes_updated.emit(procs)

    def _load_b2(self) -> None:
        procs = [
            Process("P1", arrival_time=1, burst_time=3, priority=3),
            Process("P2", arrival_time=2, burst_time=6, priority=1),
            Process("P3", arrival_time=5, burst_time=4, priority=2),
            Process("P4", arrival_time=15, burst_time=2, priority=1),
        ]
        self.set_processes(procs)
        self.processes_updated.emit(procs)

    def _load_rand(self) -> None:
        import random

        procs = []
        for i in range(1, 6):
            procs.append(
                Process(
                    pid=f"P{i}",
                    arrival_time=random.randint(0, 8),
                    burst_time=random.randint(1, 10),
                    priority=random.randint(1, 5),
                )
            )
        self.set_processes(procs)
        self.processes_updated.emit(procs)

    def set_processes(self, processes: list[Process]) -> None:
        self._processes = list(processes)
        self.lbl_workload_info.setText(
            f"Active Workload: {len(self._processes)} process(es) configured"
        )

