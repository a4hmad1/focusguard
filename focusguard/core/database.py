"""SQLite Database repository for FocusGuard."""

import sqlite3
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from focusguard.core.config import get_db_path
from focusguard.core.models import WebsiteRule, AppRule, ScheduleRule, ActiveSession, AppSettings

class Database:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or get_db_path()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize database schema with tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Website rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS website_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    domain TEXT NOT NULL UNIQUE,
                    rule_type TEXT NOT NULL DEFAULT 'blacklist',
                    is_active INTEGER NOT NULL DEFAULT 1,
                    category TEXT NOT NULL DEFAULT 'General',
                    created_at TEXT NOT NULL
                )
            """)

            # App rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    process_name TEXT NOT NULL UNIQUE,
                    is_blocked INTEGER NOT NULL DEFAULT 1,
                    path TEXT,
                    category TEXT NOT NULL DEFAULT 'General',
                    created_at TEXT NOT NULL
                )
            """)

            # Schedule rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedule_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    days_of_week TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    mode TEXT NOT NULL DEFAULT 'blacklist',
                    is_enabled INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                )
            """)

            # Active sessions table (timed blocking)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    reason TEXT NOT NULL DEFAULT 'Timed focus session'
                )
            """)

            # App settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # Audit log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT NOT NULL
                )
            """)

            conn.commit()

    # --- Website Rules CRUD ---
    def add_website_rule(self, rule: WebsiteRule) -> int:
        clean_domain = WebsiteRule.extract_domain(rule.url or rule.domain)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO website_rules (url, domain, rule_type, is_active, category, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(domain) DO UPDATE SET
                    url = excluded.url,
                    rule_type = excluded.rule_type,
                    is_active = excluded.is_active,
                    category = excluded.category
            """, (
                rule.url or clean_domain,
                clean_domain,
                rule.rule_type,
                1 if rule.is_active else 0,
                rule.category,
                rule.created_at or datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid

    def get_website_rules(self, rule_type: Optional[str] = None, only_active: bool = False) -> List[WebsiteRule]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM website_rules WHERE 1=1"
            params: List[Any] = []
            if rule_type:
                query += " AND rule_type = ?"
                params.append(rule_type)
            if only_active:
                query += " AND is_active = 1"
            query += " ORDER BY domain ASC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                WebsiteRule(
                    id=row["id"],
                    url=row["url"],
                    domain=row["domain"],
                    rule_type=row["rule_type"],
                    is_active=bool(row["is_active"]),
                    category=row["category"],
                    created_at=row["created_at"]
                )
                for row in rows
            ]

    def remove_website_rule(self, domain_or_url: str) -> bool:
        clean_domain = WebsiteRule.extract_domain(domain_or_url)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM website_rules WHERE domain = ? OR url = ?", (clean_domain, domain_or_url))
            conn.commit()
            return cursor.rowcount > 0

    def toggle_website_rule(self, domain: str, active: bool) -> bool:
        clean_domain = WebsiteRule.extract_domain(domain)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE website_rules SET is_active = ? WHERE domain = ?", (1 if active else 0, clean_domain))
            conn.commit()
            return cursor.rowcount > 0

    # --- App Rules CRUD ---
    def add_app_rule(self, rule: AppRule) -> int:
        proc_clean = rule.process_name.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO app_rules (app_name, process_name, is_blocked, path, category, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(process_name) DO UPDATE SET
                    app_name = excluded.app_name,
                    is_blocked = excluded.is_blocked,
                    path = excluded.path,
                    category = excluded.category
            """, (
                rule.app_name,
                proc_clean,
                1 if rule.is_blocked else 0,
                rule.path,
                rule.category,
                rule.created_at or datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid

    def get_app_rules(self, only_blocked: bool = False) -> List[AppRule]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM app_rules WHERE 1=1"
            if only_blocked:
                query += " AND is_blocked = 1"
            query += " ORDER BY app_name ASC"
            cursor.execute(query)
            rows = cursor.fetchall()
            return [
                AppRule(
                    id=row["id"],
                    app_name=row["app_name"],
                    process_name=row["process_name"],
                    is_blocked=bool(row["is_blocked"]),
                    path=row["path"],
                    category=row["category"],
                    created_at=row["created_at"]
                )
                for row in rows
            ]

    def remove_app_rule(self, process_or_name: str) -> bool:
        clean = process_or_name.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM app_rules WHERE lower(process_name) = ? OR lower(app_name) = ?", (clean, clean))
            conn.commit()
            return cursor.rowcount > 0

    def set_app_blocked_status(self, process_or_name: str, blocked: bool) -> bool:
        clean = process_or_name.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE app_rules SET is_blocked = ? WHERE lower(process_name) = ? OR lower(app_name) = ?", (1 if blocked else 0, clean, clean))
            conn.commit()
            return cursor.rowcount > 0

    # --- Schedule Rules CRUD ---
    def add_schedule_rule(self, rule: ScheduleRule) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO schedule_rules (name, days_of_week, start_time, end_time, mode, is_enabled, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                rule.name,
                rule.days_of_week,
                rule.start_time,
                rule.end_time,
                rule.mode,
                1 if rule.is_enabled else 0,
                rule.created_at or datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid

    def get_schedule_rules(self, only_enabled: bool = False) -> List[ScheduleRule]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM schedule_rules WHERE 1=1"
            if only_enabled:
                query += " AND is_enabled = 1"
            query += " ORDER BY start_time ASC"
            cursor.execute(query)
            rows = cursor.fetchall()
            return [
                ScheduleRule(
                    id=row["id"],
                    name=row["name"],
                    days_of_week=row["days_of_week"],
                    start_time=row["start_time"],
                    end_time=row["end_time"],
                    mode=row["mode"],
                    is_enabled=bool(row["is_enabled"]),
                    created_at=row["created_at"]
                )
                for row in rows
            ]

    def remove_schedule_rule(self, schedule_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM schedule_rules WHERE id = ?", (schedule_id,))
            conn.commit()
            return cursor.rowcount > 0

    def toggle_schedule_rule(self, schedule_id: int, enabled: bool) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE schedule_rules SET is_enabled = ? WHERE id = ?", (1 if enabled else 0, schedule_id))
            conn.commit()
            return cursor.rowcount > 0

    # --- Active Sessions (Timed Blocking) ---
    def create_session(self, session: ActiveSession) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO active_sessions (session_type, target, start_time, end_time, is_active, reason)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session.session_type,
                session.target,
                session.start_time,
                session.end_time,
                1 if session.is_active else 0,
                session.reason
            ))
            conn.commit()
            return cursor.lastrowid

    def get_active_sessions(self) -> List[ActiveSession]:
        now_iso = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM active_sessions 
                WHERE is_active = 1 AND end_time > ?
                ORDER BY end_time ASC
            """, (now_iso,))
            rows = cursor.fetchall()
            return [
                ActiveSession(
                    id=row["id"],
                    session_type=row["session_type"],
                    target=row["target"],
                    start_time=row["start_time"],
                    end_time=row["end_time"],
                    is_active=bool(row["is_active"]),
                    reason=row["reason"]
                )
                for row in rows
            ]

    def deactivate_expired_sessions(self) -> int:
        now_iso = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE active_sessions SET is_active = 0 WHERE is_active = 1 AND end_time <= ?", (now_iso,))
            conn.commit()
            return cursor.rowcount

    def end_all_active_sessions(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE active_sessions SET is_active = 0 WHERE is_active = 1")
            conn.commit()
            return cursor.rowcount

    # --- Settings ---
    def get_setting(self, key: str, default: str = "") -> str:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, str(value)))
            conn.commit()

    # --- Audit Log ---
    def log_event(self, event_type: str, target: str, details: str = "") -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (event_type, target, details, timestamp)
                VALUES (?, ?, ?, ?)
            """, (event_type, target, details, datetime.now().isoformat()))
            conn.commit()

    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
