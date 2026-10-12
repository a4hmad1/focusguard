"""FocusGuard Core Package."""

from focusguard.core.config import APP_NAME, APP_VERSION, APP_DESCRIPTION
from focusguard.core.models import WebsiteRule, AppRule, ScheduleRule, ActiveSession, AppSettings
from focusguard.core.database import Database
from focusguard.core.safety import is_critical_process
from focusguard.core.duration import parse_duration, format_duration

__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "APP_DESCRIPTION",
    "WebsiteRule",
    "AppRule",
    "ScheduleRule",
    "ActiveSession",
    "AppSettings",
    "Database",
    "is_critical_process",
    "parse_duration",
    "format_duration",
]
