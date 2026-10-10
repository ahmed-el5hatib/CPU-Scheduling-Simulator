"""Live Execution Panel: Visualizes CPU state, Ready Queue, and Clock with animations.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from scheduling.models import Process, SimResult
from scheduling.simulation_stepper import SimulationStepper, StepState
from styles.theme import get_process_color


class LiveExecutionPanel(QWidget):
    """Interactive visualizer for CPU Core, Ready Queue, Clock, and Event Logs."""

    tick_changed = Signal(int)  # Emits current clock time t

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._stepper: SimulationStepper | None = None
        self._current_tick: int = 0
        self._is_playing: bool = False
        self._processes: list[Process] = []

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer_tick)
        self._timer.setInterval(600)  # 600ms per clock cycle

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 1. Top State Dashboard (Clock + CPU Core + Ready Queue)
        state_frame = QFrame()
        state_frame.setStyleSheet(
            "background-color: #0B1F3A; border-radius: 8px; padding: 12px; border: 1px solid #1E6FBA;"
        )
        s_layout = QHBoxLayout(state_frame)
        s_layout.setContentsMargins(10, 6, 10, 6)
        s_layout.setSpacing(16)

        # Clock Badge
        clock_box = QFrame()
        clock_box.setStyleSheet(
            "background-color: #132D52; border-radius: 6px; padding: 6px 14px; border: 1px solid #17A2A2;"
        )
        cb_layout = QVBoxLayout(clock_box)
        cb_layout.setContentsMargins(0, 0, 0, 0)
        cb_layout.setSpacing(2)
        lbl_clock_title = QLabel("CLOCK TIME")
        lbl_clock_title.setStyleSheet("color: #94A3B8; font-size: 8pt; font-weight: bold;")
        self.lbl_clock_val = QLabel("t = 0")
        self.lbl_clock_val.setStyleSheet("color: #17A2A2; font-size: 16pt; font-weight: 800;")
        cb_layout.addWidget(lbl_clock_title, alignment=Qt.AlignmentFlag.AlignCenter)
        cb_layout.addWidget(self.lbl_clock_val, alignment=Qt.AlignmentFlag.AlignCenter)
        s_layout.addWidget(clock_box)

        # CPU Core State Box
        self.cpu_box = QFrame()
        self.cpu_box.setStyleSheet(
            "background-color: #132D52; border-radius: 6px; padding: 6px 16px; border: 2px solid #3B82F6;"
        )
        cpu_layout = QVBoxLayout(self.cpu_box)
        cpu_layout.setContentsMargins(0, 0, 0, 0)
        cpu_layout.setSpacing(2)
        lbl_cpu_title = QLabel("⚡ CPU CORE")
        lbl_cpu_title.setStyleSheet("color: #94A3B8; font-size: 8pt; font-weight: bold;")
        self.lbl_cpu_val = QLabel("IDLE")
        self.lbl_cpu_val.setStyleSheet("color: #FFFFFF; font-size: 13pt; font-weight: bold;")
        cpu_layout.addWidget(lbl_cpu_title)
        cpu_layout.addWidget(self.lbl_cpu_val)
        s_layout.addWidget(self.cpu_box)

        # Ready Queue Container
        queue_box = QFrame()
        queue_box.setStyleSheet(
            "background-color: #132D52; border-radius: 6px; padding: 6px 14px; border: 1px solid #334155;"
        )
        q_layout = QVBoxLayout(queue_box)
        q_layout.setContentsMargins(0, 0, 0, 0)
        q_layout.setSpacing(4)
        lbl_queue_title = QLabel("READY QUEUE (WAITING)")
        lbl_queue_title.setStyleSheet("color: #94A3B8; font-size: 8pt; font-weight: bold;")

        self.queue_items_layout = QHBoxLayout()
        self.queue_items_layout.setSpacing(8)
        self.lbl_queue_empty = QLabel("(Empty)")
        self.lbl_queue_empty.setStyleSheet("color: #64748B; font-style: italic; font-size: 11pt;")
        self.queue_items_layout.addWidget(self.lbl_queue_empty)
        self.queue_items_layout.addStretch()

        q_layout.addWidget(lbl_queue_title)
        q_layout.addLayout(self.queue_items_layout)
        s_layout.addWidget(queue_box, 1)

        layout.addWidget(state_frame)

        # 1b. Simulation Timeline Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setStyleSheet(
            "QProgressBar { background-color: #0F172A; border: 1px solid #1E293B; border-radius: 4px; "
            "text-align: center; color: #FFFFFF; font-weight: bold; font-size: 8.5pt; } "
            "QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1E6FBA, stop:1 #17A2A2); border-radius: 3px; }"
        )
        layout.addWidget(self.progress_bar)

        # 2. Controls & Animation Toolbar
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 6px; padding: 6px 12px;"
        )
        c_layout = QHBoxLayout(ctrl_frame)
        c_layout.setContentsMargins(4, 2, 4, 2)
        c_layout.setSpacing(10)

        self.btn_reset = QPushButton("↺ Reset")
        self.btn_reset.setStyleSheet(
            "background-color: #F1F5F9; color: #0F172A; padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 4px; font-weight: 600;"
        )
        self.btn_reset.clicked.connect(self.reset_to_start)

        self.btn_step_back = QPushButton("◀ Step")
        self.btn_step_back.setStyleSheet(
            "background-color: #F1F5F9; color: #0F172A; padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 4px; font-weight: 600;"
        )
        self.btn_step_back.clicked.connect(self.step_backward)

        self.btn_play = QPushButton("▶ Animate")
        self.btn_play.setStyleSheet(
            "background-color: #17A2A2; color: white; padding: 6px 18px; border-radius: 4px; font-weight: bold; font-size: 10pt;"
        )
        self.btn_play.clicked.connect(self.toggle_play)

        self.btn_step_fwd = QPushButton("Step ▶")
        self.btn_step_fwd.setStyleSheet(
            "background-color: #F1F5F9; color: #0F172A; padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 4px; font-weight: 600;"
        )
        self.btn_step_fwd.clicked.connect(self.step_forward)

        self.btn_end = QPushButton("⏩ Jump to End")
        self.btn_end.setStyleSheet(
            "background-color: #F1F5F9; color: #0F172A; padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 4px;"
        )
        self.btn_end.clicked.connect(self.jump_to_finish)

        c_layout.addWidget(self.btn_reset)
        c_layout.addWidget(self.btn_step_back)
        c_layout.addWidget(self.btn_play)
        c_layout.addWidget(self.btn_step_fwd)
        c_layout.addWidget(self.btn_end)
        c_layout.addStretch()

        lbl_speed = QLabel("Speed:")
        lbl_speed.setStyleSheet("color: #64748B; font-weight: 600;")
        self.lbl_speed_val = QLabel("600 ms")
        self.lbl_speed_val.setStyleSheet("color: #0F172A; font-weight: bold; min-width: 50px;")

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(150, 1500)
        self.speed_slider.setValue(600)
        self.speed_slider.setInvertedAppearance(True)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        self.speed_slider.setFixedWidth(80)

        c_layout.addWidget(lbl_speed)
        c_layout.addWidget(self.speed_slider)
        c_layout.addWidget(self.lbl_speed_val)

        layout.addWidget(ctrl_frame)

        # 3. Live Event Log Box
        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setMaximumHeight(75)
        self.event_log.setStyleSheet(
            "background-color: #0F172A; color: #38BDF8; font-family: 'Consolas', 'Courier New', monospace; font-size: 9.5pt; border-radius: 6px; padding: 6px; border: 1px solid #1E293B;"
        )
        layout.addWidget(self.event_log)

        self.setEnabled(False)

    def load_simulation(self, processes: list[Process], sim_result: SimResult) -> None:
        """Initializes stepper from new simulation results."""
        self.pause()
        self._processes = list(processes)
        self._stepper = SimulationStepper(processes, sim_result)
        self._current_tick = 0
        self.setEnabled(self._stepper.total_ticks > 0)
        self.event_log.clear()
        self.event_log.append("<span style='color:#17A2A2; font-weight:bold;'>🚀 Simulation loaded. Press '▶ Animate' to watch step-by-step CPU execution!</span>")
        self._render_state(0)

    def set_tick(self, tick: int) -> None:
        """Sets clock tick directly and updates UI."""
        if not self._stepper:
            return
        self._current_tick = max(0, min(tick, self._stepper.total_ticks - 1))
        self._render_state(self._current_tick)
        self.tick_changed.emit(self._current_tick)

    def step_forward(self) -> None:
        if not self._stepper:
            return
        if self._current_tick < self._stepper.total_ticks - 1:
            self.set_tick(self._current_tick + 1)
        elif self._is_playing:
            self.pause()

    def step_backward(self) -> None:
        if not self._stepper:
            return
        if self._current_tick > 0:
            self.set_tick(self._current_tick - 1)

    def reset_to_start(self) -> None:
        self.pause()
        self.event_log.clear()
        self.event_log.append("<span style='color:#94A3B8;'>↺ Execution reset to t=0</span>")
        self.set_tick(0)

    def jump_to_finish(self) -> None:
        self.pause()
        if self._stepper:
            self.set_tick(self._stepper.total_ticks - 1)

    def toggle_play(self) -> None:
        if self._is_playing:
            self.pause()
        else:
            self.play()

    def play(self) -> None:
        if not self._stepper or self._stepper.total_ticks <= 1:
            return
        if self._current_tick >= self._stepper.total_ticks - 1:
            self.set_tick(0)
        self._is_playing = True
        self.btn_play.setText("⏸ Pause")
        self.btn_play.setStyleSheet("background-color: #D97706; color: white; padding: 6px 18px; border-radius: 4px; font-weight: bold;")
        self._timer.start()

    def pause(self) -> None:
        self._is_playing = False
        self._timer.stop()
        self.btn_play.setText("▶ Animate")
        self.btn_play.setStyleSheet("background-color: #17A2A2; color: white; padding: 6px 18px; border-radius: 4px; font-weight: bold;")

    def _on_timer_tick(self) -> None:
        if self._stepper and self._current_tick < self._stepper.total_ticks - 1:
            self.step_forward()
        else:
            self.pause()

    def _on_speed_changed(self, val: int) -> None:
        self._timer.setInterval(val)
        self.lbl_speed_val.setText(f"{val} ms")

    def _render_state(self, tick: int) -> None:
        if not self._stepper:
            return
        state: StepState = self._stepper.get_state(tick)

        # 0. Update Progress Bar
        total = max(1, self._stepper.total_ticks - 1)
        pct = int((tick / total) * 100)
        self.progress_bar.setValue(pct)
        self.progress_bar.setFormat(f"Simulation Progress: t = {state.time} / {total} cycles ({pct}%)")

        # 1. Update Clock
        self.lbl_clock_val.setText(f"t = {state.time}")

        # 2. Update CPU Core Box
        if state.running_pid is not None:
            rem = state.remaining_bursts.get(state.running_pid, 0)
            p_idx = next(
                (i for i, p in enumerate(self._processes) if p.pid == state.running_pid), 0
            )
            color = get_process_color(p_idx)
            self.lbl_cpu_val.setText(f"{state.running_pid}  [Rem: {rem}]")
            self.cpu_box.setStyleSheet(
                f"background-color: #132D52; border-radius: 6px; padding: 6px 16px; border: 3px solid {color};"
            )
        else:
            self.lbl_cpu_val.setText("IDLE 💤")
            self.cpu_box.setStyleSheet(
                "background-color: #132D52; border-radius: 6px; padding: 6px 16px; border: 2px dashed #94A3B8;"
            )

        # 3. Update Ready Queue Visualizer
        # Clear existing dynamic widgets in queue layout
        while self.queue_items_layout.count() > 0:
            item = self.queue_items_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not state.ready_queue:
            lbl = QLabel("(Empty)")
            lbl.setStyleSheet("color: #64748B; font-style: italic; font-size: 10pt;")
            self.queue_items_layout.addWidget(lbl)
        else:
            for idx, pid in enumerate(state.ready_queue):
                p_idx = next((i for i, p in enumerate(self._processes) if p.pid == pid), 0)
                color = get_process_color(p_idx)
                rem = state.remaining_bursts.get(pid, 0)
                badge = QLabel(f" {pid} (rem:{rem}) ")
                badge.setStyleSheet(
                    f"background-color: {color}; color: white; font-weight: bold; font-size: 9pt; border-radius: 4px; padding: 3px 6px;"
                )
                self.queue_items_layout.addWidget(badge)
                if idx < len(state.ready_queue) - 1:
                    arrow = QLabel("→")
                    arrow.setStyleSheet("color: #94A3B8; font-weight: bold; font-size: 11pt;")
                    self.queue_items_layout.addWidget(arrow)

        self.queue_items_layout.addStretch()

        # 4. Append to event log with rich color highlights
        msg = state.event_message
        if "idle" in msg.lower():
            badge_html = "<span style='color:#94A3B8;'>💤 [IDLE]</span>"
        elif "finish" in msg.lower() or "complet" in msg.lower():
            badge_html = "<span style='color:#4ADE80; font-weight:bold;'>🏁 [DONE]</span>"
        elif "preempt" in msg.lower() or "switch" in msg.lower():
            badge_html = "<span style='color:#FBBF24; font-weight:bold;'>🔄 [SWITCH]</span>"
        else:
            badge_html = "<span style='color:#38BDF8; font-weight:bold;'>⚡ [RUN]</span>"
        log_line = f"<span style='color:#64748B;'>[t={state.time}]</span> {badge_html} <span style='color:#F1F5F9;'>{msg}</span>"
        self.event_log.append(log_line)
        self.event_log.verticalScrollBar().setValue(self.event_log.verticalScrollBar().maximum())
