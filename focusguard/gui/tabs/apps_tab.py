"""Application and Process Management Tab."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, QSize
from focusguard.core.database import Database
from focusguard.core.models import AppRule
from focusguard.core.safety import is_critical_process
from focusguard.core.duration import parse_duration
from focusguard.engine.app_detector import AppDetector
from focusguard.engine.app_blocker import AppBlocker
from focusguard.engine.scheduler import Scheduler
from focusguard.gui.icons import get_app_icon
from focusguard.gui.widgets.badge import make_badge

class AppsTab(QWidget):
    def __init__(self, db: Database, scheduler: Scheduler):
        super().__init__()
        self.db = db
        self.scheduler = scheduler
        self.detector = AppDetector()
        self.blocker = AppBlocker(db)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title = QLabel("Applications Blocked While Studying")
        title.setProperty("class", "heading_large")
        subtitle = QLabel("Choose desktop programs to block during focus sessions (e.g. Discord, Steam, games). Essential system apps are protected.")
        subtitle.setProperty("class", "subtext")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_row.addLayout(title_box)
        header_row.addStretch()

        refresh_btn = QPushButton("Refresh List")
        refresh_btn.setProperty("class", "secondary")
        refresh_btn.setFixedHeight(30)
        refresh_btn.clicked.connect(self.load_applications)
        header_row.addWidget(refresh_btn)
        layout.addLayout(header_row)

        # Search and Filters
        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search application by name...")
        self.search_input.textChanged.connect(self.load_applications)
        filter_row.addWidget(self.search_input, stretch=2)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Applications", "Running Only", "Blocked Only", "System Protected"])
        self.filter_combo.currentIndexChanged.connect(self.load_applications)
        filter_row.addWidget(self.filter_combo)

        layout.addLayout(filter_row)

        # Apps Table (4 Clean Columns with Native Icons)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Application Name", "Status", "Study Restriction", "Action"])
        self.table.setIconSize(QSize(24, 24))
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(46)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 120)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 135)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 130)

        layout.addWidget(self.table)

        self.load_applications()

    def load_applications(self):
        query = self.search_input.text().strip().lower()
        filter_mode = self.filter_combo.currentText()

        installed = self.detector.get_installed_applications()
        running_procs = self.detector.get_running_processes()
        running_names = {p["clean_name"] for p in running_procs}
        blocked_rules = {r.process_name.lower(): r for r in self.db.get_app_rules(only_blocked=True)}

        rows = []
        for app in installed:
            exec_clean = app.exec_name.lower()
            is_running = exec_clean in running_names or f"{exec_clean}.exe" in running_names
            is_blocked = exec_clean in blocked_rules or f"{exec_clean}.exe" in blocked_rules
            is_crit = is_critical_process(app.exec_name)

            if query and query not in app.name.lower() and query not in exec_clean:
                continue

            if filter_mode == "Running Only" and not is_running:
                continue
            elif filter_mode == "Blocked Only" and not is_blocked:
                continue
            elif filter_mode == "System Protected" and not is_crit:
                continue

            rows.append({
                "app": app,
                "is_running": is_running,
                "is_blocked": is_blocked,
                "is_critical": is_crit
            })

        self.table.setRowCount(len(rows))
        for i, item in enumerate(rows):
            app = item["app"]
            is_run = item["is_running"]
            is_blk = item["is_blocked"]
            is_crit = item["is_critical"]

            # Application Name & Native Freedesktop/System Icon
            icon = get_app_icon(app.icon, app.exec_name)
            name_text = app.name
            if app.exec_name.lower() != app.name.lower():
                name_text = f"{app.name}  ·  {app.exec_name}"
            name_item = QTableWidgetItem(name_text)
            name_item.setIcon(icon)
            name_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            name_item.setToolTip(f"Application: {app.name}\nProcess: {app.exec_name}\nCategory: {app.category}")
            self.table.setItem(i, 0, name_item)

            # Running state badge
            if is_run:
                self.table.setCellWidget(i, 1, make_badge("●  Running", "running"))
            else:
                self.table.setCellWidget(i, 1, make_badge("○  Closed", "idle"))

            # Restriction badge
            if is_crit:
                self.table.setCellWidget(i, 2, make_badge("🛡  Protected", "protected"))
            elif is_blk:
                self.table.setCellWidget(i, 2, make_badge("✕  Blocked", "blocked"))
            else:
                self.table.setCellWidget(i, 2, make_badge("✓  Allowed", "allowed"))

            # Action button
            actions_widget = QWidget()
            act_layout = QHBoxLayout(actions_widget)
            act_layout.setContentsMargins(6, 2, 6, 2)
            act_layout.setAlignment(Qt.AlignCenter)

            if is_crit:
                lbl = QLabel("System Safe")
                lbl.setStyleSheet("color: #6e7681; font-size: 11px; font-weight: 600;")
                lbl.setAlignment(Qt.AlignCenter)
                act_layout.addWidget(lbl)
            else:
                toggle_btn = QPushButton("Allow App" if is_blk else "Block App")
                toggle_btn.setProperty("class", "secondary" if is_blk else "danger")
                toggle_btn.setFixedHeight(28)
                toggle_btn.setFixedWidth(100)
                toggle_btn.clicked.connect(lambda _, a=app, b=is_blk: self._toggle_app_block(a, not b))
                act_layout.addWidget(toggle_btn)

            self.table.setCellWidget(i, 3, actions_widget)

    def _toggle_app_block(self, app, should_block: bool):
        clean = app.exec_name.lower()
        if should_block:
            rule = AppRule(app_name=app.name, process_name=clean, is_blocked=True, category=app.category)
            self.db.add_app_rule(rule)
            self.blocker.check_and_enforce()
        else:
            self.db.set_app_blocked_status(clean, blocked=False)
        self.load_applications()

    def _timed_block_app(self, app):
        duration_str, ok = QInputDialog.getText(
            self,
            "Timed App Block",
            f"Specify duration to block '{app.name}' (e.g. 1h, 30m, 2h 15m):"
        )
        if ok and duration_str:
            td = parse_duration(duration_str)
            if not td:
                QMessageBox.warning(self, "Invalid Duration", "Please provide a valid duration like 45m or 2h.")
                return

            clean = app.exec_name.lower()
            rule = AppRule(app_name=app.name, process_name=clean, is_blocked=True, category=app.category)
            self.db.add_app_rule(rule)
            self.scheduler.start_timed_session(
                duration=td,
                target=clean,
                session_type="app_timed",
                reason=f"Block {app.name} for {duration_str}"
            )
            self.blocker.check_and_enforce()
            self.load_applications()
            QMessageBox.information(self, "Timed Restriction Active", f"'{app.name}' is now blocked for {duration_str}.")

    def _on_start_focus(self):
        if self.scheduler:
            self.scheduler.start_focus()
            self.update_status(True)

    def _on_stop_focus(self):
        if self.scheduler:
            self.scheduler.stop_focus()
            self.update_status(False)

    def update_status(self, is_active: bool):
        pass
