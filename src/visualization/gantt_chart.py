"""Embedded Matplotlib Gantt Chart Widget for CPU Scheduling.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

from typing import Any

import matplotlib

matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Patch, Rectangle
from PySide6.QtWidgets import QToolTip, QVBoxLayout, QWidget

from scheduling.models import SimResult
from styles.theme import NAVY, WHITE, get_process_color


class GanttChartWidget(QWidget):
    """Embeds an interactive Matplotlib Gantt chart in a PySide6 widget.

    Shows IDLE blocks, repeated segments, process labels, integer ticks,
    and interactive tooltips.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.figure = Figure(figsize=(9, 2.8), dpi=100)
        self.figure.patch.set_facecolor("#FFFFFF")
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.canvas.setMinimumHeight(170)
        layout.addWidget(self.canvas)

        self._rect_data: list[tuple[Rectangle, str, int, int]] = []
        self._current_result: SimResult | None = None

        self.canvas.mpl_connect("motion_notify_event", self._on_hover)
        self.render_empty_state()

    def render_empty_state(self, message: str = "No simulation run yet.") -> None:
        """Renders an empty state placeholder on the canvas."""
        self.ax.clear()
        self.ax.set_facecolor("#FAFAFA")
        self.ax.text(
            0.5,
            0.5,
            message,
            ha="center",
            va="center",
            fontsize=12,
            color="#6B7A90",
            transform=self.ax.transAxes,
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_color("#E2E8F0")
        self.figure.subplots_adjust(left=0.08, right=0.95, top=0.85, bottom=0.25)
        self.canvas.draw()
        self._rect_data.clear()
        self._current_result = None


    def render_timeline(
        self,
        result: SimResult,
        highlight_index: int | None = None,
        current_time: int | None = None,
    ) -> None:
        """Renders the execution timeline from a SimResult.

        Args:
            result: SimResult containing the timeline segments.
            highlight_index: Optional index of a segment to highlight (for step playback).
            current_time: Optional clock time to draw a live playback cursor.
        """
        self._current_result = result
        self.ax.clear()
        self._rect_data.clear()

        if not result.timeline:
            self.render_empty_state("No timeline segments to display.")
            return

        self.ax.set_facecolor("#FFFFFF")
        timeline = result.timeline
        t_start = 0
        t_end = timeline[-1].end

        # Map each unique process PID to a color
        unique_pids = sorted(
            list({seg.pid for seg in timeline if seg.pid is not None})
        )
        pid_to_color = {pid: get_process_color(i) for i, pid in enumerate(unique_pids)}

        bar_height = 0.55
        y_pos = 0.5

        for idx, seg in enumerate(timeline):
            x = seg.start
            width = seg.duration
            is_hl = highlight_index is not None and idx == highlight_index

            # Calculate opacity based on current_time if provided
            if current_time is not None:
                if seg.end <= current_time:
                    alpha = 1.0
                elif seg.start < current_time < seg.end:
                    alpha = 1.0
                else:
                    alpha = 0.35  # Future segment in animation
            else:
                alpha = 1.0

            if seg.pid is None:
                # IDLE block
                face_color = "#E2E8F0"
                edge_color = "#94A3B8"
                hatch = "///"
                label_text = "IDLE"
                text_color = "#475569"
            else:
                face_color = pid_to_color.get(seg.pid, "#1E6FBA")
                edge_color = NAVY if is_hl else "#0B1F3A"
                hatch = None
                label_text = seg.pid
                text_color = WHITE

            line_width = 3.0 if is_hl else 1.2
            rect = Rectangle(
                (x, y_pos - bar_height / 2),
                width,
                bar_height,
                facecolor=face_color,
                edgecolor=edge_color,
                linewidth=line_width,
                hatch=hatch,
                alpha=alpha,
            )
            self.ax.add_patch(rect)
            self._rect_data.append((rect, label_text, seg.start, seg.end))

            # Display label if bar width is sufficient
            if width >= 0.9:
                font_weight = "bold" if is_hl else "normal"
                self.ax.text(
                    x + width / 2,
                    y_pos,
                    label_text,
                    ha="center",
                    va="center",
                    color=text_color,
                    fontsize=10 if width >= 2 else 8,
                    fontweight=font_weight,
                    alpha=alpha,
                )

        # Draw animated live cursor if current_time is set
        if current_time is not None:
            c_time = min(current_time, t_end)
            self.ax.axvline(
                x=c_time,
                color="#EF4444",
                linestyle="--",
                linewidth=2.2,
                zorder=10,
            )
            self.ax.text(
                c_time + 0.1,
                0.90,
                f"t={current_time}",
                color="#EF4444",
                fontsize=9,
                fontweight="bold",
                zorder=10,
            )

        # Configure axes
        self.ax.set_ylim(0, 1.0)
        self.ax.set_xlim(t_start, max(t_end, 1))


        # Time ticks: integer intervals
        step = 1 if t_end <= 25 else (2 if t_end <= 50 else max(1, t_end // 20))
        ticks = list(range(t_start, t_end + 1, step))
        if t_end not in ticks:
            ticks.append(t_end)
        self.ax.set_xticks(ticks)
        self.ax.set_yticks([])

        self.ax.set_xlabel("Time Units (Clock Cycles)", fontsize=10, color=NAVY, labelpad=8)
        self.ax.set_title(
            f"Gantt Chart — {result.algorithm_name} (Span: {result.span}, Busy: {result.busy_time}, Idle: {result.idle_time})",
            fontsize=11,
            fontweight="bold",
            color=NAVY,
            pad=10,
        )

        # Style grid & spines
        self.ax.grid(axis="x", linestyle="--", alpha=0.4, color="#94A3B8")
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["left"].set_visible(False)
        self.ax.spines["bottom"].set_color(NAVY)
        self.ax.spines["bottom"].set_linewidth(1.5)

        # Legend
        legend_patches = [
            Patch(facecolor=pid_to_color[pid], edgecolor=NAVY, label=pid)
            for pid in unique_pids
        ]
        if any(seg.pid is None for seg in timeline):
            legend_patches.append(
                Patch(facecolor="#E2E8F0", edgecolor="#94A3B8", hatch="///", label="IDLE")
            )

        if legend_patches:
            self.ax.legend(
                handles=legend_patches,
                loc="upper right",
                bbox_to_anchor=(1.0, 1.25),
                ncol=min(len(legend_patches), 6),
                frameon=False,
                fontsize=9,
            )

        self.figure.subplots_adjust(left=0.06, right=0.96, top=0.80, bottom=0.25)
        self.canvas.draw()


    def _on_hover(self, event: Any) -> None:
        """Displays informative tooltips with exact [start, end) on hover."""
        if event.inaxes != self.ax or not self._rect_data:
            return

        x = event.xdata
        y = event.ydata
        if x is None or y is None:
            return

        for rect, pid, start, end in self._rect_data:
            if rect.contains_point((event.x, event.y)):
                duration = end - start
                tip = f"{pid}: [{start}, {end}) | Duration: {duration}"
                QToolTip.showText(self.canvas.mapToGlobal(self.canvas.pos()), tip)
                break


    def export_image(self, file_path: str) -> None:
        """Exports the current Gantt chart to a PNG or PDF file."""
        self.figure.savefig(file_path, dpi=200, bbox_inches="tight")
