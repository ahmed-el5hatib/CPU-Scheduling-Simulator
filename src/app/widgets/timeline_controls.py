"""Timeline Playback and Step Controls Widget.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QWidget,
)


class TimelineControlsWidget(QWidget):
    """Interactive playback controls for step-by-step Gantt chart exploration."""

    step_changed = Signal(int)  # Emits current segment index

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._total_steps: int = 0
        self._current_step: int = -1
        self._is_playing: bool = False

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer_tick)
        self._timer.setInterval(800)  # Default 800ms per step

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        container = QFrame()
        container.setStyleSheet(
            "background-color: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 6px; padding: 4px 10px;"
        )
        c_layout = QHBoxLayout(container)
        c_layout.setContentsMargins(6, 4, 6, 4)
        c_layout.setSpacing(10)

        self.btn_reset = QPushButton("↺ Reset")
        self.btn_reset.setProperty("class", "secondaryBtn")
        self.btn_reset.clicked.connect(self.reset_playback)

        self.btn_prev = QPushButton("◀ Step Back")
        self.btn_prev.setProperty("class", "secondaryBtn")
        self.btn_prev.clicked.connect(self.step_backward)

        self.btn_play = QPushButton("▶ Play")
        self.btn_play.setProperty("class", "tealBtn")
        self.btn_play.clicked.connect(self.toggle_play)

        self.btn_next = QPushButton("Step Forward ▶")
        self.btn_next.setProperty("class", "secondaryBtn")
        self.btn_next.clicked.connect(self.step_forward)

        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet("font-weight: 600; color: #0B1F3A; min-width: 130px;")

        lbl_speed = QLabel("Speed:")
        lbl_speed.setStyleSheet("color: #64748B; font-weight: 500;")

        self.speed_slider = QSlider()
        self.speed_slider.setOrientation(Qt.Orientation.Horizontal)

        self.speed_slider.setRange(200, 1500)
        self.speed_slider.setValue(800)
        self.speed_slider.setInvertedAppearance(True)  # Faster to the right
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        self.speed_slider.setFixedWidth(100)

        c_layout.addWidget(self.btn_reset)
        c_layout.addWidget(self.btn_prev)
        c_layout.addWidget(self.btn_play)
        c_layout.addWidget(self.btn_next)
        c_layout.addWidget(self.lbl_status)
        c_layout.addStretch()
        c_layout.addWidget(lbl_speed)
        c_layout.addWidget(self.speed_slider)

        layout.addWidget(container)
        self.setEnabled(False)

    def set_total_steps(self, total: int) -> None:
        """Configures controls for the given total number of timeline segments."""
        self.pause()
        self._total_steps = total
        self._current_step = total - 1  # Default: view entire completed timeline
        self.setEnabled(total > 0)
        self._update_ui_state()

    def step_forward(self) -> None:
        if self._current_step < self._total_steps - 1:
            self._current_step += 1
            self.step_changed.emit(self._current_step)
            self._update_ui_state()
        elif self._is_playing:
            self.pause()

    def step_backward(self) -> None:
        if self._current_step > 0:
            self._current_step -= 1
            self.step_changed.emit(self._current_step)
            self._update_ui_state()

    def reset_playback(self) -> None:
        self.pause()
        if self._total_steps > 0:
            self._current_step = 0
            self.step_changed.emit(self._current_step)
            self._update_ui_state()

    def toggle_play(self) -> None:
        if self._is_playing:
            self.pause()
        else:
            self.play()

    def play(self) -> None:
        if self._total_steps == 0:
            return
        if self._current_step >= self._total_steps - 1:
            self._current_step = -1
        self._is_playing = True
        self.btn_play.setText("⏸ Pause")
        self.btn_play.setStyleSheet("background-color: #D97706; color: white;")
        self._timer.start()

    def pause(self) -> None:
        self._is_playing = False
        self._timer.stop()
        self.btn_play.setText("▶ Play")
        self.btn_play.setStyleSheet("")

    def _on_timer_tick(self) -> None:
        if self._current_step < self._total_steps - 1:
            self.step_forward()
        else:
            self.pause()

    def _on_speed_changed(self, value: int) -> None:
        self._timer.setInterval(value)

    def _update_ui_state(self) -> None:
        if self._total_steps == 0:
            self.lbl_status.setText("No Simulation")
            return
        step_display = self._current_step + 1 if self._current_step >= 0 else 0
        self.lbl_status.setText(f"Step {step_display} / {self._total_steps}")
        self.btn_prev.setEnabled(self._current_step > 0)
        self.btn_next.setEnabled(self._current_step < self._total_steps - 1)
