"""Tests for embedded BlockPageServer and dynamic PAC generation."""

import urllib.request
import time
from focusguard.engine.block_server import BlockPageServer
from focusguard.core.database import Database
from focusguard.core.models import WebsiteRule

def test_block_server_health_and_pac(tmp_path):
    db_path = tmp_path / "pac_test.db"
    db = Database(db_path)
    
    # Add a whitelisted URL
    db.add_website_rule(WebsiteRule(url="https://canvas.edu", domain="canvas.edu", rule_type="whitelist"))

    server = BlockPageServer(host="127.0.0.1", port=18890, db=db)
    started = server.start()
    assert started is True
    time.sleep(0.3)

    try:
        # Check health endpoint
        req = urllib.request.Request("http://127.0.0.1:18890/api/health")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            assert resp.status == 200
            data = resp.read()
            assert b"focusguard-blocker" in data

        # Check PAC script generation
        req_pac = urllib.request.Request("http://127.0.0.1:18890/proxy.pac")
        with urllib.request.urlopen(req_pac, timeout=2.0) as resp:
            assert resp.status == 200
            pac_text = resp.read().decode("utf-8")
            assert "FindProxyForURL" in pac_text
            assert "canvas.edu" in pac_text
            assert "PROXY 127.0.0.1:8880" in pac_text

        # Check block page HTML
        req_page = urllib.request.Request("http://127.0.0.1:18890/some-blocked-url")
        with urllib.request.urlopen(req_page, timeout=2.0) as resp:
            assert resp.status == 200
            page_data = resp.read().decode("utf-8")
            assert "FocusGuard" in page_data
            assert "Access Blocked" in page_data
    finally:
        server.stop()
