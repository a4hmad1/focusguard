"""Formal Websites Whitelist & Access Management Tab."""

import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from focusguard.core.database import Database
from focusguard.core.models import WebsiteRule
from focusguard.engine.website_blocker import WebsiteBlocker

class WebsitesTab(QWidget):
    def __init__(self, db: Database, website_blocker: WebsiteBlocker):
        super().__init__()
        self.db = db
        self.blocker = website_blocker

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header with Policy Information
        header_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("Website Access & Whitelist Policy")
        title.setProperty("class", "heading_large")
        subtitle = QLabel("Only explicitly saved URLs remain open in browsers. All other websites are blocked.")
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

        # Policy Alert Card
        self.policy_card = QFrame()
        self.policy_card.setProperty("class", "card")
        p_layout = QHBoxLayout(self.policy_card)
        p_layout.setContentsMargins(12, 10, 12, 10)
        self.policy_label = QLabel(
            "🛡️ <strong>STRICT WHITELIST ACTIVE:</strong> Every website on the internet is blocked across all browsers, "
            "<strong>EXCEPT</strong> the approved URLs saved in your list below."
        )
        self.policy_label.setStyleSheet("font-size: 12px;")
        p_layout.addWidget(self.policy_label)
        layout.addWidget(self.policy_card)

        # Add Website Form Card
        add_frame = QFrame()
        add_frame.setObjectName("add_frame")
        add_frame.setProperty("class", "card")
        add_layout = QHBoxLayout(add_frame)
        add_layout.setContentsMargins(12, 10, 12, 10)
        add_layout.setSpacing(8)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter approved URL (e.g. wikipedia.org, docs.python.org, or canvas.edu)")
        add_layout.addWidget(self.url_input, stretch=3)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["Study & Reference", "School / University", "Programming Docs", "Research", "Custom"])
        add_layout.addWidget(self.category_combo, stretch=1)

        add_btn = QPushButton("+ Save & Approve URL")
        add_btn.clicked.connect(self._on_add_website)
        add_layout.addWidget(add_btn)

        preset_btn = QPushButton("Add Study Pack")
        preset_btn.setProperty("class", "secondary")
        preset_btn.clicked.connect(self._add_preset_study_sites)
        add_layout.addWidget(preset_btn)

        layout.addWidget(add_frame)

        # Search Bar & Interactive URL Checker
        checker_frame = QFrame()
        checker_frame.setProperty("class", "card")
        chk_layout = QHBoxLayout(checker_frame)
        chk_layout.setContentsMargins(12, 8, 12, 8)
        chk_layout.setSpacing(10)

        chk_layout.addWidget(QLabel("🔍 <strong>Test URL Access:</strong>"))
        self.test_input = QLineEdit()
        self.test_input.setPlaceholderText("Type any website (e.g. google.com or wikipedia.org)...")
        chk_layout.addWidget(self.test_input, stretch=2)

        test_btn = QPushButton("Check Status")
        test_btn.setProperty("class", "secondary")
        test_btn.clicked.connect(self._check_test_url)
        chk_layout.addWidget(test_btn)

        self.test_result_label = QLabel("Result: Ready to test")
        self.test_result_label.setStyleSheet("font-size: 12px; font-weight: 700; color: #64748b;")
        chk_layout.addWidget(self.test_result_label, stretch=1)

        layout.addWidget(checker_frame)

        # Search filter
        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search approved URLs...")
        self.search_input.textChanged.connect(self.load_rules)
        filter_row.addWidget(self.search_input)
        layout.addLayout(filter_row)

        # Table of Approved Websites
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Approved Domain", "Full URL", "Category", "Access Permission", "Actions"])
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
            self.mode_btn.setText("Policy: STRICT WHITELIST (Only Approved URLs Open)")
            self.mode_btn.setStyleSheet("background-color: #16a34a; border-color: #15803d; color: white;")
            self.policy_label.setText(
                "🛡️ <strong>STRICT WHITELIST ACTIVE:</strong> All websites across all browsers are blocked, "
                "<strong>EXCEPT</strong> your saved approved URLs below."
            )
        else:
            self.mode_btn.setText("Policy: BLACKLIST (Blocks Selected Websites)")
            self.mode_btn.setStyleSheet("background-color: #2563eb; border-color: #1d4ed8; color: white;")
            self.policy_label.setText(
                "⚠️ <strong>BLACKLIST MODE:</strong> Web browsing is open by default, only explicitly blocked websites are restricted."
            )

    def _toggle_mode(self):
        curr = self.blocker.get_mode()
        new_mode = "blacklist" if curr == "whitelist" else "whitelist"
        try:
            self.blocker.set_mode(new_mode)
            self._update_mode_button()
            self.load_rules()
        except PermissionError as pe:
            QMessageBox.warning(self, "Permission Note", str(pe))

    def _check_test_url(self):
        raw = self.test_input.text().strip()
        if not raw:
            return
        is_allowed = self.blocker.is_url_allowed(raw)
        if is_allowed:
            self.test_result_label.setText("✅ ALLOWED (In Saved Whitelist)")
            self.test_result_label.setStyleSheet("color: #16a34a; font-weight: 700;")
        else:
            self.test_result_label.setText("⛔ BLOCKED (All non-saved sites blocked)")
            self.test_result_label.setStyleSheet("color: #dc2626; font-weight: 700;")

    def _on_add_website(self):
        raw_url = self.url_input.text().strip()
        if not raw_url:
            return

        domain = WebsiteRule.extract_domain(raw_url)
        if not domain:
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid URL or domain.")
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
        QMessageBox.information(self, "URL Approved", f"'{domain}' is saved in your whitelist and will remain accessible.")

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
        for row, r in enumerate(filtered):
            # Domain
            self.table.setItem(row, 0, QTableWidgetItem(r.domain))
            # Full URL
            self.table.setItem(row, 1, QTableWidgetItem(r.url))
            # Category
            self.table.setItem(row, 2, QTableWidgetItem(r.category))

            # Status Badge
            perm_item = QTableWidgetItem("● ALLOWED (OPEN)" if r.rule_type == "whitelist" else "⛔ BLOCKED")
            perm_item.setTextAlignment(Qt.AlignCenter)
            perm_item.setForeground(Qt.green if r.rule_type == "whitelist" else Qt.red)
            self.table.setItem(row, 3, perm_item)

            # Actions cell
            actions_widget = QWidget()
            act_layout = QHBoxLayout(actions_widget)
            act_layout.setContentsMargins(2, 2, 2, 2)
            act_layout.setSpacing(6)

            open_btn = QPushButton("Open")
            open_btn.setProperty("class", "secondary")
            full_url = r.url if "://" in r.url else f"https://{r.domain}"
            open_btn.clicked.connect(lambda _, u=full_url: webbrowser.open(u))
            act_layout.addWidget(open_btn)

            del_btn = QPushButton("Remove")
            del_btn.setProperty("class", "danger")
            del_btn.clicked.connect(lambda _, d=r.domain: self._delete_rule(d))
            act_layout.addWidget(del_btn)

            self.table.setCellWidget(row, 4, actions_widget)

    def _delete_rule(self, domain: str):
        self.db.remove_website_rule(domain)
        try:
            self.blocker.sync_rules()
        except Exception:
            pass
        self.load_rules()
