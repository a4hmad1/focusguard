"""Tests for embedded BlockPageServer."""

import urllib.request
import time
from focusguard.engine.block_server import BlockPageServer

def test_block_server_health():
    # Use high port for testing to avoid conflicts
    server = BlockPageServer(host="127.0.0.1", port=18888)
    started = server.start()
    assert started is True
    time.sleep(0.3)

    try:
        # Check health endpoint
        req = urllib.request.Request("http://127.0.0.1:18888/api/health")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            assert resp.status == 200
            data = resp.read()
            assert b"focusguard-blocker" in data

        # Check block page HTML
        req_page = urllib.request.Request("http://127.0.0.1:18888/some-blocked-url")
        with urllib.request.urlopen(req_page, timeout=2.0) as resp:
            assert resp.status == 200
            page_data = resp.read().decode("utf-8")
            assert "FocusGuard" in page_data
            assert "Access Blocked" in page_data
    finally:
        server.stop()
