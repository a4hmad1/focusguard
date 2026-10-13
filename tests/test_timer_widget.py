"""Tests for the TimerWidget GUI countdown and preset selection."""

import os
import pytest
from datetime import timedelta

# Ensure Qt offscreen platform for headless test runs
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_timer_widget_defaults(qapp):
    from focusguard.gui.widgets.timer_widget import TimerWidget
    widget = TimerWidget()
    
    # Initial state must be 5m (300 seconds)
    assert widget.digits_label.text() == "05:00"
    assert widget.get_selected_duration() == timedelta(minutes=5)
    assert widget._is_active is False

def test_timer_widget_preset_switching(qapp):
    from focusguard.gui.widgets.timer_widget import TimerWidget
    widget = TimerWidget()

    # Switch to 15m
    widget._on_preset_clicked("15m")
    assert widget.digits_label.text() == "15:00"
    assert widget.get_selected_duration() == timedelta(minutes=15)

    # Switch back to 5m
    widget._on_preset_clicked("5m")
    assert widget.digits_label.text() == "05:00"
    assert widget.get_selected_duration() == timedelta(minutes=5)

def test_timer_widget_countdown_update(qapp):
    from focusguard.gui.widgets.timer_widget import TimerWidget
    widget = TimerWidget()
    widget.show()

    # Active countdown
    widget.update_countdown(280.0, is_active=True)
    assert widget.digits_label.text() == "04:40"
    assert widget.start_btn.isHidden() is True
    assert widget.stop_btn.isHidden() is False

    # When session ends, it must restore the selected preset duration (05:00), NOT 25:00
    widget.update_countdown(0.0, is_active=False)
    assert widget.digits_label.text() == "05:00"
    assert widget.start_btn.isHidden() is False
    assert widget.stop_btn.isHidden() is True

def test_timer_widget_custom_input(qapp):
    from focusguard.gui.widgets.timer_widget import TimerWidget
    widget = TimerWidget()

    # Type 10m
    widget.custom_input.setText("10m")
    assert widget.digits_label.text() == "10:00"
    assert widget.get_selected_duration() == timedelta(minutes=10)
