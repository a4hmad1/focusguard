"""Tests for Default-Deny URL Whitelist Enforcement and Theme Stylesheets."""

import pytest
from focusguard.core.database import Database
from focusguard.core.models import WebsiteRule
from focusguard.engine.website_blocker import WebsiteBlocker
from focusguard.engine.proxy_manager import SystemProxyManager
from focusguard.gui.theme import get_theme_stylesheet, FORMAL_LIGHT_THEME_QSS, FORMAL_DARK_THEME_QSS

@pytest.fixture
def blocker_env(tmp_path):
    db_file = tmp_path / "whitelist_test.db"
    db = Database(db_file)
    blocker = WebsiteBlocker(db=db)
    return blocker, db

def test_whitelist_allows_only_saved_urls(blocker_env):
    blocker, db = blocker_env
    blocker.set_mode("whitelist")

    # Save approved URLs
    db.add_website_rule(WebsiteRule(url="https://canvas.edu", domain="canvas.edu", rule_type="whitelist"))
    db.add_website_rule(WebsiteRule(url="https://wikipedia.org", domain="wikipedia.org", rule_type="whitelist"))

    # Saved URLs must be allowed
    assert blocker.is_url_allowed("canvas.edu") is True
    assert blocker.is_url_allowed("https://canvas.edu/courses") is True
    assert blocker.is_url_allowed("sub.canvas.edu") is True
    assert blocker.is_url_allowed("https://en.wikipedia.org/wiki/Main_Page") is True

    # ALL other websites on the internet must be BLOCKED
    assert blocker.is_url_allowed("google.com") is False
    assert blocker.is_url_allowed("youtube.com") is False
    assert blocker.is_url_allowed("reddit.com") is False
    assert blocker.is_url_allowed("tiktok.com") is False
    assert blocker.is_url_allowed("random-news-portal.org") is False

def test_blacklist_mode_behavior(blocker_env):
    blocker, db = blocker_env
    blocker.set_mode("blacklist")

    # Blacklist a specific distraction
    db.add_website_rule(WebsiteRule(url="https://distraction.com", domain="distraction.com", rule_type="blacklist"))

    # Explicitly blacklisted domain is blocked
    assert blocker.is_url_allowed("distraction.com") is False
    assert blocker.is_url_allowed("https://sub.distraction.com") is False

    # Unlisted sites remain allowed in blacklist mode
    assert blocker.is_url_allowed("google.com") is True
    assert blocker.is_url_allowed("wikipedia.org") is True

def test_theme_stylesheets():
    light = get_theme_stylesheet("white")
    assert light == FORMAL_LIGHT_THEME_QSS
    assert "#ffffff" in light

    dark = get_theme_stylesheet("black")
    assert dark == FORMAL_DARK_THEME_QSS
    assert "#0d1117" in dark

def test_proxy_manager_instantiation():
    pm = SystemProxyManager()
    assert pm.pac_url.endswith("/proxy.pac")
    # Disabling should not throw errors
    assert pm.disable_proxy() is True
