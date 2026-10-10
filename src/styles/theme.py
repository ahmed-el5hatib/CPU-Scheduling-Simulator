"""Theme definitions and color palette for CPU Scheduling Simulator.

Author signature: Eng Ahmed El-khatib
"""

NAVY = "#0B1F3A"
WHITE = "#FFFFFF"
ACCENT = "#1E6FBA"
ACCENT_HOVER = "#155997"
TEAL = "#17A2A2"
DANGER = "#C0392B"
MUTED = "#6B7A90"
BG_LIGHT = "#F4F7FB"
CARD_BG = "#FFFFFF"
BORDER = "#D9E2EC"
IDLE_COLOR = "#94A3B8"

PROCESS_COLORS: list[str] = [
    "#1E6FBA",  # Vibrant navy accent
    "#17A2A2",  # Teal
    "#D97706",  # Amber/Orange
    "#8B5CF6",  # Purple
    "#10B981",  # Emerald
    "#EF4444",  # Crimson
    "#0284C7",  # Sky
    "#EC4899",  # Pink
]


def get_process_color(index: int) -> str:
    """Returns a deterministic high-contrast color for a process by index."""
    return PROCESS_COLORS[index % len(PROCESS_COLORS)]


def init_application_fonts() -> None:
    """Ensures Segoe UI and Segoe UI Emoji fonts are registered in Qt QFontDatabase."""
    from pathlib import Path

    from PySide6.QtGui import QFontDatabase

    candidate_fonts = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/seguisb.ttf",
        "C:/Windows/Fonts/seguiemj.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for font_path in candidate_fonts:
        if Path(font_path).exists():
            QFontDatabase.addApplicationFont(font_path)

