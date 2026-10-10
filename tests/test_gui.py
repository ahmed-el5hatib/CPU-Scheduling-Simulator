"""GUI and Gantt integration test suite.

Author signature: Eng Ahmed El-khatib

Verifies:
  - Gate G3: GUI launches (offscreen) and navigation works.
  - Gate G4: Gantt matches engine timeline exactly for Example 1 and Example 2.
  - Gate G5: Signature 'Eng Ahmed El-khatib' present in About dialog, footer, and version.py.
  - Captures offscreen screenshots for visual proof.
"""

import os
from pathlib import Path

import pytest

# Ensure offscreen Qt platform for testing and headless rendering
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QLabel

from app.about_dialog import AboutDialog
from app.main_window import MainWindow
from resources.version import __author__
from scheduling.algorithms.fcfs import schedule_fcfs
from styles.theme import init_application_fonts


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    init_application_fonts()
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    return app


def test_gate_g5_signature_presence(qapp: QApplication) -> None:
    """Gate G5: Signature 'Eng Ahmed El-khatib' present in version.py, AboutDialog, and Footer."""
    assert __author__ == "Eng Ahmed El-khatib"

    window = MainWindow()
    # Check footer label text
    footer_label = window.findChild(QLabel, "footerLabel")
    assert footer_label is not None
    assert "Eng Ahmed El-khatib" in footer_label.text()
    assert footer_label.text() == "Operating Systems | CPU Scheduling Simulator | Eng Ahmed El-khatib"

    # Check About dialog
    dialog = AboutDialog(window)
    dialog_text = dialog.findChildren(QLabel)
    author_found = any("Eng Ahmed El-khatib" in lbl.text() for lbl in dialog_text)
    assert author_found, "Author signature missing from About dialog."


def test_gate_g3_gui_launches_and_nav_works(qapp: QApplication) -> None:
    """Gate G3: GUI launches without errors and navigation switches all views."""
    window = MainWindow()
    assert window is not None
    assert window.stacked.count() == 5

    # Switch across all pages
    for page_idx in range(5):
        window.nav.set_current_index(page_idx)
        assert window.stacked.currentIndex() == page_idx


def test_gate_g4_gantt_matches_engine_timeline_exactly(qapp: QApplication) -> None:
    """Gate G4: Gantt matches engine timeline exactly for the example dataset (verified by test)."""
    window = MainWindow()

    # 1. Test on Example 1: FCFS
    window.view_pm.load_example_1()
    procs = window.view_pm.get_processes()
    expected_result = schedule_fcfs(procs)

    # Set Simulator to FCFS and run
    window.view_sim.set_processes(procs)
    for i in range(window.view_sim.combo_algo.count()):
        if window.view_sim.combo_algo.itemData(i) == "fcfs":
            window.view_sim.combo_algo.setCurrentIndex(i)
            break
    window.view_sim.run_current_simulation()

    gantt_rects = window.view_sim.gantt_chart._rect_data
    assert len(gantt_rects) == len(expected_result.timeline)

    for (rect, pid, start, end), seg in zip(gantt_rects, expected_result.timeline):
        expected_pid = seg.pid if seg.pid is not None else "IDLE"
        assert pid == expected_pid, f"PID mismatch: got {pid}, expected {expected_pid}"
        assert start == seg.start, f"Start mismatch: got {start}, expected {seg.start}"
        assert end == seg.end, f"End mismatch: got {end}, expected {seg.end}"
        assert (end - start) == seg.duration

    # 2. Test on Example 2: Forces IDLE time and Preemption
    window.view_pm.load_example_2()
    procs2 = window.view_pm.get_processes()
    expected_res2 = schedule_fcfs(procs2)

    window.view_sim.set_processes(procs2)
    window.view_sim.run_current_simulation()

    gantt_rects2 = window.view_sim.gantt_chart._rect_data
    assert len(gantt_rects2) == len(expected_res2.timeline)

    for (rect, pid, start, end), seg in zip(gantt_rects2, expected_res2.timeline):
        expected_pid = seg.pid if seg.pid is not None else "IDLE"
        assert pid == expected_pid
        assert start == seg.start
        assert end == seg.end


