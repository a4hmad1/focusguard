"""Duration parser and formatter for time-based blocking."""

import re
from datetime import timedelta
from typing import Optional

DURATION_REGEX = re.compile(
    r"""
    ^\s*
    (?:(?P<days>\d+)\s*(?:d|days?))?[\s,]*
    (?:(?P<hours>\d+)\s*(?:h|hours?|hrs?))?[\s,]*
    (?:(?P<minutes>\d+)\s*(?:m|mins?|minutes?))?[\s,]*
    (?:(?P<seconds>\d+)\s*(?:s|secs?|seconds?))?
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

def parse_duration(duration_str: str) -> Optional[timedelta]:
    """
    Parse a human-readable duration string into a datetime.timedelta.

    Supported formats:
    - '2h', '30m', '45s', '1d'
    - '1h30m', '2h 15m', '45 mins'
    - '90' (default is minutes if only a number)
    - '1:30' (hours:minutes)
    """
    if not duration_str or not isinstance(duration_str, str):
        return None

    duration_str = duration_str.strip()

    # Plain integer: treat as minutes
    if duration_str.isdigit():
        return timedelta(minutes=int(duration_str))

    # Colon format 'HH:MM' or 'HH:MM:SS'
    if ":" in duration_str:
        parts = duration_str.split(":")
        try:
            if len(parts) == 2:
                return timedelta(hours=int(parts[0]), minutes=int(parts[1]))
            elif len(parts) == 3:
                return timedelta(hours=int(parts[0]), minutes=int(parts[1]), seconds=int(parts[2]))
        except ValueError:
            return None

    match = DURATION_REGEX.match(duration_str)
    if not match:
        return None

    data = match.groupdict()
    days = int(data.get("days") or 0)
    hours = int(data.get("hours") or 0)
    minutes = int(data.get("minutes") or 0)
    seconds = int(data.get("seconds") or 0)

    total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
    if total_seconds == 0:
        return None

    return timedelta(seconds=total_seconds)

def format_duration(td: timedelta) -> str:
    """Format a timedelta into a human-readable string like '1h 30m'."""
    total_seconds = int(td.total_seconds())
    if total_seconds <= 0:
        return "0s"

    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 and not parts:  # only show seconds if less than a minute
        parts.append(f"{seconds}s")

    return " ".join(parts) if parts else "0m"

def format_time_remaining(seconds_remaining: float) -> str:
    """Format seconds into HH:MM:SS countdown format."""
    secs = max(0, int(seconds_remaining))
    hours = secs // 3600
    minutes = (secs % 3600) // 60
    seconds = secs % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"
