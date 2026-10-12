"""Time-Based Blocking and Recurring Schedule Engine.

Manages countdown sessions, automatic expiration and unblocking,
and recurring weekly schedule enforcement.
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from focusguard.core.database import Database
from focusguard.core.models import ActiveSession, ScheduleRule
from focusguard.engine.app_blocker import AppBlocker
from focusguard.engine.website_blocker import WebsiteBlocker

logger = logging.getLogger("focusguard.engine.scheduler")

DAY_MAP = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun"
}

class Scheduler:
    def __init__(
        self,
        db: Optional[Database] = None,
        app_blocker: Optional[AppBlocker] = None,
        website_blocker: Optional[WebsiteBlocker] = None
    ):
        self.db = db or Database()
        self.app_blocker = app_blocker or AppBlocker(self.db)
        self.website_blocker = website_blocker or WebsiteBlocker(self.db)
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.on_state_change: Optional[Callable[[Dict[str, Any]], None]] = None

    def start_timed_session(
        self,
        duration: timedelta,
        target: str = "all",
        session_type: str = "focus_mode",
        reason: str = "Timed focus session"
    ) -> int:
        """Start a new timed blocking session with a countdown."""
        now = datetime.now()
        end_time = now + duration

        session = ActiveSession(
            session_type=session_type,
            target=target,
            start_time=now.isoformat(),
            end_time=end_time.isoformat(),
            is_active=True,
            reason=reason
        )

        session_id = self.db.create_session(session)
        self.db.log_event("SESSION_START", target, f"Duration: {duration}, ID: {session_id}")

        # Enforce rules immediately
        self.enforce_current_state()
        return session_id

    def cancel_active_sessions(self) -> int:
        """Cancel all running timed sessions and restore access."""
        count = self.db.end_all_active_sessions()
        self.db.log_event("SESSION_CANCEL", "all", f"Cancelled {count} active sessions")
        self.enforce_current_state()
        return count

    def get_current_status(self) -> Dict[str, Any]:
        """
        Evaluate current state of timed sessions and recurring schedules.

        Returns detailed status including remaining time and active rules.
        """
        # Purge expired sessions
        expired_count = self.db.deactivate_expired_sessions()
        if expired_count > 0:
            logger.info(f"Deactivated {expired_count} expired session(s).")

        now = datetime.now()
        active_sessions = self.db.get_active_sessions()
        
        # Calculate maximum remaining seconds among active sessions
        max_remaining_seconds = 0.0
        for s in active_sessions:
            try:
                end_dt = datetime.fromisoformat(s.end_time)
                diff = (end_dt - now).total_seconds()
                if diff > max_remaining_seconds:
                    max_remaining_seconds = diff
            except Exception:
                continue

        # Check recurring schedules
        active_schedules = self._check_active_recurring_schedules(now)

        is_blocking_active = len(active_sessions) > 0 or len(active_schedules) > 0

        return {
            "is_blocking_active": is_blocking_active,
            "has_timed_session": len(active_sessions) > 0,
            "has_active_schedule": len(active_schedules) > 0,
            "remaining_seconds": max_remaining_seconds,
            "active_sessions": [s.__dict__ for s in active_sessions],
            "active_schedules": [s.__dict__ for s in active_schedules],
            "mode": self.website_blocker.get_mode(),
            "timestamp": now.isoformat()
        }

    def _check_active_recurring_schedules(self, now: datetime) -> List[ScheduleRule]:
        """Check if current time matches any enabled recurring schedule."""
        today_abbr = DAY_MAP[now.weekday()]
        current_time_str = now.strftime("%H:%M")

        matching = []
        rules = self.db.get_schedule_rules(only_enabled=True)
        for r in rules:
            days = [d.strip() for d in r.days_of_week.split(",")]
            if today_abbr in days:
                if r.start_time <= current_time_str <= r.end_time:
                    matching.append(r)

        return matching

    def enforce_current_state(self) -> None:
        """Apply or lift website and application restrictions based on current state."""
        status = self.get_current_status()
        if status["is_blocking_active"]:
            try:
                self.website_blocker.sync_rules()
            except PermissionError:
                pass
            self.app_blocker.check_and_enforce()
        else:
            try:
                self.website_blocker.unblock_all()
            except PermissionError:
                pass

        if self.on_state_change:
            self.on_state_change(status)

    def start_background_loop(self, poll_interval: float = 1.0) -> None:
        """Start background loop for real-time schedule and countdown tracking."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._loop, args=(poll_interval,), daemon=True)
        self._thread.start()
        logger.info("Scheduler background loop started.")

    def stop_background_loop(self) -> None:
        """Stop the scheduler background loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            logger.info("Scheduler background loop stopped.")

    def _loop(self, interval: float) -> None:
        while self._running:
            try:
                self.enforce_current_state()
            except Exception as e:
                logger.error(f"Error in scheduler tick: {e}")
            time.sleep(interval)
