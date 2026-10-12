"""Main Application Window for FocusGuard GUI."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget, QLabel,
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from focusguard.core.config import APP_NAME, APP_VERSION
from focusguard.core.database import Database
from focusguard.engine.app_blocker import AppBlocker
from focusguard.engine.website_blocker import WebsiteBlocker
from focusguard.engine.scheduler import Scheduler
from focusguard.gui.theme import (
    FORMAL_DARK_THEME_QSS, FORMAL_LIGHT_THEME_QSS, get_theme_stylesheet
)
from focusguard.gui.tabs import (
    DashboardTab, WebsitesTab, AppsTab,
    SchedulesTab, SettingsTab
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} - Study Shield & Application Blocker v{APP_VERSION}")
        self.resize(1120, 740)
        self.setMinimumSize(940, 620)

        # Initialize Core Services
        self.db = Database()
        self.app_blocker = AppBlocker(self.db)
        self.website_blocker = WebsiteBlocker(self.db)
        self.scheduler = Scheduler(self.db, self.app_blocker, self.website_blocker)
        self.scheduler.start_background_loop()

        # Load Theme Preference (Default: black / dark)
        self.current_theme = self.db.get_setting("theme", default="black")
        self.setStyleSheet(get_theme_stylesheet(self.current_theme))

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
        sidebar.setFixedWidth(230)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 20, 14, 20)
        layout.setSpacing(10)

        # Brand Header
        brand_box = QHBoxLayout()
        logo_icon = QLabel("🛡️")
        logo_icon.setStyleSheet("font-size: 24px;")
        
        brand_text_box = QVBoxLayout()
        brand_text_box.setSpacing(0)
        brand_title = QLabel(APP_NAME)
        brand_title.setStyleSheet("font-size: 17px; font-weight: 800; letter-spacing: -0.4px;")
        brand_sub = QLabel("Study & Focus Shield")
        brand_sub.setStyleSheet("font-size: 11px; font-weight: 500; color: #64748b;")
        brand_text_box.addWidget(brand_title)
        brand_text_box.addWidget(brand_sub)

        brand_box.addWidget(logo_icon)
        brand_box.addLayout(brand_text_box)
        layout.addLayout(brand_box)
        layout.addSpacing(14)

        # Nav Items List
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("nav_list")
        
        items = [
            ("⚡  Dashboard", 0),
            ("🌐  Websites Whitelist", 1),
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

        # Policy & Version Pill
        ver_lbl = QLabel(f"{APP_NAME} Desktop v{APP_VERSION}")
        ver_lbl.setStyleSheet("color: #64748b; font-size: 11px;")
        ver_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(ver_lbl)

        return sidebar

    def _create_header_bar(self) -> QFrame:
        header = QFrame()
        header.setObjectName("header_bar")
        header.setFixedHeight(56)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(12)

        self.page_title_lbl = QLabel("Dashboard Overview")
        self.page_title_lbl.setStyleSheet("font-size: 15px; font-weight: 700;")
        layout.addWidget(self.page_title_lbl)
        layout.addStretch()

        # Theme Switcher Button (White / Black)
        self.theme_btn = QPushButton()
        self.theme_btn.setProperty("class", "secondary")
        self.theme_btn.setFixedHeight(30)
        self._update_theme_button_text()
        self.theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_btn)

        # Status Pill
        self.status_pill = QLabel("○ SHIELD IDLE")
        self.status_pill.setStyleSheet("""
            background-color: rgba(148, 163, 184, 0.12);
            color: #64748b;
            border: 1px solid rgba(148, 163, 184, 0.3);
            border-radius: 4px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 700;
        """)
        layout.addWidget(self.status_pill)

        # Emergency Unlock Header Button
        em_btn = QPushButton("Emergency Unlock")
        em_btn.setProperty("class", "danger")
        em_btn.setFixedHeight(30)
        em_btn.clicked.connect(self._quick_emergency_unlock)
        layout.addWidget(em_btn)

        return header

    def _update_theme_button_text(self):
        if self.current_theme in ("white", "light"):
            self.theme_btn.setText("🌙 Dark Mode")
        else:
            self.theme_btn.setText("☀️ Light Mode")

    def _toggle_theme(self):
        new_theme = "white" if self.current_theme in ("black", "dark") else "black"
        self.current_theme = new_theme
        self.db.set_setting("theme", new_theme)
        self.setStyleSheet(get_theme_stylesheet(new_theme))
        self._update_theme_button_text()

    def _on_nav_change(self, row: int):
        self.stacked_pages.setCurrentIndex(row)
        titles = [
            "Dashboard Overview",
            "Website Access & Whitelist Policy",
            "Application & Process Management",
            "Recurring Study Schedules",
            "Settings & System Controls"
        ]
        if 0 <= row < len(titles):
            self.page_title_lbl.setText(titles[row])

    def _on_tick(self):
        self.dashboard_tab.refresh_stats()

        status = self.scheduler.get_current_status()
        if status["is_blocking_active"]:
            self.status_pill.setText("● FOCUS SHIELD ACTIVE")
            self.status_pill.setStyleSheet("""
                background-color: rgba(34, 197, 94, 0.18);
                color: #16a34a;
                border: 1px solid rgba(34, 197, 94, 0.4);
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
            """)
        else:
            self.status_pill.setText("○ SHIELD IDLE")
            self.status_pill.setStyleSheet("""
                background-color: rgba(148, 163, 184, 0.12);
                color: #64748b;
                border: 1px solid rgba(148, 163, 184, 0.3);
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
            """)

    def _quick_emergency_unlock(self):
        confirm = QMessageBox.question(
            self,
            "Confirm Emergency Unlock",
            "Immediately cancel all active blocking sessions and restore open browser access?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.scheduler.cancel_active_sessions()
            try:
                self.website_blocker.unblock_all()
                QMessageBox.information(self, "Restrictions Lifted", "All restrictions lifted. Normal web access restored.")
            except Exception as e:
                QMessageBox.warning(self, "Notice", str(e))
            self._on_tick()

    def closeEvent(self, event):
        self.scheduler.stop_background_loop()
        super().closeEvent(event)
