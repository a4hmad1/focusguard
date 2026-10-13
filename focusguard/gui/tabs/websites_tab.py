"""Website Whitelist & Access Control Tab - Modern Professional Redesign."""

import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QSize
from typing import Optional
from focusguard.core.database import Database
from focusguard.core.models import WebsiteRule
from focusguard.engine.website_blocker import WebsiteBlocker
from focusguard.engine.scheduler import Scheduler
from focusguard.gui.icons import get_web_icon
from focusguard.gui.widgets.badge import make_badge

class WebsitesTab(QWidget):
    def __init__(self, db: Database, website_blocker: WebsiteBlocker, scheduler: Optional[Scheduler] = None):
        super().__init__()
        self.db = db
        self.blocker = website_blocker
        self.scheduler = scheduler

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header with Title and Start/Stop Controls
        header_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        
        title = QLabel("Websites I Can Open While Studying")
        title.setProperty("class", "heading_large")
        subtitle = QLabel("During Focus Mode, web browsers will ONLY open these approved websites. All other websites are blocked.")
        subtitle.setProperty("class", "subtext")
        
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_row.addLayout(title_box)
        header_row.addStretch()

        self.mode_badge = QLabel("●  STRICT WHITELIST")
        self.mode_badge.setStyleSheet("""
            background-color: rgba(22, 163, 74, 0.15);
            color: #16a34a;
            border: 1px solid rgba(22, 163, 74, 0.35);
            border-radius: 20px;
            padding: 5px 14px;
            font-size: 11px;
            font-weight: 700;
        """)
        header_row.addWidget(self.mode_badge)
        layout.addLayout(header_row)

        # Unified Action Panel (Add Website & Study Pack)
        panel = QFrame()
        panel.setProperty("class", "card")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(14, 14, 14, 14)
        panel_layout.setSpacing(12)

        # Row 1: Add Input + Category + Add Button
        add_row = QHBoxLayout()
        add_row.setSpacing(8)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter website address (e.g. wikipedia.org, github.com, canvas.edu)...")
        add_row.addWidget(self.url_input, stretch=3)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["Study & Reference", "School / University", "Programming Docs", "Research", "Custom"])
        add_row.addWidget(self.category_combo, stretch=1)

        add_btn = QPushButton("+ Add Website")
        add_btn.setProperty("class", "primary")
        add_btn.clicked.connect(self._on_add_website)
        add_row.addWidget(add_btn)

        preset_btn = QPushButton("📚  Add Study Pack")
        preset_btn.setProperty("class", "secondary")
        preset_btn.clicked.connect(self._add_preset_study_sites)
        add_row.addWidget(preset_btn)

        panel_layout.addLayout(add_row)

        # Row 2: Search filter + Test URL access validator
        tools_row = QHBoxLayout()
        tools_row.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search approved websites...")
        self.search_input.textChanged.connect(self.load_rules)
        tools_row.addWidget(self.search_input, stretch=2)

        # Tester
        tools_row.addWidget(QLabel("Test a Website:"))
        self.test_input = QLineEdit()
        self.test_input.setPlaceholderText("e.g. youtube.com or wikipedia.org")
        self.test_input.setFixedWidth(220)
        tools_row.addWidget(self.test_input)

        test_btn = QPushButton("Check Access")
        test_btn.setProperty("class", "secondary")
        test_btn.clicked.connect(self._check_test_url)
        tools_row.addWidget(test_btn)

        self.test_result_label = QLabel("Ready")
        self.test_result_label.setProperty("class", "subtext")
        self.test_result_label.setStyleSheet("font-weight: 600;")
        tools_row.addWidget(self.test_result_label)

        panel_layout.addLayout(tools_row)
        layout.addWidget(panel)

        # Table of Approved Websites (3 Clean Columns)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Approved Website Domain", "Category", "Actions"])
        self.table.setIconSize(QSize(20, 20))
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(46)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setShowGrid(False)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 140)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 170)
        layout.addWidget(self.table)

        self.load_rules()

    def _update_mode_button(self):
        curr_mode = self.blocker.get_mode()
        if curr_mode == "whitelist":
            self.mode_badge.setText("● STRICT WHITELIST ACTIVE")
            self.mode_badge.setProperty("class", "badge_active")
            self.mode_badge.setStyleSheet("""
                background-color: rgba(46, 160, 67, 0.15);
                color: #3fb950;
                border: 1px solid rgba(46, 160, 67, 0.35);
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
            """)
            self.mode_btn.setText("Switch to Blacklist Mode")
        else:
            self.mode_badge.setText("⚠️ BLACKLIST MODE")
            self.mode_badge.setStyleSheet("""
                background-color: rgba(31, 111, 235, 0.15);
                color: #58a6ff;
                border: 1px solid rgba(31, 111, 235, 0.35);
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
            """)
            self.mode_btn.setText("Switch to Whitelist Mode")

    def _toggle_mode(self):
        curr = self.blocker.get_mode()
        new_mode = "blacklist" if curr == "whitelist" else "whitelist"
        try:
            self.blocker.set_mode(new_mode)
            self._update_mode_button()
            self.load_rules()
        except Exception as e:
            QMessageBox.warning(self, "Notice", str(e))

    def _on_start_focus(self):
        if self.scheduler:
            self.scheduler.start_focus()
            self.update_status(True)

    def _on_stop_focus(self):
        if self.scheduler:
            self.scheduler.stop_focus()
            try:
                self.blocker.unblock_all()
            except Exception:
                pass
            self.update_status(False)

    def update_status(self, is_active: bool):
        pass

    def _check_test_url(self):
        raw = self.test_input.text().strip()
        if not raw:
            return
        is_allowed = self.blocker.is_url_allowed(raw)
        if is_allowed:
            self.test_result_label.setText("ALLOWED (Whitelisted)")
            self.test_result_label.setStyleSheet("color: #3fb950; font-weight: 700;")
        else:
            self.test_result_label.setText("BLOCKED (Unapproved)")
            self.test_result_label.setStyleSheet("color: #f85149; font-weight: 700;")

    def _on_add_website(self):
        raw_url = self.url_input.text().strip()
        if not raw_url:
            return

        domain = WebsiteRule.extract_domain(raw_url)
        if not domain:
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid website URL or domain.")
            return

        category = self.category_combo.currentText()
        rule = WebsiteRule(
            url=raw_url,
            domain=domain,
            rule_type="whitelist",
            is_active=True,
            category=category
        )
        self.db.add_website_rule(rule)
        self.url_input.clear()

        try:
            self.blocker.sync_rules()
        except Exception:
            pass

        self.load_rules()

    def _add_preset_study_sites(self):
        presets = [
            ("https://wikipedia.org", "wikipedia.org", "Study & Reference"),
            ("https://khanacademy.org", "khanacademy.org", "Study & Reference"),
            ("https://docs.python.org", "docs.python.org", "Programming Docs"),
            ("https://github.com", "github.com", "Programming Docs"),
            ("https://coursera.org", "coursera.org", "Study & Reference"),
        ]
        for url, dom, cat in presets:
            r = WebsiteRule(url=url, domain=dom, rule_type="whitelist", is_active=True, category=cat)
            self.db.add_website_rule(r)

        try:
            self.blocker.sync_rules()
        except Exception:
            pass
        self.load_rules()
        QMessageBox.information(self, "Study Pack Added", "Standard study and educational websites added to Whitelist.")

    def load_rules(self):
        query = self.search_input.text().strip().lower()
        curr_mode = self.blocker.get_mode()
        target_type = "whitelist" if curr_mode == "whitelist" else None

        all_rules = self.db.get_website_rules(rule_type=target_type)
        filtered = [
            r for r in all_rules
            if not query or query in r.domain.lower() or query in r.url.lower() or query in r.category.lower()
        ]

        self.table.setRowCount(len(filtered))
        web_icon = get_web_icon()
        for row, r in enumerate(filtered):
            # Domain with native web icon
            dom_item = QTableWidgetItem(r.domain)
            dom_item.setIcon(web_icon)
            dom_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            dom_item.setToolTip(f"Whitelisted Domain: {r.domain}\nSaved URL: {r.url or r.domain}")
            self.table.setItem(row, 0, dom_item)

            # Category pill badge
            cat_text = r.category.capitalize() if r.category else "General"
            self.table.setCellWidget(row, 1, make_badge(cat_text, "category"))

            # Actions cell (Open in Browser & Remove)
            actions_widget = QWidget()
            act_layout = QHBoxLayout(actions_widget)
            act_layout.setContentsMargins(6, 2, 6, 2)
            act_layout.setSpacing(6)
            act_layout.setAlignment(Qt.AlignCenter)

            open_btn = QPushButton("Open")
            open_btn.setProperty("class", "secondary")
            open_btn.setFixedHeight(28)
            full_url = r.url if "://" in r.url else f"https://{r.domain}"
            open_btn.clicked.connect(lambda _, u=full_url: webbrowser.open(u))
            act_layout.addWidget(open_btn)

            del_btn = QPushButton("Remove")
            del_btn.setProperty("class", "danger")
            del_btn.setFixedHeight(28)
            del_btn.clicked.connect(lambda _, d=r.domain: self._delete_rule(d))
            act_layout.addWidget(del_btn)

            self.table.setCellWidget(row, 2, actions_widget)

    def _delete_rule(self, domain: str):
        self.db.remove_website_rule(domain)
        try:
            self.blocker.sync_rules()
        except Exception:
            pass
        self.load_rules()
