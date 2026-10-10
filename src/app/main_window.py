"""Main Application Window for CPU Scheduling Simulator.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.about_dialog import AboutDialog
from app.navigation import NavigationWidget
from app.views.comparison import ComparisonView
from app.views.dashboard import DashboardView
from app.views.guide import GuideView
from app.views.process_manager import ProcessManagerView
from app.views.simulator import SimulatorView
from resources.version import __app_name__, __author__


class MainWindow(QMainWindow):
    """Main Application Window housing the Header, Sidebar, Workspace, and Footer."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{__app_name__} — {__author__}")
        self.resize(1260, 840)
        self.setMinimumSize(980, 680)

        # Apply QSS
        import sys

        base_dir = getattr(sys, "_MEIPASS", Path(__file__).parent.parent)
        qss_path = Path(base_dir) / "styles" / "app.qss"
        if not qss_path.exists():
            qss_path = Path(__file__).parent.parent / "styles" / "app.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text(encoding="utf-8"))


        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Header Frame
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(20, 10, 20, 10)

        titles_layout = QVBoxLayout()
        titles_layout.setSpacing(2)

        lbl_title = QLabel(__app_name__)
        lbl_title.setObjectName("headerTitle")

        lbl_subtitle = QLabel(
            "Operating Systems Educational Workbench & Interactive Simulation"
        )
        lbl_subtitle.setObjectName("headerSubtitle")

        titles_layout.addWidget(lbl_title)
        titles_layout.addWidget(lbl_subtitle)
        h_layout.addLayout(titles_layout)
        h_layout.addStretch()

        btn_about = QPushButton("ℹ️ About")
        btn_about.setStyleSheet(
            "background-color: #132D52; color: #FFFFFF; border: 1px solid #1E6FBA; padding: 7px 16px; border-radius: 6px; font-weight: 600;"
        )
        btn_about.clicked.connect(self._show_about_dialog)
        h_layout.addWidget(btn_about)

        root_layout.addWidget(header_frame)

        # 2. Main Middle Body (Sidebar + Workspace)
        middle_widget = QWidget()
        m_layout = QHBoxLayout(middle_widget)
        m_layout.setContentsMargins(0, 0, 0, 0)
        m_layout.setSpacing(0)

        # Sidebar
        self.nav = NavigationWidget()
        self.nav.page_changed.connect(self._on_navigate)
        m_layout.addWidget(self.nav)

        # Workspace Stacked Widget
        self.stacked = QStackedWidget()
        self.view_dashboard = DashboardView()
        self.view_pm = ProcessManagerView()
        self.view_sim = SimulatorView()
        self.view_comp = ComparisonView()
        self.view_guide = GuideView()

        self.stacked.addWidget(self.view_dashboard)  # Index 0
        self.stacked.addWidget(self.view_pm)         # Index 1
        self.stacked.addWidget(self.view_sim)        # Index 2
        self.stacked.addWidget(self.view_comp)       # Index 3
        self.stacked.addWidget(self.view_guide)      # Index 4

        m_layout.addWidget(self.stacked, 1)
        root_layout.addWidget(middle_widget, 1)

        # 3. Footer Frame (Always Visible)
        footer_frame = QFrame()
        footer_frame.setObjectName("footerFrame")
        f_layout = QHBoxLayout(footer_frame)
        f_layout.setContentsMargins(20, 6, 20, 6)

        footer_text = QLabel("Operating Systems | CPU Scheduling Simulator | Eng Ahmed El-khatib")
        footer_text.setObjectName("footerLabel")
        footer_text.setStyleSheet("color: #CBD5E1; font-weight: 500; font-size: 10pt;")
        f_layout.addWidget(footer_text)
        f_layout.addStretch()

        footer_right = QLabel("Production Desktop Architecture")
        footer_right.setStyleSheet("color: #64748B; font-size: 9pt;")
        f_layout.addWidget(footer_right)

        root_layout.addWidget(footer_frame)

        # Wire cross-view data synchronization
        self.view_pm.processes_updated.connect(self._on_pm_processes_updated)
        self.view_sim.processes_updated.connect(self._on_sim_processes_updated)
        self.view_dashboard.processes_updated.connect(self._on_pm_processes_updated)
        self.view_dashboard.navigate_requested.connect(self.nav.set_current_index)
        self.view_dashboard.run_algo_requested.connect(self._on_dashboard_run_algo)

        # Initial data sync
        initial_procs = self.view_pm.get_processes()
        self._on_pm_processes_updated(initial_procs)

    def _on_navigate(self, index: int) -> None:
        self.stacked.setCurrentIndex(index)
        if index == 3:
            self.view_comp.run_comparison()

    def _on_pm_processes_updated(self, processes: list) -> None:
        self.view_dashboard.set_processes(processes)
        self.view_sim.set_processes(processes)
        self.view_comp.set_processes(processes)

    def _on_sim_processes_updated(self, processes: list) -> None:
        self.view_dashboard.set_processes(processes)
        self.view_pm.set_processes(processes)
        self.view_comp.set_processes(processes)

    def _on_dashboard_run_algo(self, algo_key: str) -> None:
        self.nav.set_current_index(2)  # Switch to Simulator view
        for i in range(self.view_sim.combo_algo.count()):
            if self.view_sim.combo_algo.itemData(i) == algo_key:
                self.view_sim.combo_algo.setCurrentIndex(i)
                break
        self.view_sim.run_current_simulation()

    def _show_about_dialog(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()
