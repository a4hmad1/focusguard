"""Tests for SQLite database operations and models."""

import pytest
from datetime import datetime, timedelta
from focusguard.core.database import Database
from focusguard.core.models import WebsiteRule, AppRule, ScheduleRule, ActiveSession

@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_focusguard.db"
    return Database(db_file)

def test_website_rules_crud(test_db):
    rule = WebsiteRule(
        url="https://youtube.com/watch?v=123",
        domain="youtube.com",
        rule_type="blacklist",
        category="Entertainment"
    )
    rule_id = test_db.add_website_rule(rule)
    assert rule_id is not None

    rules = test_db.get_website_rules(rule_type="blacklist")
    assert len(rules) == 1
    assert rules[0].domain == "youtube.com"
    assert rules[0].is_active is True

    # Toggle
    test_db.toggle_website_rule("youtube.com", False)
    rules = test_db.get_website_rules()
    assert rules[0].is_active is False

    # Remove
    test_db.remove_website_rule("youtube.com")
    assert len(test_db.get_website_rules()) == 0

def test_extract_domain():
    assert WebsiteRule.extract_domain("https://www.reddit.com/r/python") == "reddit.com"
    assert WebsiteRule.extract_domain("http://github.com:8080/path") == "github.com"
    assert WebsiteRule.extract_domain("docs.python.org") == "docs.python.org"
    assert WebsiteRule.extract_domain("WWW.EXAMPLE.COM") == "example.com"

def test_app_rules_crud(test_db):
    app = AppRule(app_name="Discord", process_name="discord", is_blocked=True, category="Social")
    test_db.add_app_rule(app)

    rules = test_db.get_app_rules(only_blocked=True)
    assert len(rules) == 1
    assert rules[0].process_name == "discord"

    test_db.set_app_blocked_status("discord", False)
    assert len(test_db.get_app_rules(only_blocked=True)) == 0

    test_db.remove_app_rule("discord")
    assert len(test_db.get_app_rules()) == 0

def test_schedule_rules(test_db):
    sched = ScheduleRule(
        name="Study Hours",
        days_of_week="Mon,Tue,Wed",
        start_time="09:00",
        end_time="12:00",
        mode="blacklist"
    )
    s_id = test_db.add_schedule_rule(sched)
    assert s_id is not None

    schedules = test_db.get_schedule_rules(only_enabled=True)
    assert len(schedules) == 1
    assert schedules[0].name == "Study Hours"

    test_db.toggle_schedule_rule(s_id, False)
    assert len(test_db.get_schedule_rules(only_enabled=True)) == 0

def test_active_sessions_expiration(test_db):
    now = datetime.now()
    # Expired session
    s_expired = ActiveSession(
        session_type="focus_mode",
        target="all",
        start_time=(now - timedelta(hours=2)).isoformat(),
        end_time=(now - timedelta(hours=1)).isoformat(),
        is_active=True
    )
    # Active session
    s_active = ActiveSession(
        session_type="focus_mode",
        target="all",
        start_time=now.isoformat(),
        end_time=(now + timedelta(hours=1)).isoformat(),
        is_active=True
    )

    test_db.create_session(s_expired)
    test_db.create_session(s_active)

    active_before = test_db.get_active_sessions()
    assert len(active_before) == 1  # get_active_sessions filters end_time > now

    expired_count = test_db.deactivate_expired_sessions()
    assert expired_count == 1
