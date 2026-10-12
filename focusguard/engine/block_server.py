"""Embedded Local HTTP Block Page Server and Dynamic PAC Provider.

Serves the "Access Blocked" landing page when a restricted website is requested,
generates the dynamic PAC script for default-deny URL whitelisting across browsers,
and handles proxy traffic.
"""

import http.server
import socketserver
import threading
import logging
import urllib.parse
from pathlib import Path
from typing import Optional, List
from focusguard.core.config import DEFAULT_BLOCK_HOST, DEFAULT_BLOCK_PORT
from focusguard.core.database import Database

logger = logging.getLogger("focusguard.engine.block_server")

HTML_TEMPLATE_PATH = Path(__file__).parent.parent / "resources" / "block_page" / "index.html"

class BlockHTTPHandler(http.server.BaseHTTPRequestHandler):
    db: Optional[Database] = None

    def do_CONNECT(self):
        """Handle HTTPS proxy tunneling for blocked domains by refusing access."""
        # Send 403 Forbidden to block HTTPS connection to non-whitelisted destinations
        try:
            blocked_msg = (
                b"HTTP/1.1 403 Forbidden\r\n"
                b"Content-Type: text/html; charset=utf-8\r\n"
                b"Connection: close\r\n\r\n"
                b"<!DOCTYPE html><html><head><title>FocusGuard - Blocked</title></head>"
                b"<body style='font-family:sans-serif;text-align:center;padding:50px;background:#0f172a;color:#fff;'>"
                b"<h1>Access Blocked by FocusGuard</h1>"
                b"<p>This website is restricted. Only approved whitelisted URLs are accessible during focus mode.</p>"
                b"</body></html>"
            )
            self.wfile.write(blocked_msg)
        except Exception:
            pass

    def do_GET(self):
        # 1. Health check endpoint
        if self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "service": "focusguard-blocker"}')
            return

        # 2. Dynamic PAC (Proxy Auto-Configuration) endpoint
        if self.path == "/proxy.pac":
            pac_content = self._generate_pac_script()
            pac_bytes = pac_content.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ns-proxy-autoconfig")
            self.send_header("Content-Length", str(len(pac_bytes)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(pac_bytes)
            return

        # 3. Serve the "Access Blocked" landing page
        raw_host = self.headers.get("Host", "Restricted URL")
        content = self._get_rendered_block_page(raw_host)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(content)

    def _generate_pac_script(self) -> str:
        """
        Dynamically generate PAC script that enforces strict default-deny whitelist:
        ALL URLs in all browsers are blocked EXCEPT explicitly approved saved URLs.
        """
        db = BlockHTTPHandler.db or Database()
        mode = db.get_setting("blocking_mode", default="whitelist")

        if mode == "whitelist":
            # Fetch explicitly whitelisted domains
            rules = db.get_website_rules(rule_type="whitelist", only_active=True)
            whitelisted_domains = [r.domain.lower() for r in rules if r.domain]

            # Format JavaScript array of allowed domains
            domains_js_array = ",\n        ".join(f'"{d}"' for d in whitelisted_domains)

            return f"""function FindProxyForURL(url, host) {{
    if (!host) return "DIRECT";
    var lHost = host.toLowerCase();

    // Allow localhost and local LAN
    if (isPlainHostName(lHost) ||
        shExpMatch(lHost, "127.*") ||
        shExpMatch(lHost, "10.*") ||
        shExpMatch(lHost, "192.168.*") ||
        shExpMatch(lHost, "172.16.*") ||
        lHost === "localhost" ||
        lHost === "::1") {{
        return "DIRECT";
    }}

    // Whitelisted / Saved URLs that are permitted to open
    var allowedDomains = [
        {domains_js_array}
    ];

    for (var i = 0; i < allowedDomains.length; i++) {{
        var d = allowedDomains[i];
        if (lHost === d || dnsDomainIs(lHost, "." + d) || shExpMatch(lHost, "*." + d)) {{
            return "DIRECT";
        }}
    }}

    // ALL OTHER URLS ARE BLOCKED - Route to FocusGuard block server
    return "PROXY {DEFAULT_BLOCK_HOST}:{DEFAULT_BLOCK_PORT}";
}}
"""
        else:
            # Blacklist mode: only block specific blacklisted domains
            rules = db.get_website_rules(rule_type="blacklist", only_active=True)
            blocked_domains = [r.domain.lower() for r in rules if r.domain]
            domains_js_array = ",\n        ".join(f'"{d}"' for d in blocked_domains)

            return f"""function FindProxyForURL(url, host) {{
    if (!host) return "DIRECT";
    var lHost = host.toLowerCase();

    var blockedDomains = [
        {domains_js_array}
    ];

    for (var i = 0; i < blockedDomains.length; i++) {{
        var d = blockedDomains[i];
        if (lHost === d || dnsDomainIs(lHost, "." + d) || shExpMatch(lHost, "*." + d)) {{
            return "PROXY {DEFAULT_BLOCK_HOST}:{DEFAULT_BLOCK_PORT}";
        }}
    }}

    return "DIRECT";
}}
"""

    def _get_rendered_block_page(self, host: str) -> bytes:
        if HTML_TEMPLATE_PATH.exists():
            with open(HTML_TEMPLATE_PATH, "r", encoding="utf-8") as f:
                html = f.read()
            html = html.replace("Protected Destination", host)
            return html.encode("utf-8")
        return b"<html><body><h1>FocusGuard - Access Blocked</h1><p>Only approved websites are accessible.</p></body></html>"

    def log_message(self, format, *args):
        # Suppress noisy standard request log messages
        pass

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class BlockPageServer:
    def __init__(self, host: str = DEFAULT_BLOCK_HOST, port: int = DEFAULT_BLOCK_PORT, db: Optional[Database] = None):
        self.host = host
        self.port = port
        self.db = db or Database()
        BlockHTTPHandler.db = self.db
        self.server: Optional[ReusableTCPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.is_running = False

    def start(self) -> bool:
        """Start the block page & PAC server in a background daemon thread."""
        if self.is_running:
            return True

        try:
            BlockHTTPHandler.db = self.db
            self.server = ReusableTCPServer((self.host, self.port), BlockHTTPHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            self.is_running = True
            logger.info(f"Block server & PAC running on http://{self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start block server on {self.host}:{self.port}: {e}")
            self.is_running = False
            return False

    def stop(self) -> None:
        """Stop the block server."""
        if self.server and self.is_running:
            self.server.shutdown()
            self.server.server_close()
            self.is_running = False
            logger.info("Block server stopped.")
