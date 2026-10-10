"""Process Table Widget displaying currently configured processes.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from scheduling.models import Process
from styles.theme import get_process_color


class ProcessTableWidget(QWidget):
    """Table widget presenting the list of processes with an empty state placeholder."""

    delete_requested = Signal(str)  # Emits PID to delete

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._processes: list[Process] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "PID",
            "Arrival",
            "Burst",
            "Priority",
            "Del",
        ])
        self.table.horizontalHeader().setVisible(True)
        self.table.horizontalHeader().setFixedHeight(30)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 45)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setStyleSheet(
            "QHeaderView::section { background-color: #0B1F3A; color: #FFFFFF; font-weight: bold; font-size: 9pt; padding: 6px; border: none; border-right: 1px solid #1A365D; }"
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.empty_label = QLabel("No processes yet — click Load Example or Add Process.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #6B7A90; font-size: 11pt; padding: 30px;")

        layout.addWidget(self.empty_label)
        layout.addWidget(self.table)
        self.table.hide()

    def set_processes(self, processes: list[Process]) -> None:
        """Updates table contents with the given list of processes."""
        self._processes = list(processes)
        if not self._processes:
            self.table.setRowCount(0)
            self.table.hide()
            self.empty_label.show()
            return

        self.empty_label.hide()
        self.table.show()
        self.table.horizontalHeader().setVisible(True)
        self.table.setRowCount(len(self._processes))

        for row, p in enumerate(self._processes):
            color = get_process_color(row)
            pid_item = QTableWidgetItem(p.pid)
            pid_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            pid_item.setData(Qt.ItemDataRole.UserRole, p.pid)
            pid_font = QFont()
            pid_font.setBold(True)
            pid_item.setFont(pid_font)
            pid_item.setForeground(QColor(color))

            at_item = QTableWidgetItem(str(p.arrival_time))
            at_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            bt_item = QTableWidgetItem(str(p.burst_time))
            bt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            pri_item = QTableWidgetItem(str(p.priority))
            pri_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(row, 0, pid_item)
            self.table.setItem(row, 1, at_item)
            self.table.setItem(row, 2, bt_item)
            self.table.setItem(row, 3, pri_item)

            # Delete button
            del_btn = QPushButton("✕")
            del_btn.setToolTip(f"Remove process {p.pid}")
            del_btn.setStyleSheet(
                "background-color: #EF4444; color: white; font-weight: bold; border-radius: 4px; padding: 2px 4px; font-size: 10pt; border: none;"
            )
            del_btn.clicked.connect(lambda _, pid=p.pid: self.delete_requested.emit(pid))
            self.table.setCellWidget(row, 4, del_btn)

    def get_processes(self) -> list[Process]:
        return list(self._processes)
