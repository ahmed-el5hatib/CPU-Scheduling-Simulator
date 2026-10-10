"""Embedded Matplotlib Comparison Charts Widget.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

import matplotlib

matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

from scheduling.models import SimResult
from styles.theme import ACCENT, NAVY, TEAL


def _short_algo_name(full_name: str) -> str:
    n = full_name.lower()
    if "fcfs" in n or "first-come" in n:
        return "FCFS"
    if "sjf" in n or "shortest job" in n:
        return "SJF"
    if "srtf" in n or "remaining" in n:
        return "SRTF"
    if "round robin" in n or "(rr)" in n:
        return "RR"
    if "preemptive priority" in n:
        return "P-Pri"
    if "priority" in n:
        return "NP-Pri"
    return full_name[:8]


class ComparisonChartsWidget(QWidget):
    """Embeds comparative bar charts for multiple simulation results."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.figure = Figure(figsize=(9, 3.6), dpi=100)
        self.figure.patch.set_facecolor("#FFFFFF")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self.render_empty_state()

    def render_empty_state(self, message: str = "Select algorithms to compare.") -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#FAFAFA")
        ax.text(
            0.5,
            0.5,
            message,
            ha="center",
            va="center",
            fontsize=12,
            color="#6B7A90",
            transform=ax.transAxes,
        )
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color("#E2E8F0")
        self.figure.tight_layout()
        self.canvas.draw()


    def render_comparison(self, results: list[SimResult]) -> None:
        """Renders side-by-side metric charts for multiple algorithms."""
        self.figure.clear()
        if not results:
            self.render_empty_state()
            return

        # 2 subplots: Left = Avg Times (TAT, WT, RT), Right = Utilization (%) & Throughput
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)

        names = [_short_algo_name(r.algorithm_name) for r in results]
        x = range(len(results))
        width = 0.25


        # Subplot 1: Average Latencies
        tat_vals = [r.avg_turnaround_time for r in results]
        wt_vals = [r.avg_waiting_time for r in results]
        rt_vals = [r.avg_response_time for r in results]

        x1 = [i - width for i in x]
        x2 = list(x)
        x3 = [i + width for i in x]

        ax1.bar(x1, tat_vals, width=width, label="Avg TAT", color=NAVY)
        ax1.bar(x2, wt_vals, width=width, label="Avg WT", color=ACCENT)
        ax1.bar(x3, rt_vals, width=width, label="Avg RT", color=TEAL)

        ax1.set_title("Average Times (Lower is Better)", fontsize=10, fontweight="bold", color=NAVY)
        ax1.set_xticks(list(x))
        ax1.set_xticklabels(names, rotation=20, ha="right", fontsize=9)
        ax1.set_ylabel("Time Units", fontsize=9)
        ax1.legend(fontsize=8, frameon=False)
        ax1.grid(axis="y", linestyle="--", alpha=0.3)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)

        # Subplot 2: CPU Utilization
        util_vals = [r.cpu_utilization * 100 for r in results]
        bars = ax2.bar(x, util_vals, width=0.45, color=TEAL)
        ax2.set_title("CPU Utilization (%) (Higher is Better)", fontsize=10, fontweight="bold", color=NAVY)
        ax2.set_xticks(list(x))
        ax2.set_xticklabels(names, rotation=20, ha="right", fontsize=9)
        ax2.set_ylabel("Utilization %", fontsize=9)
        ax2.set_ylim(0, 105)
        ax2.grid(axis="y", linestyle="--", alpha=0.3)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)

        for bar in bars:
            h = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                h + 1.5,
                f"{h:.1f}%",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                color=NAVY,
            )

        self.figure.tight_layout()
        self.canvas.draw()


    def export_image(self, file_path: str) -> None:
        self.figure.savefig(file_path, dpi=200, bbox_inches="tight")
