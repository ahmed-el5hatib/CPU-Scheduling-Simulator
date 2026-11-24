"""Regression tests for comparison failures, cached results and exports."""

import logging
import os
from unittest.mock import Mock

os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
from PySide6.QtWidgets import QApplication

from app.views import comparison
from scheduling.engine import ALGORITHMS
from scheduling.models import Process


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def view(qapp):
    widget = comparison.ComparisonView()
    yield widget
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


def load_workload(view):
    view.set_processes([Process(pid="P1", arrival_time=0, burst_time=3)])


def test_exports_disabled_before_first_benchmark(view):
    assert not view.btn_export_csv.isEnabled()
    assert not view.btn_export_chart.isEnabled()


@pytest.mark.parametrize("clear_via_setter", [True, False])
def test_empty_workload_discards_cached_results(view, monkeypatch, clear_via_setter):
    load_workload(view)
    assert len(view._results) == len(ALGORITHMS)
    assert view.btn_export_csv.isEnabled()
    if clear_via_setter:
        view.set_processes([])
    else:
        view._processes = []
        view.run_comparison()
    assert view._results == []
    assert view.table.rowCount() == 0
    assert "—" in view.lbl_best_wt.text()
    assert not view.btn_export_csv.isEnabled()
    assert not view.btn_export_chart.isEnabled()
    dialog = Mock()
    monkeypatch.setattr(comparison.QFileDialog, "getSaveFileName", dialog)
    view._on_export_csv()
    view._on_export_chart()
    dialog.assert_not_called()


def test_partial_failure_is_visible_and_logged(view, monkeypatch, caplog):
    original = comparison.run_simulation

    def fail_fcfs(key, processes, **config):
        if key == "fcfs":
            raise RuntimeError("test scheduler failure")
        return original(key, processes, **config)

    monkeypatch.setattr(comparison, "run_simulation", fail_fcfs)
    with caplog.at_level(logging.ERROR):
        load_workload(view)
    assert len(view._results) == len(ALGORITHMS) - 1
    assert view.table.rowCount() == len(ALGORITHMS) - 1
    assert not view.lbl_status.isHidden()
    assert "Partial benchmark" in view.lbl_status.text()
    assert ALGORITHMS["fcfs"]["name"] in view.lbl_status.text()
    assert "successful algorithms only" in view.lbl_status.text()
    assert any(record.exc_info for record in caplog.records)
    assert "fcfs" in caplog.text
    assert view.btn_export_csv.isEnabled()
    assert view.btn_export_chart.isEnabled()

    # A successful retry must clear the old warning.
    monkeypatch.setattr(comparison, "run_simulation", original)
    view.run_comparison()
    assert len(view._results) == len(ALGORITHMS)
    assert view.lbl_status.isHidden()
    assert view.lbl_status.text() == ""


def test_total_failure_cannot_export_old_results(view, monkeypatch):
    load_workload(view)
    monkeypatch.setattr(comparison, "run_simulation", Mock(side_effect=RuntimeError("failed")))
    view.run_comparison()
    assert view._results == []
    assert view.table.rowCount() == 0
    assert "Benchmark failed: 0/6" in view.lbl_status.text()
    assert not view.lbl_status.isHidden()
    assert not view.btn_export_csv.isEnabled()
    assert not view.btn_export_chart.isEnabled()
    view.set_processes([])
    assert view.lbl_status.isHidden()


@pytest.mark.parametrize("kind", ["csv", "chart"])
def test_export_failure_warns_user_and_logs(view, monkeypatch, caplog, tmp_path, kind):
    load_workload(view)
    monkeypatch.setattr(comparison.QFileDialog, "getSaveFileName", Mock(return_value=(str(tmp_path / kind), "")))
    warning = Mock()
    monkeypatch.setattr(comparison.QMessageBox, "warning", warning)
    failure = Mock(side_effect=PermissionError("read-only destination"))
    if kind == "csv":
        monkeypatch.setattr(comparison, "export_comparison_to_csv", failure)
    else:
        monkeypatch.setattr(view.chart_widget, "export_image", failure)
    with caplog.at_level(logging.ERROR):
        getattr(view, f"_on_export_{kind}")()
    warning.assert_called_once()
    assert "Export failed" in warning.call_args.args
    assert any(record.exc_info for record in caplog.records)
    assert len(view._results) == len(ALGORITHMS)


@pytest.mark.parametrize("kind", ["csv", "chart"])
def test_export_cancel_does_not_write(view, monkeypatch, kind):
    load_workload(view)
    monkeypatch.setattr(comparison.QFileDialog, "getSaveFileName", Mock(return_value=("", "")))
    writer = Mock()
    if kind == "csv":
        monkeypatch.setattr(comparison, "export_comparison_to_csv", writer)
    else:
        monkeypatch.setattr(view.chart_widget, "export_image", writer)
    getattr(view, f"_on_export_{kind}")()
    writer.assert_not_called()


@pytest.mark.parametrize("kind,extension", [("csv", "csv"), ("chart", "png")])
def test_successful_export_writes_file(view, monkeypatch, tmp_path, kind, extension):
    load_workload(view)
    target = tmp_path / f"benchmark.{extension}"
    monkeypatch.setattr(comparison.QFileDialog, "getSaveFileName", Mock(return_value=(str(target), "")))
    warning = Mock()
    monkeypatch.setattr(comparison.QMessageBox, "warning", warning)
    getattr(view, f"_on_export_{kind}")()
    assert target.stat().st_size > 0
    warning.assert_not_called()
    if kind == "csv":
        assert ALGORITHMS["fcfs"]["name"] in target.read_text()
