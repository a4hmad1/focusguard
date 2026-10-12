"""Settings, Emergency Recovery, and Security Tab."""

import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QTextEdit, QScrollArea
)
from PySide6.QtCore import Qt
from focusguard.core.config import is_admin, get_hosts_path, get_hosts_backup_path, DEFAULT_BLOCK_PORT
from focusguard.core.database import Database
from focusguard.engine.hosts_manager import HostsManager
from focusguard.engine.website_blocker import WebsiteBlocker
from focusguard.engine.scheduler import Scheduler

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
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header
        title = QLabel("System Settings & Emergency Recovery")
        title.setProperty("class", "heading_large")
        subtitle = QLabel("Privilege checks, hosts backup recovery, DNS maintenance, and audit history.")
        subtitle.setProperty("class", "subtext")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Section 1: System Privileges & Security
        priv_card = self._create_card("System Privileges & Permissions")
        priv_layout = QVBoxLayout(priv_card)

        admin_status = "Granted (Root / Administrator)" if is_admin() else "Standard User (Limited hosts modification)"
        color = "#22c55e" if is_admin() else "#f59e0b"
        status_lbl = QLabel(f"Administrative Status: <strong style='color:{color};'>{admin_status}</strong>")
        priv_layout.addWidget(status_lbl)

        info_lbl = QLabel(
            "Note: Modifying /etc/hosts (Linux) or C:\\Windows\\System32\\drivers\\etc\\hosts (Windows) "
            "requires administrative privileges. Run FocusGuard as administrator or use the background service."
        )
        info_lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")
        info_lbl.setWordWrap(True)
        priv_layout.addWidget(info_lbl)

        layout.addWidget(priv_card)

        # Section 2: Emergency Recovery
        rec_card = self._create_card("Emergency Recovery Fail-Safe")
        rec_layout = QVBoxLayout(rec_card)

        rec_desc = QLabel(
            "Accidentally locked yourself out of an essential resource? "
            "Emergency Recovery instantly terminates all active sessions, lifts application locks, "
            "and restores your clean hosts file."
        )
        rec_desc.setStyleSheet("color: #94a3b8; font-size: 13px;")
        rec_desc.setWordWrap(True)
        rec_layout.addWidget(rec_desc)

        rec_btn_row = QHBoxLayout()
        emergency_btn = QPushButton("Trigger Emergency Unblock")
        emergency_btn.setProperty("class", "danger")
        emergency_btn.clicked.connect(self._on_emergency_unblock)
        rec_btn_row.addWidget(emergency_btn)

        restore_bak_btn = QPushButton("Restore Hosts from Backup")
        restore_bak_btn.setProperty("class", "secondary")
        restore_bak_btn.clicked.connect(self._on_restore_hosts_backup)
        rec_btn_row.addWidget(restore_bak_btn)

        flush_dns_btn = QPushButton("Flush OS DNS Cache")
        flush_dns_btn.setProperty("class", "secondary")
        flush_dns_btn.clicked.connect(self._on_flush_dns)
        rec_btn_row.addWidget(flush_dns_btn)

        rec_btn_row.addStretch()
        rec_layout.addLayout(rec_btn_row)

        layout.addWidget(rec_card)

        # Section 3: Local Block Page Server
        server_card = self._create_card("Local Block Page Web Server")
        srv_layout = QVBoxLayout(server_card)

        srv_info = QLabel(f"Local block page running at <strong>http://127.0.0.1:{DEFAULT_BLOCK_PORT}</strong>")
        srv_layout.addWidget(srv_info)

        preview_btn = QPushButton("Preview 'Access Blocked' Page in Browser")
        preview_btn.setProperty("class", "secondary")
        preview_btn.clicked.connect(lambda: webbrowser.open(f"http://127.0.0.1:{DEFAULT_BLOCK_PORT}"))
        srv_layout.addWidget(preview_btn, alignment=Qt.AlignLeft)

        layout.addWidget(server_card)

        # Section 4: Technical Limitations & Bypass Guidance
        lim_card = self._create_card("Security Model & Technical Limitations")
        lim_layout = QVBoxLayout(lim_card)

        lim_text = QLabel(
            "<strong>1. DNS-over-HTTPS (DoH):</strong> Modern browsers (Chrome, Firefox) may bypass system DNS "
            "using encrypted DNS. FocusGuard redirects known DoH endpoints, but users should disable 'Secure DNS' "
            "in browser settings for 100% strict enforcement.<br><br>"
            "<strong>2. VPNs & Proxies:</strong> Third-party VPN tunnels bypass OS-level hosts filtering. Application "
            "blocking can be used to restrict unauthorized VPN clients.<br><br>"
            "<strong>3. Core OS Safety:</strong> Essential operating system processes (init, systemd, explorer.exe, dwm.exe) "
            "are strictly protected and will never be terminated."
        )
        lim_text.setStyleSheet("color: #cbd5e1; font-size: 12px; line-height: 1.5;")
        lim_text.setWordWrap(True)
        lim_layout.addWidget(lim_text)

        layout.addWidget(lim_card)

        # Section 5: Audit Logs
        logs_card = self._create_card("Recent Enforcement Audit Logs")
        logs_layout = QVBoxLayout(logs_card)

        self.logs_table = QTableWidget(0, 4)
        self.logs_table.setHorizontalHeaderLabels(["Timestamp", "Event", "Target", "Details"])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.logs_table.setFixedHeight(160)
        self.logs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        logs_layout.addWidget(self.logs_table)

        layout.addWidget(logs_card)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        self.load_logs()

    def _create_card(self, title_text: str) -> QFrame:
        card = QFrame()
        card.setObjectName("settings_card")
        card.setStyleSheet("""
            QFrame#settings_card {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        t = QLabel(title_text)
        t.setProperty("class", "heading_medium")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.addWidget(t)
        return card

    def _on_emergency_unblock(self):
        confirm = QMessageBox.question(
            self,
            "Confirm Emergency Unblock",
            "Are you sure you want to lift all restrictions and restore clean access?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.scheduler.cancel_active_sessions()
            try:
                self.blocker.unblock_all()
                QMessageBox.information(self, "Unblocked", "All restrictions have been lifted successfully.")
            except PermissionError as e:
                QMessageBox.warning(self, "Permission Required", str(e))
            self.load_logs()

    def _on_restore_hosts_backup(self):
        try:
            success = self.hosts_mgr.restore_from_backup()
            if success:
                QMessageBox.information(self, "Restored", "Original hosts file restored from backup.")
            else:
                QMessageBox.warning(self, "No Backup", "No safety backup file was found.")
        except PermissionError as e:
            QMessageBox.warning(self, "Permission Required", str(e))

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
