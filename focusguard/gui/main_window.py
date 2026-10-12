"""Main Application Window for FocusGuard GUI."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget, QLabel,
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QSize
from focusguard.core.config import APP_NAME, APP_VERSION
from focusguard.core.database import Database
from focusguard.engine.app_blocker import AppBlocker
from focusguard.engine.website_blocker import WebsiteBlocker
from focusguard.engine.scheduler import Scheduler
from focusguard.gui.theme import DARK_THEME_QSS
from focusguard.gui.tabs import (
    DashboardTab, WebsitesTab, AppsTab,
    SchedulesTab, SettingsTab
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} - Focus & Distraction Shield v{APP_VERSION}")
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(DARK_THEME_QSS)

        # Initialize Core Services
        self.db = Database()
        self.app_blocker = AppBlocker(self.db)
        self.website_blocker = WebsiteBlocker(self.db)
        self.scheduler = Scheduler(self.db, self.app_blocker, self.website_blocker)
        self.scheduler.start_background_loop()

        # Central Widget & Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left Sidebar Navigation
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        # Right Content Area
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header Bar
        header = self._create_header_bar()
        content_layout.addWidget(header)

        # Stacked Pages
        self.stacked_pages = QStackedWidget()
        self.dashboard_tab = DashboardTab(self.db, self.scheduler)
        self.websites_tab = WebsitesTab(self.db, self.website_blocker)
        self.apps_tab = AppsTab(self.db, self.scheduler)
        self.schedules_tab = SchedulesTab(self.db)
        self.settings_tab = SettingsTab(self.db, self.website_blocker, self.scheduler)

        self.stacked_pages.addWidget(self.dashboard_tab)
        self.stacked_pages.addWidget(self.websites_tab)
        self.stacked_pages.addWidget(self.apps_tab)
        self.stacked_pages.addWidget(self.schedules_tab)
        self.stacked_pages.addWidget(self.settings_tab)

        content_layout.addWidget(self.stacked_pages)
        main_layout.addWidget(content_container, stretch=1)

        # Real-time Update Timer (1 Hz)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(1000)

        self.nav_list.setCurrentRow(0)

    def _create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(12)

        # Brand / Logo Header
        brand_box = QHBoxLayout()
        logo_icon = QLabel("🛡️")
        logo_icon.setStyleSheet("font-size: 26px;")
        
        brand_text_box = QVBoxLayout()
        brand_text_box.setSpacing(0)
        brand_title = QLabel(APP_NAME)
        brand_title.setStyleSheet("font-size: 18px; font-weight: 800; color: #f8fafc; letter-spacing: -0.5px;")
        brand_sub = QLabel("Study Guard Desktop")
        brand_sub.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 500;")
        brand_text_box.addWidget(brand_title)
        brand_text_box.addWidget(brand_sub)

        brand_box.addWidget(logo_icon)
        brand_box.addLayout(brand_text_box)
        layout.addLayout(brand_box)
        layout.addSpacing(16)

        # Nav Items List
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("nav_list")
        
        items = [
            ("⚡  Dashboard", 0),
            ("🌐  Websites", 1),
            ("💻  Applications", 2),
            ("📅  Schedules", 3),
            ("⚙️  Settings", 4),
        ]
        for text, idx in items:
            it = QListWidgetItem(text)
            self.nav_list.addItem(it)

        self.nav_list.currentRowChanged.connect(self._on_nav_change)
        layout.addWidget(self.nav_list)
        layout.addStretch()

        # Version Pill
        ver_lbl = QLabel(f"FocusGuard v{APP_VERSION}")
        ver_lbl.setStyleSheet("color: #475569; font-size: 11px; text-align: center;")
        ver_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(ver_lbl)

        return sidebar

    def _create_header_bar(self) -> QFrame:
        header = QFrame()
        header.setObjectName("header_bar")
        header.setFixedHeight(60)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)

        self.page_title_lbl = QLabel("Dashboard Overview")
        self.page_title_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #f8fafc;")
        layout.addWidget(self.page_title_lbl)
        layout.addStretch()

        # Status Pill
        self.status_pill = QLabel("● IDLE")
        self.status_pill.setStyleSheet("""
            background-color: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 9999px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: 700;
        """)
        layout.addWidget(self.status_pill)

        # Emergency Unlock Header Button
        em_btn = QPushButton("Emergency Unlock")
        em_btn.setProperty("class", "danger")
        em_btn.setFixedHeight(32)
        em_btn.clicked.connect(self._quick_emergency_unlock)
        layout.addWidget(em_btn)

        return header

    def _on_nav_change(self, row: int):
        self.stacked_pages.setCurrentIndex(row)
        titles = ["Dashboard Overview", "Website Rules & Whitelist", "Application Restrictions", "Study Schedules", "Settings & Recovery"]
        if 0 <= row < len(titles):
            self.page_title_lbl.setText(titles[row])

    def _on_tick(self):
        # Refresh dashboard live stats
        self.dashboard_tab.refresh_stats()

        # Update Header status pill
        status = self.scheduler.get_current_status()
        if status["is_blocking_active"]:
            self.status_pill.setText("● FOCUS ACTIVE")
            self.status_pill.setStyleSheet("""
                background-color: rgba(34, 197, 94, 0.15);
                color: #4ade80;
                border: 1px solid rgba(34, 197, 94, 0.3);
                border-radius: 9999px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: 700;
            """)
        else:
            self.status_pill.setText("○ IDLE")
            self.status_pill.setStyleSheet("""
                background-color: rgba(148, 163, 184, 0.12);
                color: #94a3b8;
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 9999px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: 700;
            """)

    def _quick_emergency_unlock(self):
        confirm = QMessageBox.question(
            self,
            "Confirm Emergency Unlock",
            "Immediately cancel all active blocking sessions and lift restrictions?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.scheduler.cancel_active_sessions()
            try:
                self.website_blocker.unblock_all()
                QMessageBox.information(self, "Restrictions Lifted", "All restrictions have been lifted.")
            except PermissionError as e:
                QMessageBox.warning(self, "Permission Required", str(e))
            self._on_tick()

    def closeEvent(self, event):
        self.scheduler.stop_background_loop()
        super().closeEvent(event)
