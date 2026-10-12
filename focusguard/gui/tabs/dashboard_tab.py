"""Dashboard Overview Tab for FocusGuard GUI."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from datetime import timedelta
from focusguard.core.database import Database
from focusguard.engine.scheduler import Scheduler
from focusguard.engine.app_detector import AppDetector
from focusguard.gui.widgets.stat_card import StatCard
from focusguard.gui.widgets.timer_widget import TimerWidget

class DashboardTab(QWidget):
    def __init__(self, db: Database, scheduler: Scheduler):
        super().__init__()
        self.db = db
        self.scheduler = scheduler
        self.detector = AppDetector()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header Title
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        
        self.title_label = QLabel("Focus Dashboard")
        self.title_label.setProperty("class", "heading_large")
        self.subtitle_label = QLabel("Eliminate distractions and maintain deep concentration.")
        self.subtitle_label.setProperty("class", "subtext")
        
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.subtitle_label)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Stat Cards Row
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(16)

        self.card_sites = StatCard("Blocked Websites", "0", "Configured rules", "#ef4444")
        self.card_apps = StatCard("Blocked Apps", "0", "Applications restricted", "#f59e0b")
        self.card_running = StatCard("Running Processes", "0", "Active on system", "#10b981")
        self.card_mode = StatCard("Filter Mode", "BLACKLIST", "Current enforcement", "#3b82f6")

        self.stats_row.addWidget(self.card_sites)
        self.stats_row.addWidget(self.card_apps)
        self.stats_row.addWidget(self.card_running)
        self.stats_row.addWidget(self.card_mode)
        layout.addLayout(self.stats_row)

        # Center Hero Timer Widget
        self.timer_widget = TimerWidget()
        self.timer_widget.session_start_requested.connect(self._on_start_session)
        self.timer_widget.session_stop_requested.connect(self._on_stop_session)
        layout.addWidget(self.timer_widget)

        # Active Sessions Summary Table
        sessions_frame = QFrame()
        sessions_frame.setObjectName("sessions_frame")
        sessions_frame.setStyleSheet("""
            QFrame#sessions_frame {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        sessions_layout = QVBoxLayout(sessions_frame)
        sessions_layout.setContentsMargins(12, 12, 12, 12)

        sec_title = QLabel("Active Focus Restrictions")
        sec_title.setProperty("class", "heading_medium")
        sessions_layout.addWidget(sec_title)

        self.sessions_table = QTableWidget(0, 4)
        self.sessions_table.setHorizontalHeaderLabels(["Target", "Type", "Expires At", "Reason"])
        self.sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sessions_table.setFixedHeight(120)
        self.sessions_table.setEditTriggers(QTableWidget.NoEditTriggers)
        sessions_layout.addWidget(self.sessions_table)

        layout.addWidget(sessions_frame)
        layout.addStretch()

        self.refresh_stats()

    def _on_start_session(self, duration: timedelta, reason: str):
        self.scheduler.start_timed_session(duration=duration, reason=reason)
        self.refresh_stats()

    def _on_stop_session(self):
        self.scheduler.cancel_active_sessions()
        self.refresh_stats()

    def refresh_stats(self):
        """Update counts, active session rows, and timer status."""
        status = self.scheduler.get_current_status()

        # Update Timer widget
        self.timer_widget.update_countdown(
            remaining_seconds=status["remaining_seconds"],
            is_active=status["is_blocking_active"]
        )

        # Update Stat Cards
        sites_count = len(self.db.get_website_rules(rule_type="blacklist", only_active=True))
        apps_count = len(self.db.get_app_rules(only_blocked=True))
        running_count = len(self.detector.get_running_processes())
        mode_str = status["mode"].upper()

        self.card_sites.set_value(str(sites_count))
        self.card_apps.set_value(str(apps_count))
        self.card_running.set_value(str(running_count))
        self.card_mode.set_value(mode_str)

        # Populate Active Sessions
        active_sessions = status["active_sessions"]
        self.sessions_table.setRowCount(len(active_sessions))
        for row, s in enumerate(active_sessions):
            self.sessions_table.setItem(row, 0, QTableWidgetItem(str(s.get("target", "All"))))
            self.sessions_table.setItem(row, 1, QTableWidgetItem(str(s.get("session_type", "Focus Mode"))))
            self.sessions_table.setItem(row, 2, QTableWidgetItem(str(s.get("end_time", ""))))
            self.sessions_table.setItem(row, 3, QTableWidgetItem(str(s.get("reason", ""))))
