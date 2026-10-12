"""Tests for AppDetector and system inspection."""

from focusguard.engine.app_detector import AppDetector, InstalledApp

def test_app_detector_installed_apps():
    detector = AppDetector()
    apps = detector.get_installed_applications()
    assert isinstance(apps, list)
    assert len(apps) > 0

    # Ensure each item is an InstalledApp
    for app in apps[:5]:
        assert isinstance(app, InstalledApp)
        assert app.name
        assert app.exec_name
        d = app.to_dict()
        assert "is_critical" in d

def test_app_detector_running_processes():
    detector = AppDetector()
    procs = detector.get_running_processes()
    assert isinstance(procs, list)
    assert len(procs) > 0

    first = procs[0]
    assert "pid" in first
    assert "clean_name" in first
    assert "is_critical" in first