def test_capture_offscreen_screenshots(qapp: QApplication) -> None:
    """Renders offscreen window and exports screenshots to screenshots/ directory."""
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)

    window = MainWindow()
    window.resize(1200, 800)
    window.show()

    # Simulator View Screenshot
    window.nav.set_current_index(2)
    window.view_sim.run_current_simulation()
    qapp.processEvents()

    pixmap_sim = window.grab()
    sim_path = str(screenshots_dir / "simulator_view.png")
    pixmap_sim.save(sim_path)
    assert Path(sim_path).exists()
    assert Path(sim_path).stat().st_size > 1000

    # Comparison View Screenshot
    window.nav.set_current_index(3)
    window.view_comp.run_comparison()
    qapp.processEvents()

    pixmap_comp = window.grab()
    comp_path = str(screenshots_dir / "comparison_view.png")
    pixmap_comp.save(comp_path)
    assert Path(comp_path).exists()
    assert Path(comp_path).stat().st_size > 1000

    # Process Manager View Screenshot
    window.nav.set_current_index(1)
    qapp.processEvents()
    pixmap_pm = window.grab()
    pm_path = str(screenshots_dir / "process_manager_view.png")
    pixmap_pm.save(pm_path)
    assert Path(pm_path).exists()
    assert Path(pm_path).stat().st_size > 1000

    # Dashboard View Screenshot
    window.nav.set_current_index(0)
    qapp.processEvents()
    pixmap_dash = window.grab()
    dash_path = str(screenshots_dir / "dashboard_view.png")
    pixmap_dash.save(dash_path)
    assert Path(dash_path).exists()

    # Guide View Screenshot
    window.nav.set_current_index(4)
    qapp.processEvents()
    pixmap_guide = window.grab()
    guide_path = str(screenshots_dir / "guide_view.png")
    pixmap_guide.save(guide_path)
    assert Path(guide_path).exists()


def test_simulator_view_animation_stepping(qapp: QApplication) -> None:
    """Verifies that the Live Execution Panel advances ticks, updates CPU/Queue, and syncs Gantt cursor."""
    window = MainWindow()
    window.resize(1260, 840)
    window.show()

    # Load benchmark 1 in simulator view
    window.nav.set_current_index(2)
    window.view_sim._load_benchmark_1()
    qapp.processEvents()

    assert len(window.view_sim._processes) == 4
    assert window.view_sim._current_result is not None
    assert window.view_sim.live_panel.isEnabled()

    # Initial tick t=0
    assert window.view_sim.live_panel._current_tick == 0
    assert "t = 0" in window.view_sim.live_panel.lbl_clock_val.text()

    # Step forward to t=1
    window.view_sim.live_panel.step_forward()
    assert window.view_sim.live_panel._current_tick == 1
    assert "t = 1" in window.view_sim.live_panel.lbl_clock_val.text()
    assert window.view_sim.live_panel.progress_bar.value() > 0

    # Step backward to t=0
    window.view_sim.live_panel.step_backward()
    assert window.view_sim.live_panel._current_tick == 0
    assert "t = 0" in window.view_sim.live_panel.lbl_clock_val.text()

    # Jump to end
    window.view_sim.live_panel.jump_to_finish()
    stepper = window.view_sim.live_panel._stepper
    assert stepper is not None
    max_tick = stepper.total_ticks - 1
    assert window.view_sim.live_panel._current_tick == max_tick

    # Reset
    window.view_sim.live_panel.reset_to_start()
    assert window.view_sim.live_panel._current_tick == 0


def test_dashboard_presets_and_comparison_sync(qapp: QApplication) -> None:
    """Verifies that loading presets on Dashboard synchronizes across all views and updates champions."""
    window = MainWindow()
    window.show()

    # Click Dashboard preset 1
    window.view_dashboard._load_b1()
    qapp.processEvents()

    assert len(window.view_pm.get_processes()) == 4
    assert len(window.view_sim._processes) == 4
    assert len(window.view_comp._processes) == 4

    # Navigate to Comparison view
    window.nav.set_current_index(3)
    qapp.processEvents()

    assert len(window.view_comp._results) == 6
    assert window.view_comp.table.rowCount() == 6
    assert "Best WT:" in window.view_comp.lbl_best_wt.text()
    assert "—" not in window.view_comp.lbl_best_wt.text()


