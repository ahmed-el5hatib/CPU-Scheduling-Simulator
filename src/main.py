"""Application entry point for CPU Scheduling Simulator.

Author signature: Eng Ahmed El-khatib
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from resources.version import __app_name__, __author__, __version__
from styles.theme import init_application_fonts


def main() -> int:
    """Initializes and runs the CPU Scheduling Simulator Qt application."""
    # Ensure high DPI attributes are respected
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)
    app.setOrganizationName(__author__)

    init_application_fonts()
    app_font = QFont("Segoe UI", 10)
    app_font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(app_font)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
