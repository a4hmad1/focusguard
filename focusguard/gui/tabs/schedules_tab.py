"""Recurring Schedules Management Tab."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QCheckBox, QTimeEdit, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QTime
from focusguard.core.database import Database
from focusguard.core.models import ScheduleRule

class SchedulesTab(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title = QLabel("Recurring Study Schedules")
        title.setProperty("class", "heading_large")
        subtitle = QLabel("Automate distraction blocking during study or work hours.")
        subtitle.setProperty("class", "subtext")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_row.addLayout(title_box)
        header_row.addStretch()
        layout.addLayout(header_row)

        # Create New Schedule Card
        sched_card = QFrame()
        sched_card.setObjectName("sched_card")
        sched_card.setStyleSheet("""
            QFrame#sched_card {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        card_layout = QVBoxLayout(sched_card)
        card_layout.setSpacing(12)

        card_title = QLabel("Create New Recurring Schedule")
        card_title.setProperty("class", "heading_medium")
        card_layout.addWidget(card_title)

        inputs_row = QHBoxLayout()
        inputs_row.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Schedule Name (e.g. Deep Work Morning)")
        inputs_row.addWidget(self.name_input, stretch=2)

        inputs_row.addWidget(QLabel("Start:"))
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(9, 0))
        inputs_row.addWidget(self.start_time)

        inputs_row.addWidget(QLabel("End:"))
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(17, 0))
        inputs_row.addWidget(self.end_time)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Blacklist Mode", "Whitelist Mode"])
        inputs_row.addWidget(self.mode_combo)

        add_btn = QPushButton("Save Schedule")
        add_btn.clicked.connect(self._on_save_schedule)
        inputs_row.addWidget(add_btn)

        card_layout.addLayout(inputs_row)

        # Days Selection Row
        days_row = QHBoxLayout()
        days_row.setSpacing(12)
        days_row.addWidget(QLabel("Active Days:"))

        self.day_checkboxes = {}
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            cb = QCheckBox(day)
            if day in ["Mon", "Tue", "Wed", "Thu", "Fri"]:
                cb.setChecked(True)
            days_row.addWidget(cb)
            self.day_checkboxes[day] = cb

        days_row.addStretch()
        card_layout.addLayout(days_row)

        layout.addWidget(sched_card)

        # Schedules List Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Name", "Days of Week", "Hours (Start - End)", "Mode", "Active", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.load_schedules()

    def _on_save_schedule(self):
        name = self.name_input.text().strip() or "Study Session"
        selected_days = [day for day, cb in self.day_checkboxes.items() if cb.isChecked()]
        if not selected_days:
            QMessageBox.warning(self, "No Days Selected", "Please select at least one day of the week.")
            return

        s_time = self.start_time.time().toString("HH:mm")
        e_time = self.end_time.time().toString("HH:mm")
        mode = "whitelist" if "Whitelist" in self.mode_combo.currentText() else "blacklist"

        rule = ScheduleRule(
            name=name,
            days_of_week=",".join(selected_days),
            start_time=s_time,
            end_time=e_time,
            mode=mode,
            is_enabled=True
        )
        self.db.add_schedule_rule(rule)
        self.name_input.clear()
        self.load_schedules()
        QMessageBox.information(self, "Schedule Saved", f"Recurring schedule '{name}' created successfully.")

    def load_schedules(self):
        rules = self.db.get_schedule_rules()
        self.table.setRowCount(len(rules))

        for row, r in enumerate(rules):
            self.table.setItem(row, 0, QTableWidgetItem(r.name))
            self.table.setItem(row, 1, QTableWidgetItem(r.days_of_week))
            self.table.setItem(row, 2, QTableWidgetItem(f"{r.start_time} - {r.end_time}"))
            self.table.setItem(row, 3, QTableWidgetItem(r.mode.upper()))

            # Enable Toggle
            en_cb = QCheckBox("Enabled" if r.is_enabled else "Disabled")
            en_cb.setChecked(r.is_enabled)
            en_cb.toggled.connect(lambda chk, rid=r.id: self._toggle_schedule(rid, chk))
            self.table.setCellWidget(row, 4, en_cb)

            # Delete
            del_btn = QPushButton("Delete")
            del_btn.setProperty("class", "danger")
            del_btn.clicked.connect(lambda _, rid=r.id: self._delete_schedule(rid))
            self.table.setCellWidget(row, 5, del_btn)

    def _toggle_schedule(self, schedule_id: int, enabled: bool):
        self.db.toggle_schedule_rule(schedule_id, enabled)
        self.load_schedules()

    def _delete_schedule(self, schedule_id: int):
        self.db.remove_schedule_rule(schedule_id)
        self.load_schedules()
