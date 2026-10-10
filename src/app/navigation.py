"""Sidebar Navigation Widget for CPU Scheduling Simulator.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class NavigationWidget(QWidget):
    """Sidebar navigation menu with distinct active states."""

    page_changed = Signal(int)  # Emits target page index in QStackedWidget

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("sidebarFrame")
        self.sidebar_frame.setStyleSheet(
            "QFrame#sidebarFrame { background-color: #0B1F3A; border-right: 1px solid #1A365D; }"
        )
        s_layout = QVBoxLayout(self.sidebar_frame)
        s_layout.setContentsMargins(0, 16, 0, 16)
        s_layout.setSpacing(4)

        nav_title = QLabel("  NAVIGATION")
        nav_title.setStyleSheet("color: #64748B; font-size: 8.5pt; font-weight: 700; padding: 4px 16px;")
        s_layout.addWidget(nav_title)

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        self.nav_items: list[tuple[str, int]] = [
            ("🏠  Dashboard", 0),
            ("📋  Process Manager", 1),
            ("⚙️  Simulator", 2),
            ("📊  Algorithm Comparison", 3),
            ("📖  Educational Guide", 4),
        ]

        self.buttons: list[QPushButton] = []
        for label, idx in self.nav_items:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("class", "navBtn")
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    color: #CBD5E1;
                    font-size: 11pt;
                    font-weight: 600;
                    text-align: left;
                    padding: 12px 20px;
                    border: none;
                    border-left: 4px solid transparent;
                }
                QPushButton:hover {
                    background-color: #132D52;
                    color: #FFFFFF;
                }
                QPushButton:checked {
                    background-color: #183B68;
                    color: #FFFFFF;
                    border-left: 4px solid #17A2A2;
                }
                """
            )
            btn.clicked.connect(lambda _, index=idx: self._on_btn_clicked(index))
            self.btn_group.addButton(btn, idx)
            s_layout.addWidget(btn)
            self.buttons.append(btn)

        s_layout.addStretch()

        # System info in sidebar bottom
        lbl_version = QLabel("  v1.0.0 Production")
        lbl_version.setStyleSheet("color: #64748B; font-size: 8.5pt; padding: 4px 16px;")
        s_layout.addWidget(lbl_version)

        layout.addWidget(self.sidebar_frame)
        if self.buttons:
            self.buttons[0].setChecked(True)

    def _on_btn_clicked(self, index: int) -> None:
        self.page_changed.emit(index)

    def set_current_index(self, index: int) -> None:
        if 0 <= index < len(self.buttons):
            self.buttons[index].setChecked(True)
            self.page_changed.emit(index)
