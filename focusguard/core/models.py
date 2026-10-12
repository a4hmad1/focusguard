"""Data models for FocusGuard rules, sessions, and schedules."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import urllib.parse
import re

@dataclass
class WebsiteRule:
    id: Optional[int] = None
    url: str = ""
    domain: str = ""
    rule_type: str = "blacklist"  # "whitelist" or "blacklist"
    is_active: bool = True
    category: str = "General"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @staticmethod
    def extract_domain(raw_url: str) -> str:
        """Extract clean domain name from URL or raw domain string."""
        raw = raw_url.strip().lower()
        if not raw:
            return ""

        # Remove protocol if present
        if "://" in raw:
            parsed = urllib.parse.urlparse(raw)
            raw = parsed.netloc

        # Remove port if present
        if ":" in raw:
            raw = raw.split(":")[0]

        # Remove trailing path/query
        raw = raw.split("/")[0]

        # Strip www. prefix for consistent matching
        if raw.startswith("www."):
            raw = raw[4:]

        return raw.strip()

@dataclass
class AppRule:
    id: Optional[int] = None
    app_name: str = ""
    process_name: str = ""
    is_blocked: bool = True
    path: Optional[str] = None
    category: str = "General"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ScheduleRule:
    id: Optional[int] = None
    name: str = "Study Schedule"
    days_of_week: str = "Mon,Tue,Wed,Thu,Fri"  # Comma separated: Mon,Tue,Wed,Thu,Fri,Sat,Sun
    start_time: str = "09:00"  # HH:MM (24h)
    end_time: str = "17:00"    # HH:MM (24h)
    mode: str = "blacklist"    # "whitelist" or "blacklist"
    is_enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ActiveSession:
    id: Optional[int] = None
    session_type: str = "focus_mode"  # "focus_mode", "app_timed", "site_timed"
    target: str = "all"               # "all", app process name, or domain
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: str = ""                # ISO format timestamp
    is_active: bool = True
    reason: str = "Timed focus session"

@dataclass
class AppSettings:
    mode: str = "blacklist"           # "blacklist" or "whitelist"
    auto_start_on_boot: bool = False
    emergency_pin: str = "0000"
    block_port: int = 8880
    theme: str = "dark"
