"""Application and Process Management Tab."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt
from focusguard.core.database import Database
from focusguard.core.models import AppRule
from focusguard.core.safety import is_critical_process
from focusguard.core.duration import parse_duration
from focusguard.engine.app_detector import AppDetector
from focusguard.engine.app_blocker import AppBlocker
from focusguard.engine.scheduler import Scheduler

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
        title = QLabel("Application & Process Management")
        title.setProperty("class", "heading_large")
        subtitle = QLabel("Detect running programs and control application execution.")
        subtitle.setProperty("class", "subtext")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_row.addLayout(title_box)
        header_row.addStretch()

        refresh_btn = QPushButton("Refresh Apps List")
        refresh_btn.setProperty("class", "secondary")
        refresh_btn.clicked.connect(self.load_applications)
        header_row.addWidget(refresh_btn)
        layout.addLayout(header_row)

        # Search and Filters
        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search application by name or executable...")
        self.search_input.textChanged.connect(self.load_applications)
        filter_row.addWidget(self.search_input, stretch=2)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Applications", "Running Only", "Blocked Only", "System Protected"])
        self.filter_combo.currentIndexChanged.connect(self.load_applications)
        filter_row.addWidget(self.filter_combo)

        layout.addLayout(filter_row)

        # Apps Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Application Name", "Executable / Process", "Process State", "Restriction Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
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

            # Name
            self.table.setItem(i, 0, QTableWidgetItem(app.name))
            # Executable
            self.table.setItem(i, 1, QTableWidgetItem(app.exec_name))

            # Running state badge
            run_item = QTableWidgetItem("Running" if is_run else "Stopped")
            run_item.setTextAlignment(Qt.AlignCenter)
            run_item.setForeground(Qt.green if is_run else Qt.gray)
            self.table.setItem(i, 2, run_item)

            # Restriction badge
            if is_crit:
                restr_item = QTableWidgetItem("System Protected")
                restr_item.setForeground(Qt.cyan)
            elif is_blk:
                restr_item = QTableWidgetItem("Blocked")
                restr_item.setForeground(Qt.red)
            else:
                restr_item = QTableWidgetItem("Allowed")
                restr_item.setForeground(Qt.blue)
            restr_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, restr_item)

            # Actions cell
            actions_widget = QWidget()
            act_layout = QHBoxLayout(actions_widget)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setSpacing(6)

            if is_crit:
                lbl = QLabel("Protected OS")
                lbl.setStyleSheet("color: #38bdf8; font-weight: 600;")
                act_layout.addWidget(lbl)
            else:
                toggle_btn = QPushButton("Unblock" if is_blk else "Block")
                toggle_btn.setProperty("class", "secondary" if is_blk else "danger")
                toggle_btn.clicked.connect(lambda _, a=app, b=is_blk: self._toggle_app_block(a, not b))
                act_layout.addWidget(toggle_btn)

                timed_btn = QPushButton("Timed...")
                timed_btn.setProperty("class", "secondary")
                timed_btn.clicked.connect(lambda _, a=app: self._timed_block_app(a))
                act_layout.addWidget(timed_btn)

            self.table.setCellWidget(i, 4, actions_widget)

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
