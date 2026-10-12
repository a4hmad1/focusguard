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
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - Study Shield")
        self.resize(1080, 700)
        self.setMinimumSize(900, 600)

        # Initialize Core Services
        self.db = Database()
        self.app_blocker = AppBlocker(self.db)
        self.website_blocker = WebsiteBlocker(self.db)
        self.scheduler = Scheduler(self.db, self.app_blocker, self.website_blocker)
        self.scheduler.start_background_loop()

        # Load Theme (Default: black)
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
        self.websites_tab = WebsitesTab(self.db, self.website_blocker, self.scheduler)
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
        sidebar.setFixedWidth(210)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 18, 12, 18)
        layout.setSpacing(10)

        # Brand / Logo Header
        brand_box = QHBoxLayout()
        brand_box.setSpacing(8)
        
        logo_icon = QLabel("🛡️")
        logo_icon.setStyleSheet("font-size: 22px;")
        
        brand_text_box = QVBoxLayout()
        brand_text_box.setSpacing(0)
        brand_title = QLabel(APP_NAME)
        brand_title.setStyleSheet("font-size: 16px; font-weight: 800; letter-spacing: -0.3px;")
        brand_sub = QLabel("Study Shield")
        brand_sub.setStyleSheet("font-size: 11px; font-weight: 500; color: #8b949e;")
        brand_text_box.addWidget(brand_title)
        brand_text_box.addWidget(brand_sub)

        brand_box.addWidget(logo_icon)
        brand_box.addLayout(brand_text_box)
        layout.addLayout(brand_box)
        layout.addSpacing(10)

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

        # Version Footer
        ver_lbl = QLabel(f"v{APP_VERSION}")
        ver_lbl.setStyleSheet("color: #6e7681; font-size: 11px;")
        ver_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(ver_lbl)

        return sidebar

    def _create_header_bar(self) -> QFrame:
        header = QFrame()
        header.setObjectName("header_bar")
        header.setFixedHeight(52)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)

        self.page_title_lbl = QLabel("Dashboard")
        self.page_title_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #8b949e;")
        layout.addWidget(self.page_title_lbl)
        layout.addStretch()

        # Prominent Global Start and Stop Buttons
        self.start_shield_btn = QPushButton("▶  Start Focus")
        self.start_shield_btn.setFixedHeight(30)
        self.start_shield_btn.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                color: #ffffff;
                border: 1px solid #2ea043;
                border-radius: 6px;
                padding: 4px 14px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
            QPushButton:disabled {
                background-color: rgba(35, 134, 54, 0.25);
                color: rgba(255, 255, 255, 0.35);
                border: 1px solid rgba(46, 160, 67, 0.2);
            }
        """)
        self.start_shield_btn.clicked.connect(self._start_global_shield)
        layout.addWidget(self.start_shield_btn)

        self.stop_shield_btn = QPushButton("⏹  Stop Focus")
        self.stop_shield_btn.setFixedHeight(30)
        self.stop_shield_btn.setStyleSheet("""
            QPushButton {
                background-color: #da3633;
                color: #ffffff;
                border: 1px solid #f85149;
                border-radius: 6px;
                padding: 4px 14px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #b62324;
            }
            QPushButton:disabled {
                background-color: rgba(218, 54, 51, 0.25);
                color: rgba(255, 255, 255, 0.35);
                border: 1px solid rgba(248, 81, 73, 0.2);
            }
        """)
        self.stop_shield_btn.clicked.connect(self._stop_global_shield)
        layout.addWidget(self.stop_shield_btn)

        # Theme Switcher Button
        self.theme_btn = QPushButton()
        self.theme_btn.setProperty("class", "secondary")
        self.theme_btn.setFixedHeight(28)
        self._update_theme_button_text()
        self.theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_btn)

        # Status Pill
        self.status_pill = QLabel("○ SHIELD IDLE")
        self.status_pill.setStyleSheet("""
            background-color: rgba(110, 118, 129, 0.12);
            color: #8b949e;
            border: 1px solid rgba(110, 118, 129, 0.3);
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 11px;
            font-weight: 600;
        """)
        layout.addWidget(self.status_pill)

        # Emergency Unlock Header Button
        em_btn = QPushButton("Emergency Unlock")
        em_btn.setProperty("class", "danger")
        em_btn.setFixedHeight(28)
        em_btn.clicked.connect(self._quick_emergency_unlock)
        layout.addWidget(em_btn)

        return header

    def _start_global_shield(self):
        self.scheduler.start_focus()
        self._on_tick()

    def _stop_global_shield(self):
        self.scheduler.stop_focus()
        try:
            self.website_blocker.unblock_all()
        except Exception:
            pass
        self._on_tick()

    def _toggle_global_shield(self):
        status = self.scheduler.get_current_status()
        if status["is_blocking_active"]:
            self._stop_global_shield()
        else:
            self._start_global_shield()

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
            "Dashboard",
            "Website Whitelist",
            "Applications",
            "Study Schedules",
            "Settings"
        ]
        if 0 <= row < len(titles):
            self.page_title_lbl.setText(titles[row])

    def _on_tick(self):
        self.dashboard_tab.refresh_stats()

        status = self.scheduler.get_current_status()
        is_active = status["is_blocking_active"]
        if is_active:
            self.status_pill.setText("● SHIELD ACTIVE")
            self.status_pill.setStyleSheet("""
                background-color: rgba(46, 160, 67, 0.15);
                color: #3fb950;
                border: 1px solid rgba(46, 160, 67, 0.35);
                border-radius: 4px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 600;
            """)
            self.start_shield_btn.setEnabled(False)
            self.stop_shield_btn.setEnabled(True)
        else:
            self.status_pill.setText("○ SHIELD IDLE")
            self.status_pill.setStyleSheet("""
                background-color: rgba(110, 118, 129, 0.12);
                color: #8b949e;
                border: 1px solid rgba(110, 118, 129, 0.3);
                border-radius: 4px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 600;
            """)
            self.start_shield_btn.setEnabled(True)
            self.stop_shield_btn.setEnabled(False)

        # Sync tab states
        if hasattr(self.websites_tab, "update_status"):
            self.websites_tab.update_status(is_active)
        if hasattr(self.apps_tab, "update_status"):
            self.apps_tab.update_status(is_active)

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
