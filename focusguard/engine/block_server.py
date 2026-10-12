"""Embedded Local HTTP Block Page Server.

Runs a local web server that serves the "Access Blocked" landing page
when a user accesses a restricted website redirected via hosts or proxy.
"""

import http.server
import socketserver
import threading
import logging
from pathlib import Path
from typing import Optional
from focusguard.core.config import DEFAULT_BLOCK_HOST, DEFAULT_BLOCK_PORT

logger = logging.getLogger("focusguard.engine.block_server")

HTML_TEMPLATE_PATH = Path(__file__).parent.parent / "resources" / "block_page" / "index.html"

class BlockHTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Health check endpoint
        if self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "service": "focusguard-blocker"}')
            return

        # Serve the block page HTML for all other requests
        content = b""
        if HTML_TEMPLATE_PATH.exists():
            with open(HTML_TEMPLATE_PATH, "rb") as f:
                content = f.read()
        else:
            content = b"<html><body><h1>FocusGuard - Access Blocked</h1><p>This site is restricted during focus hours.</p></body></html>"

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        # Suppress standard noisy access logging
        pass

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

class BlockPageServer:
    def __init__(self, host: str = DEFAULT_BLOCK_HOST, port: int = DEFAULT_BLOCK_PORT):
        self.host = host
        self.port = port
        self.server: Optional[ReusableTCPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.is_running = False

    def start(self) -> bool:
        """Start the block page server in a background daemon thread."""
        if self.is_running:
            return True

        try:
            self.server = ReusableTCPServer((self.host, self.port), BlockHTTPHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            self.is_running = True
            logger.info(f"Block page server running on http://{self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start block page server on {self.host}:{self.port}: {e}")
            self.is_running = False
            return False

    def stop(self) -> None:
        """Stop the block page server."""
        if self.server and self.is_running:
            self.server.shutdown()
            self.server.server_close()
            self.is_running = False
            logger.info("Block page server stopped.")
