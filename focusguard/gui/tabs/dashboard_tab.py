from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton
)
from PySide6.QtCore import Qt, Signal
from datetime import timedelta
from focusguard.core.database import Database
from focusguard.engine.scheduler import Scheduler
from focusguard.engine.app_detector import AppDetector
from focusguard.gui.widgets.timer_widget import TimerWidget

class DashboardTab(QWidget):
    navigate_to_tab = Signal(int)  # 1 for Websites, 2 for Apps

    def __init__(self, db: Database, scheduler: Scheduler):
        super().__init__()
        self.db = db
        self.scheduler = scheduler
        self.detector = AppDetector()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(18)

        # Header Title
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        
        self.title_label = QLabel("Study & Homework Focus Shield")
        self.title_label.setProperty("class", "heading_large")
        self.subtitle_label = QLabel("Lock your browsers to approved websites only and block distracting applications.")
        self.subtitle_label.setProperty("class", "subtext")
        
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.subtitle_label)
        layout.addLayout(title_box)

        # Center Hero Timer Widget
        self.timer_widget = TimerWidget()
        self.timer_widget.session_start_requested.connect(self._on_start_session)
        self.timer_widget.session_stop_requested.connect(self._on_stop_session)
        layout.addWidget(self.timer_widget)

        # Quick Control & Status Cards Row
        cards_row = QHBoxLayout()
        cards_row.setSpacing(14)

        # Card 1: Allowed Websites Summary
        self.sites_card = QFrame()
        self.sites_card.setProperty("class", "card")
        sc_layout = QVBoxLayout(self.sites_card)
        sc_layout.setContentsMargins(16, 14, 16, 14)
        sc_layout.setSpacing(8)

        sc_title = QLabel("🌐   Allowed Websites")
        sc_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        self.sc_count_lbl = QLabel("0 Approved Sites")
        self.sc_count_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #16a34a;")
        sc_desc = QLabel("Only websites in your Allowed list can be opened in any web browser during focus.")
        sc_desc.setStyleSheet("font-size: 12px; color: #64748b;")
        sc_desc.setWordWrap(True)

        sc_btn = QPushButton("Manage Allowed Websites →")
        sc_btn.setProperty("class", "secondary")
        sc_btn.clicked.connect(lambda: self.navigate_to_tab.emit(1))

        sc_layout.addWidget(sc_title)
        sc_layout.addWidget(self.sc_count_lbl)
        sc_layout.addWidget(sc_desc)
        sc_layout.addStretch()
        sc_layout.addWidget(sc_btn)
        cards_row.addWidget(self.sites_card)

        # Card 2: Blocked Applications Summary
        self.apps_card = QFrame()
        self.apps_card.setProperty("class", "card")
        ac_layout = QVBoxLayout(self.apps_card)
        ac_layout.setContentsMargins(16, 14, 16, 14)
        ac_layout.setSpacing(8)

        ac_title = QLabel("💻   Distracting Apps")
        ac_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        self.ac_count_lbl = QLabel("0 Blocked Apps")
        self.ac_count_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #dc2626;")
        ac_desc = QLabel("Selected apps (games, Discord, etc.) will be automatically closed if opened while studying.")
        ac_desc.setStyleSheet("font-size: 12px; color: #64748b;")
        ac_desc.setWordWrap(True)

        ac_btn = QPushButton("Manage Blocked Apps →")
        ac_btn.setProperty("class", "secondary")
        ac_btn.clicked.connect(lambda: self.navigate_to_tab.emit(2))

        ac_layout.addWidget(ac_title)
        ac_layout.addWidget(self.ac_count_lbl)
        ac_layout.addWidget(ac_desc)
        ac_layout.addStretch()
        ac_layout.addWidget(ac_btn)
        cards_row.addWidget(self.apps_card)

        layout.addLayout(cards_row)

        # Friendly 3-Step Guide Card
        guide_card = QFrame()
        guide_card.setProperty("class", "card")
        g_layout = QVBoxLayout(guide_card)
        g_layout.setContentsMargins(16, 12, 16, 12)
        g_layout.setSpacing(6)

        g_title = QLabel("💡   How FocusGuard Works")
        g_title.setStyleSheet("font-size: 13px; font-weight: 700;")
        
        g_text = QLabel(
            "1. <strong>Add your websites:</strong> Go to 'Allowed Websites' and add sites you need for school or research.<br>"
            "2. <strong>Start your session:</strong> Choose a time duration above and click <strong>Start Focus Session</strong>.<br>"
            "3. <strong>Study without distractions:</strong> All browsers (Chrome, Firefox, Brave, Edge) will strictly block all other websites until your timer ends!"
        )
        g_text.setStyleSheet("font-size: 12px; color: #64748b; line-height: 1.4;")
        g_text.setWordWrap(True)

        g_layout.addWidget(g_title)
        g_layout.addWidget(g_text)
        layout.addWidget(guide_card)

        layout.addStretch()
        self.refresh_stats()

    def _on_start_session(self, duration: timedelta, reason: str):
        self.scheduler.start_timed_session(duration=duration, reason=reason)
        self.refresh_stats()

    def _on_stop_session(self):
        self.scheduler.cancel_active_sessions()
        self.refresh_stats()

    def refresh_stats(self):
        """Update counts and timer status."""
        status = self.scheduler.get_current_status()

        # Update Timer widget
        self.timer_widget.update_countdown(
            remaining_seconds=status["remaining_seconds"],
            is_active=status["is_blocking_active"]
        )

        # Update Counts
        whitelisted_count = len(self.db.get_website_rules(rule_type="whitelist", only_active=True))
        apps_count = len(self.db.get_app_rules(only_blocked=True))

        self.sc_count_lbl.setText(f"{whitelisted_count} Approved Study Websites")
        self.ac_count_lbl.setText(f"{apps_count} Restricted Applications")
