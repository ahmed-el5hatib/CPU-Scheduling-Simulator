"""Algorithm Comparison View for side-by-side performance benchmarking.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from scheduling.engine import ALGORITHMS, run_simulation
from scheduling.models import Process, SimResult
from storage.export import export_comparison_to_csv
from visualization.comparison_charts import ComparisonChartsWidget


class ComparisonView(QWidget):
    """View allowing side-by-side comparison of all 6 algorithms on the active workload."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._processes: list[Process] = []
        self._results: list[SimResult] = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Control Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 8px;"
        )
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(14, 10, 14, 10)
        tb_layout.setSpacing(10)

        title = QLabel("Algorithm Benchmarking")
        title.setStyleSheet("font-size: 13pt; font-weight: bold; color: #0B1F3A;")

        lbl_rr_q = QLabel("RR Quantum:")
        lbl_rr_q.setStyleSheet("font-weight: 600; color: #475569;")
        self.spin_rr_q = QSpinBox()
        self.spin_rr_q.setRange(1, 999)
        self.spin_rr_q.setValue(2)
        self.spin_rr_q.setFixedWidth(60)

        self.btn_compare = QPushButton("⚡ Run Benchmark")
        self.btn_compare.setStyleSheet(
            "background-color: #1E6FBA; color: white; padding: 7px 16px; border-radius: 6px; font-weight: bold;"
        )
        self.btn_compare.clicked.connect(self.run_comparison)

        self.btn_export_chart = QPushButton("🖼️ Export Chart")
        self.btn_export_chart.setStyleSheet(
            "background-color: #F8FAFC; color: #0F172A; padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 6px; font-weight: 600;"
        )
        self.btn_export_chart.clicked.connect(self._on_export_chart)

        self.btn_export_csv = QPushButton("📑 Export CSV")
        self.btn_export_csv.setStyleSheet(
            "background-color: #F8FAFC; color: #0F172A; padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 6px; font-weight: 600;"
        )
        self.btn_export_csv.clicked.connect(self._on_export_csv)

        tb_layout.addWidget(title)
        tb_layout.addStretch()
        tb_layout.addWidget(lbl_rr_q)
        tb_layout.addWidget(self.spin_rr_q)
        tb_layout.addWidget(self.btn_compare)
        tb_layout.addWidget(self.btn_export_chart)
        tb_layout.addWidget(self.btn_export_csv)

        main_layout.addWidget(toolbar)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        # Workload Champions Highlight Banner
        self.banner_card = QFrame()
        self.banner_card.setStyleSheet(
            "background-color: #0B1F3A; border-radius: 8px; border: 1px solid #1E6FBA;"
        )
        banner_layout = QHBoxLayout(self.banner_card)
        banner_layout.setContentsMargins(16, 10, 16, 10)
        banner_layout.setSpacing(14)

        lbl_champ_title = QLabel("🏆 Workload Champions:")
        lbl_champ_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #38BDF8;")
        banner_layout.addWidget(lbl_champ_title)

        self.lbl_best_wt = QLabel("Best WT: —")
        self.lbl_best_wt.setStyleSheet(
            "background-color: #132D52; color: #FFFFFF; padding: 5px 10px; border-radius: 5px; font-size: 9.5pt; font-weight: 600;"
        )
        banner_layout.addWidget(self.lbl_best_wt)

        self.lbl_best_tat = QLabel("Best TAT: —")
        self.lbl_best_tat.setStyleSheet(
            "background-color: #132D52; color: #FFFFFF; padding: 5px 10px; border-radius: 5px; font-size: 9.5pt; font-weight: 600;"
        )
        banner_layout.addWidget(self.lbl_best_tat)

        self.lbl_best_rt = QLabel("Fastest RT: —")
        self.lbl_best_rt.setStyleSheet(
            "background-color: #132D52; color: #FFFFFF; padding: 5px 10px; border-radius: 5px; font-size: 9.5pt; font-weight: 600;"
        )
        banner_layout.addWidget(self.lbl_best_rt)

        self.lbl_best_util = QLabel("CPU Utilization: —")
        self.lbl_best_util.setStyleSheet(
            "background-color: #132D52; color: #FFFFFF; padding: 5px 10px; border-radius: 5px; font-size: 9.5pt; font-weight: 600;"
        )
        banner_layout.addWidget(self.lbl_best_util)

        banner_layout.addStretch()
        content_layout.addWidget(self.banner_card)

        # Comparison Charts Card
        chart_card = QFrame()
        chart_card.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 8px;"
        )
        cc_layout = QVBoxLayout(chart_card)
        cc_layout.setContentsMargins(10, 10, 10, 10)
        self.chart_widget = ComparisonChartsWidget()
        cc_layout.addWidget(self.chart_widget)
        content_layout.addWidget(chart_card)

        # Comparison Table Card
        table_card = QFrame()
        table_card.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 8px;"
        )
        tc_layout = QVBoxLayout(table_card)
        tc_layout.setContentsMargins(12, 12, 12, 12)

        tbl_title = QLabel("Comparative Summary Metrics (Green indicates workload optimum)")
        tbl_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #0B1F3A;")
        tc_layout.addWidget(tbl_title)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Algorithm",
            "Preemptive?",
            "Avg TAT",
            "Avg WT",
            "Avg RT",
            "CPU Utilization",
            "Throughput",
            "Span (Busy/Idle)",
        ])
        self.table.horizontalHeader().setVisible(True)
        self.table.horizontalHeader().setFixedHeight(30)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setStyleSheet(
            "QHeaderView::section { background-color: #0B1F3A; color: #FFFFFF; font-weight: bold; font-size: 9pt; padding: 6px; border: none; border-right: 1px solid #1A365D; }"
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tc_layout.addWidget(self.table)

        content_layout.addWidget(table_card)
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def set_processes(self, processes: list[Process]) -> None:
        self._processes = list(processes)
        if self._processes:
            self.run_comparison()
        else:
            self.chart_widget.render_empty_state("No processes to compare. Add processes in Process Manager.")
            self.table.setRowCount(0)
            self._update_champions_banner([])

    def run_comparison(self) -> None:
        """Executes all algorithms against the current workload and updates charts and table."""
        if not self._processes:
            self.chart_widget.render_empty_state("No processes to compare. Add processes in Process Manager.")
            self.table.setRowCount(0)
            self._update_champions_banner([])
            return

        q = self.spin_rr_q.value()
        results: list[SimResult] = []

        for key in ALGORITHMS:
            config: dict[str, Any] = {"quantum": q} if key == "round_robin" else {}
            try:
                res = run_simulation(key, self._processes, **config)
                results.append(res)
            except Exception:
                pass

        self._results = results
        self.chart_widget.render_comparison(results)
        self._populate_table(results)
        self._update_champions_banner(results)

    def _update_champions_banner(self, results: list[SimResult]) -> None:
        if not results:
            self.lbl_best_wt.setText("Best WT: —")
            self.lbl_best_tat.setText("Best TAT: —")
            self.lbl_best_rt.setText("Fastest RT: —")
            self.lbl_best_util.setText("CPU Utilization: —")
            return

        best_wt_res = min(results, key=lambda r: r.avg_waiting_time)
        best_tat_res = min(results, key=lambda r: r.avg_turnaround_time)
        best_rt_res = min(results, key=lambda r: r.avg_response_time)
        best_util_res = max(results, key=lambda r: r.cpu_utilization)

        self.lbl_best_wt.setText(f"⏱️ Best WT: {best_wt_res.algorithm_name.split('(')[0].strip()} ({best_wt_res.avg_waiting_time:.2f})")
        self.lbl_best_tat.setText(f"🏁 Best TAT: {best_tat_res.algorithm_name.split('(')[0].strip()} ({best_tat_res.avg_turnaround_time:.2f})")
        self.lbl_best_rt.setText(f"🚀 Fastest RT: {best_rt_res.algorithm_name.split('(')[0].strip()} ({best_rt_res.avg_response_time:.2f})")
        self.lbl_best_util.setText(f"⚡ CPU Util: {best_util_res.cpu_utilization * 100:.1f}%")

    def _populate_table(self, results: list[SimResult]) -> None:
        self.table.setRowCount(len(results))
        if not results:
            return

        min_tat = min(r.avg_turnaround_time for r in results)
        min_wt = min(r.avg_waiting_time for r in results)
        min_rt = min(r.avg_response_time for r in results)
        max_util = max(r.cpu_utilization for r in results)

        emerald = QColor("#059669")
        white = QColor("#FFFFFF")
        bold_font = QFont()
        bold_font.setBold(True)

        for row, r in enumerate(results):
            algo_key = r.algorithm_name.lower()
            if "non-preemptive" in algo_key or "fcfs" in algo_key or "sjf" in algo_key:
                is_preempt = "No"
            elif "preemptive" in algo_key or "srtf" in algo_key or "round robin" in algo_key:
                is_preempt = "Yes"
            else:
                is_preempt = "No"


            items = [
                QTableWidgetItem(r.algorithm_name),
                QTableWidgetItem(is_preempt),
                QTableWidgetItem(f"{r.avg_turnaround_time:.2f}"),
                QTableWidgetItem(f"{r.avg_waiting_time:.2f}"),
                QTableWidgetItem(f"{r.avg_response_time:.2f}"),
                QTableWidgetItem(f"{r.cpu_utilization * 100:.1f}%"),
                QTableWidgetItem(f"{r.throughput:.3f}"),
                QTableWidgetItem(f"{r.span} ({r.busy_time}/{r.idle_time})"),
            ]

            # Highlight best values with emerald badge
            if abs(r.avg_turnaround_time - min_tat) < 1e-4:
                items[2].setBackground(emerald)
                items[2].setForeground(white)
                items[2].setFont(bold_font)
                items[2].setToolTip("Lowest Turnaround Time")
            if abs(r.avg_waiting_time - min_wt) < 1e-4:
                items[3].setBackground(emerald)
                items[3].setForeground(white)
                items[3].setFont(bold_font)
                items[3].setToolTip("Lowest Waiting Time")
            if abs(r.avg_response_time - min_rt) < 1e-4:
                items[4].setBackground(emerald)
                items[4].setForeground(white)
                items[4].setFont(bold_font)
                items[4].setToolTip("Fastest Response Time")
            if abs(r.cpu_utilization - max_util) < 1e-4 and r.cpu_utilization > 0:
                items[5].setBackground(emerald)
                items[5].setForeground(white)
                items[5].setFont(bold_font)
                items[5].setToolTip("Highest CPU Utilization")

            for col, item in enumerate(items):
                if col > 0:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)

    def _on_export_chart(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Comparison Chart",
            "comparison_chart.png",
            "PNG Image (*.png);;PDF Document (*.pdf);;SVG Vector (*.svg)",
        )
        if file_path:
            self.chart_widget.export_image(file_path)

    def _on_export_csv(self) -> None:
        if not self._results:
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Comparison Benchmark CSV",
            "comparison_benchmark.csv",
            "CSV Spreadsheet (*.csv)",
        )
        if file_path:
            export_comparison_to_csv(self._results, file_path)

