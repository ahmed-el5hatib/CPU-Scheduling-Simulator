"""About Dialog for CPU Scheduling Simulator.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from resources.version import (
    __app_name__,
    __author__,
    __description__,
    __license__,
    __version__,
)


class AboutDialog(QDialog):
    """About dialog providing metadata, author signature, and technology stack."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"About — {__app_name__}")
        self.setFixedSize(520, 420)
        self.setStyleSheet("background-color: #FFFFFF; font-family: 'Segoe UI', sans-serif;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header card
        header_card = QFrame()
        header_card.setStyleSheet(
            "background-color: #0B1F3A; border-radius: 8px; padding: 16px;"
        )
        h_layout = QVBoxLayout(header_card)
        h_layout.setSpacing(4)

        lbl_app = QLabel(__app_name__)
        lbl_app.setStyleSheet("color: #FFFFFF; font-size: 16pt; font-weight: bold;")

        lbl_ver = QLabel(f"Version {__version__} | Production Desktop Release")
        lbl_ver.setStyleSheet("color: #17A2A2; font-size: 10pt; font-weight: 600;")

        h_layout.addWidget(lbl_app)
        h_layout.addWidget(lbl_ver)
        layout.addWidget(header_card)

        # Info card
        info_card = QFrame()
        info_card.setStyleSheet(
            "background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px;"
        )
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(8)

        # Author signature prominently displayed
        lbl_author = QLabel(f"<b>Author:</b> <span style='color: #1E6FBA; font-size: 11pt;'>{__author__}</span>")
        lbl_desc = QLabel(__description__)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #475569; font-size: 10pt;")

        lbl_tech = QLabel(
            "<b>Tech Stack:</b> Python 3.11 | PySide6 (Qt6) | Matplotlib 3.9 | PyTest"
        )
        lbl_tech.setStyleSheet("color: #334155; font-size: 9.5pt;")

        lbl_license = QLabel(f"<b>License:</b> {__license__} Open Educational License")
        lbl_license.setStyleSheet("color: #334155; font-size: 9.5pt;")

        info_layout.addWidget(lbl_author)
        info_layout.addWidget(lbl_desc)
        info_layout.addWidget(lbl_tech)
        info_layout.addWidget(lbl_license)
        layout.addWidget(info_card)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_close = QPushButton("Close")
        btn_close.setProperty("class", "primaryBtn")
        btn_close.setStyleSheet(
            "background-color: #1E6FBA; color: white; padding: 8px 24px; border-radius: 6px; font-weight: bold;"
        )
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)
