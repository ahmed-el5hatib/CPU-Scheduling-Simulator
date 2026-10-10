"""Metrics Table and Summary Cards Widget for CPU Scheduling Simulator.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from scheduling.models import SimResult
from styles.theme import get_process_color


class MetricsTableWidget(QWidget):
    """Widget presenting per-process metrics and overall system summary statistics."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 1. Summary Cards Frame
        self.summary_frame = QFrame()
        self.summary_frame.setProperty("class", "cardFrame")
        self.summary_frame.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 8px; padding: 12px;"
        )
        summary_layout = QGridLayout(self.summary_frame)
        summary_layout.setContentsMargins(8, 8, 8, 8)
        summary_layout.setSpacing(12)

        self.card_span = self._create_card("Schedule Span", "0")
        self.card_busy = self._create_card("Busy Time", "0")
        self.card_idle = self._create_card("Idle Time", "0")
        self.card_util = self._create_card("CPU Utilization", "0.0%")
        self.card_tp = self._create_card("Throughput", "0.00")
        self.card_tat = self._create_card("Avg Turnaround (TAT)", "0.00")
        self.card_wt = self._create_card("Avg Waiting (WT)", "0.00")
        self.card_rt = self._create_card("Avg Response (RT)", "0.00")

        summary_layout.addWidget(self.card_span, 0, 0)
        summary_layout.addWidget(self.card_busy, 0, 1)
        summary_layout.addWidget(self.card_idle, 0, 2)
        summary_layout.addWidget(self.card_util, 0, 3)
        summary_layout.addWidget(self.card_tp, 1, 0)
        summary_layout.addWidget(self.card_tat, 1, 1)
        summary_layout.addWidget(self.card_wt, 1, 2)
        summary_layout.addWidget(self.card_rt, 1, 3)

        layout.addWidget(self.summary_frame)

        # 2. Per-Process Table
        table_container = QFrame()
        table_container.setProperty("class", "cardFrame")
        table_container.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 8px; padding: 8px;"
        )
        tc_layout = QVBoxLayout(table_container)
        tc_layout.setContentsMargins(4, 4, 4, 4)

        tbl_title = QLabel("Per-Process Performance Metrics")
        tbl_title.setStyleSheet("font-size: 11pt; font-weight: bold; color: #0B1F3A;")
        tc_layout.addWidget(tbl_title)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "PID",
            "Arrival (AT)",
            "Burst (BT)",
            "Priority",
            "Start (ST)",
            "Completion (CT)",
            "Turnaround (TAT)",
            "Waiting (WT)",
            "Response (RT)",
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setStyleSheet(
            "QHeaderView::section { background-color: #0B1F3A; color: #FFFFFF; font-weight: bold; font-size: 9pt; padding: 6px; border: none; border-right: 1px solid #1A365D; }"
        )
        self.table.verticalHeader().setDefaultSectionSize(32)
        self.table.setMinimumHeight(200)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tc_layout.addWidget(self.table)

        layout.addWidget(table_container)

    def _create_card(self, title: str, default_val: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px;"
        )
        cl = QVBoxLayout(card)
        cl.setContentsMargins(4, 4, 4, 4)
        cl.setSpacing(2)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #64748B; font-size: 9pt; font-weight: 600;")
        lbl_val = QLabel(default_val)
        lbl_val.setStyleSheet("color: #0B1F3A; font-size: 13pt; font-weight: 700;")
        lbl_val.setObjectName("val")

        cl.addWidget(lbl_title)
        cl.addWidget(lbl_val)
        return card

    def _update_card_val(self, card: QFrame, val: str) -> None:
        lbl = card.findChild(QLabel, "val")
        if lbl:
            lbl.setText(val)

    def set_result(self, result: SimResult | None) -> None:
        """Populates the cards and table with simulation results."""
        if result is None or not result.process_metrics:
            self._update_card_val(self.card_span, "0")
            self._update_card_val(self.card_busy, "0")
            self._update_card_val(self.card_idle, "0")
            self._update_card_val(self.card_util, "0.0%")
            self._update_card_val(self.card_tp, "0.00")
            self._update_card_val(self.card_tat, "0.00")
            self._update_card_val(self.card_wt, "0.00")
            self._update_card_val(self.card_rt, "0.00")
            self.table.setRowCount(0)
            return

        self._update_card_val(self.card_span, str(result.span))
        self._update_card_val(self.card_busy, str(result.busy_time))
        self._update_card_val(self.card_idle, str(result.idle_time))
        self._update_card_val(self.card_util, f"{result.cpu_utilization * 100:.1f}%")
        self._update_card_val(self.card_tp, f"{result.throughput:.3f}")
        self._update_card_val(self.card_tat, f"{result.avg_turnaround_time:.2f}")
        self._update_card_val(self.card_wt, f"{result.avg_waiting_time:.2f}")
        self._update_card_val(self.card_rt, f"{result.avg_response_time:.2f}")

        self.table.setRowCount(len(result.process_metrics))
        for row, m in enumerate(result.process_metrics):
            vals = [
                m.pid,
                str(m.arrival_time),
                str(m.burst_time),
                str(m.priority),
                str(m.start_time),
                str(m.completion_time),
                str(m.turnaround_time),
                str(m.waiting_time),
                str(m.response_time),
            ]
            color = get_process_color(row)
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 0:
                    p_font = QFont()
                    p_font.setBold(True)
                    item.setFont(p_font)
                    item.setForeground(QColor(color))
                self.table.setItem(row, col, item)
