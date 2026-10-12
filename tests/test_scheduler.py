"""Tests for timed session scheduler and recurring cron logic."""

import pytest
from datetime import datetime, timedelta
from focusguard.core.database import Database
from focusguard.core.models import ScheduleRule
from focusguard.engine.scheduler import Scheduler, DAY_MAP

@pytest.fixture
def scheduler_setup(tmp_path):
    db_file = tmp_path / "sched_test.db"
    db = Database(db_file)
    scheduler = Scheduler(db=db)
    return scheduler, db

def test_start_timed_session(scheduler_setup):
    scheduler, db = scheduler_setup

    s_id = scheduler.start_timed_session(timedelta(hours=2), reason="Study test")
    assert s_id is not None

    status = scheduler.get_current_status()
    assert status["is_blocking_active"] is True
    assert status["has_timed_session"] is True
    assert status["remaining_seconds"] > 7000  # approximately 7200 seconds

def test_cancel_active_sessions(scheduler_setup):
    scheduler, db = scheduler_setup
    scheduler.start_timed_session(timedelta(hours=1))

    cancelled = scheduler.cancel_active_sessions()
    assert cancelled == 1

    status = scheduler.get_current_status()
    assert status["is_blocking_active"] is False

def test_recurring_schedule_matching(scheduler_setup):
    scheduler, db = scheduler_setup
    now = datetime.now()
    today_abbr = DAY_MAP[now.weekday()]

    # Create schedule matching today and surrounding current hour
    s_hour = (now - timedelta(hours=1)).strftime("%H:%M")
    e_hour = (now + timedelta(hours=1)).strftime("%H:%M")

    rule = ScheduleRule(
        name="Current Window Schedule",
        days_of_week=today_abbr,
        start_time=s_hour,
        end_time=e_hour,
        is_enabled=True
    )
    db.add_schedule_rule(rule)

    matching = scheduler._check_active_recurring_schedules(now)
    assert len(matching) == 1
    assert matching[0].name == "Current Window Schedule"

    status = scheduler.get_current_status()
    assert status["is_blocking_active"] is True
    assert status["has_active_schedule"] is True
