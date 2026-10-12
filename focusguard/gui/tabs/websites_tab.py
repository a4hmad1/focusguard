"""Websites Whitelist and Blacklist Management Tab."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from focusguard.core.database import Database
from focusguard.core.models import WebsiteRule
from focusguard.engine.website_blocker import WebsiteBlocker, CURATED_DISTRACTION_DOMAINS

class WebsitesTab(QWidget):
    def __init__(self, db: Database, website_blocker: WebsiteBlocker):
        super().__init__()
        self.db = db
        self.blocker = website_blocker

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header with Mode Indicator
        header_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title = QLabel("Website Protection & URL Whitelist")
        title.setProperty("class", "heading_large")
        subtitle = QLabel("Control approved websites or block distracting domains.")
        subtitle.setProperty("class", "subtext")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_row.addLayout(title_box)
        header_row.addStretch()

        # Mode Toggle Button
        self.mode_btn = QPushButton()
        self.mode_btn.clicked.connect(self._toggle_mode)
        header_row.addWidget(self.mode_btn)
        layout.addLayout(header_row)

        # Add Website Form Card
        add_frame = QFrame()
        add_frame.setObjectName("add_frame")
        add_frame.setStyleSheet("""
            QFrame#add_frame {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 14px;
            }
        """)
        add_layout = QHBoxLayout(add_frame)
        add_layout.setSpacing(10)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL or domain (e.g., https://wikipedia.org or youtube.com)")
        add_layout.addWidget(self.url_input, stretch=3)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Whitelist (Approved)", "Blacklist (Blocked)"])
        add_layout.addWidget(self.type_combo, stretch=1)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["Study & Research", "Social Media", "Video & Streaming", "Gaming", "News", "Custom"])
        add_layout.addWidget(self.category_combo, stretch=1)

        add_btn = QPushButton("Add Website")
        add_btn.clicked.connect(self._on_add_website)
        add_layout.addWidget(add_btn)

        layout.addWidget(add_frame)

        # Quick Actions and Search Filter
        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search websites...")
        self.search_input.textChanged.connect(self.load_rules)
        filter_row.addWidget(self.search_input, stretch=2)

        self.filter_type_combo = QComboBox()
        self.filter_type_combo.addItems(["All Types", "Whitelist Only", "Blacklist Only"])
        self.filter_type_combo.currentIndexChanged.connect(self.load_rules)
        filter_row.addWidget(self.filter_type_combo)

        preset_btn = QPushButton("Add Top Distractions Pack")
        preset_btn.setProperty("class", "secondary")
        preset_btn.clicked.connect(self._add_preset_distractions)
        filter_row.addWidget(preset_btn)

        layout.addLayout(filter_row)

        # Website Rules Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Domain", "Full URL", "Type", "Category", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self._update_mode_button()
        self.load_rules()

    def _update_mode_button(self):
        curr_mode = self.blocker.get_mode()
        if curr_mode == "whitelist":
            self.mode_btn.setText("Mode: WHITELIST (Strict - Only Approved Accessible)")
            self.mode_btn.setStyleSheet("background-color: #059669; border-color: #10b981; color: white;")
        else:
            self.mode_btn.setText("Mode: BLACKLIST (Standard - Blocks Distractions)")
            self.mode_btn.setStyleSheet("background-color: #2563eb; border-color: #3b82f6; color: white;")

    def _toggle_mode(self):
        curr = self.blocker.get_mode()
        new_mode = "whitelist" if curr == "blacklist" else "blacklist"
        try:
            self.blocker.set_mode(new_mode)
            self._update_mode_button()
            self.load_rules()
        except PermissionError as pe:
            QMessageBox.warning(self, "Elevation Required", str(pe))

    def _on_add_website(self):
        raw_url = self.url_input.text().strip()
        if not raw_url:
            return

        domain = WebsiteRule.extract_domain(raw_url)
        if not domain:
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid website URL or domain.")
            return

        selected_type = "whitelist" if "Whitelist" in self.type_combo.currentText() else "blacklist"
        category = self.category_combo.currentText()

        rule = WebsiteRule(
            url=raw_url,
            domain=domain,
            rule_type=selected_type,
            is_active=True,
            category=category
        )
        self.db.add_website_rule(rule)
        self.url_input.clear()

        try:
            self.blocker.sync_rules()
        except PermissionError:
            pass

        self.load_rules()

    def _add_preset_distractions(self):
        for dist in CURATED_DISTRACTION_DOMAINS[:15]:
            rule = WebsiteRule(
                url=f"https://{dist}",
                domain=dist,
                rule_type="blacklist",
                is_active=True,
                category="Social & Media"
            )
            self.db.add_website_rule(rule)
        try:
            self.blocker.sync_rules()
        except PermissionError:
            pass
        self.load_rules()
        QMessageBox.information(self, "Preset Applied", "Top distraction websites added to Blacklist.")

    def load_rules(self):
        query = self.search_input.text().strip().lower()
        filter_idx = self.filter_type_combo.currentIndex()
        rule_type = None
        if filter_idx == 1:
            rule_type = "whitelist"
        elif filter_idx == 2:
            rule_type = "blacklist"

        all_rules = self.db.get_website_rules(rule_type=rule_type)
        filtered = [
            r for r in all_rules
            if not query or query in r.domain.lower() or query in r.url.lower() or query in r.category.lower()
        ]

        self.table.setRowCount(len(filtered))
        for row, r in enumerate(filtered):
            # Domain
            self.table.setItem(row, 0, QTableWidgetItem(r.domain))
            # URL
            self.table.setItem(row, 1, QTableWidgetItem(r.url))
            # Type Badge
            type_item = QTableWidgetItem(r.rule_type.upper())
            type_item.setTextAlignment(Qt.AlignCenter)
            if r.rule_type == "whitelist":
                type_item.setForeground(Qt.green)
            else:
                type_item.setForeground(Qt.red)
            self.table.setItem(row, 2, type_item)
            # Category
            self.table.setItem(row, 3, QTableWidgetItem(r.category))

            # Delete button
            del_btn = QPushButton("Remove")
            del_btn.setProperty("class", "danger")
            del_btn.clicked.connect(lambda _, d=r.domain: self._delete_rule(d))
            self.table.setCellWidget(row, 4, del_btn)

    def _delete_rule(self, domain: str):
        self.db.remove_website_rule(domain)
        try:
            self.blocker.sync_rules()
        except PermissionError:
            pass
        self.load_rules()
