"""Formal Settings, Emergency Recovery, and Security Tab."""

import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QScrollArea, QComboBox
)
from PySide6.QtCore import Qt
from focusguard.core.config import is_admin, DEFAULT_BLOCK_PORT
from focusguard.core.database import Database
from focusguard.engine.hosts_manager import HostsManager
from focusguard.engine.website_blocker import WebsiteBlocker
from focusguard.engine.scheduler import Scheduler
from focusguard.gui.theme import get_theme_stylesheet

class SettingsTab(QWidget):
    def __init__(self, db: Database, blocker: WebsiteBlocker, scheduler: Scheduler):
        super().__init__()
        self.db = db
        self.blocker = blocker
        self.scheduler = scheduler
        self.hosts_mgr = HostsManager()

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        title = QLabel("System Settings & Emergency Recovery")
        title.setProperty("class", "heading_large")
        subtitle = QLabel("Desktop appearance, browser proxy status, privileges, and recovery options.")
        subtitle.setProperty("class", "subtext")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Section 1: Appearance (White / Black Theme)
        theme_card, t_layout = self._create_card("Desktop Appearance & Color Theme")
        t_row = QHBoxLayout()
        t_row.addWidget(QLabel("Interface Theme:"))

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Black / Dark Mode", "White / Light Mode"])
        saved_theme = self.db.get_setting("theme", default="black")
        if saved_theme in ("white", "light"):
            self.theme_combo.setCurrentIndex(1)
        else:
            self.theme_combo.setCurrentIndex(0)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        t_row.addWidget(self.theme_combo)
        t_row.addStretch()
        t_layout.addLayout(t_row)
        layout.addWidget(theme_card)

        # Section 2: How Website Blocking Works
        pac_card, pac_layout = self._create_card("🌐   How Website Blocking Works")
        
        p_info = QLabel(
            "FocusGuard automatically configures your web browsers (Chrome, Firefox, Edge, Brave) "
            "to permit <strong>ONLY your approved websites</strong> to open. "
            "If you try to open any unapproved website (such as YouTube, Reddit, or gaming sites), "
            "access will be blocked with a study shield landing page.<br><br>"
            "When your study timer finishes or you click <strong>Stop Focus</strong>, "
            "all websites and applications unlock automatically."
        )
        p_info.setStyleSheet("font-size: 13px; color: #64748b; line-height: 1.4;")
        p_info.setWordWrap(True)
        pac_layout.addWidget(p_info)

        preview_btn = QPushButton("Preview 'Access Blocked' Landing Page in Browser")
        preview_btn.setProperty("class", "secondary")
        preview_btn.clicked.connect(lambda: webbrowser.open(f"http://127.0.0.1:{DEFAULT_BLOCK_PORT}"))
        pac_layout.addWidget(preview_btn, alignment=Qt.AlignLeft)
        layout.addWidget(pac_card)

        # Section 3: Emergency Recovery
        rec_card, rec_layout = self._create_card("🚨   Emergency Unlock")

        rec_desc = QLabel(
            "Need to immediately stop all restrictions? "
            "Emergency Unlock instantly ends any active session, removes browser blocks, and restores unrestricted internet access."
        )
        rec_desc.setStyleSheet("font-size: 13px; color: #64748b;")
        rec_desc.setWordWrap(True)
        rec_layout.addWidget(rec_desc)

        rec_btn_row = QHBoxLayout()
        emergency_btn = QPushButton("🚨  Trigger Emergency Unlock")
        emergency_btn.setProperty("class", "danger")
        emergency_btn.setFixedHeight(34)
        emergency_btn.clicked.connect(self._on_emergency_unblock)
        rec_btn_row.addWidget(emergency_btn)

        flush_dns_btn = QPushButton("Flush OS DNS Cache")
        flush_dns_btn.setProperty("class", "secondary")
        flush_dns_btn.setFixedHeight(34)
        flush_dns_btn.clicked.connect(self._on_flush_dns)
        rec_btn_row.addWidget(flush_dns_btn)

        rec_btn_row.addStretch()
        rec_layout.addLayout(rec_btn_row)
        layout.addWidget(rec_card)

        # Section 4: Audit Logs
        logs_card, logs_layout = self._create_card("Enforcement History & Audit Logs")

        self.logs_table = QTableWidget(0, 4)
        self.logs_table.setHorizontalHeaderLabels(["Timestamp", "Event", "Target", "Details"])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.logs_table.verticalHeader().setVisible(False)
        self.logs_table.verticalHeader().setDefaultSectionSize(36)
        self.logs_table.setShowGrid(False)
        self.logs_table.setFixedHeight(140)
        self.logs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        logs_layout.addWidget(self.logs_table)
        layout.addWidget(logs_card)

        layout.addStretch()
        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        self.load_logs()

    def _create_card(self, title_text: str):
        card = QFrame()
        card.setObjectName("settings_card")
        card.setProperty("class", "card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(10)
        t = QLabel(title_text)
        t.setProperty("class", "heading_medium")
        card_layout.addWidget(t)
        return card, card_layout

    def _on_theme_changed(self, idx: int):
        theme_name = "white" if idx == 1 else "black"
        self.db.set_setting("theme", theme_name)
        # Find window ancestor and apply
        win = self.window()
        if win:
            win.setStyleSheet(get_theme_stylesheet(theme_name))
            if hasattr(win, "current_theme"):
                win.current_theme = theme_name
                win._update_theme_button_text()

    def _on_emergency_unblock(self):
        confirm = QMessageBox.question(
            self,
            "Confirm Emergency Unblock",
            "Are you sure you want to lift all restrictions and restore completely open browser access?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.scheduler.cancel_active_sessions()
            try:
                self.blocker.unblock_all()
                QMessageBox.information(self, "Unblocked", "All restrictions lifted. Normal web access restored.")
            except Exception as e:
                QMessageBox.warning(self, "Notice", str(e))
            self.load_logs()

    def _on_flush_dns(self):
        self.hosts_mgr.flush_dns_cache()
        QMessageBox.information(self, "DNS Flushed", "Operating system DNS cache flush command dispatched.")

    def load_logs(self):
        logs = self.db.get_recent_logs(limit=25)
        self.logs_table.setRowCount(len(logs))
        for row, item in enumerate(logs):
            self.logs_table.setItem(row, 0, QTableWidgetItem(str(item.get("timestamp", ""))[:19]))
            self.logs_table.setItem(row, 1, QTableWidgetItem(str(item.get("event_type", ""))))
            self.logs_table.setItem(row, 2, QTableWidgetItem(str(item.get("target", ""))))
            self.logs_table.setItem(row, 3, QTableWidgetItem(str(item.get("details", ""))))
