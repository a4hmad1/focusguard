"""FocusGuard Background Enforcement Service.

Enforces blocking policies, countdown timers, and recurring schedules
autonomously as a headless daemon or service.
"""

import time
import signal
import sys
import logging
from focusguard.core.database import Database
from focusguard.engine.app_blocker import AppBlocker
from focusguard.engine.website_blocker import WebsiteBlocker
from focusguard.engine.scheduler import Scheduler

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("focusguard.service")

class FocusGuardService:
    def __init__(self):
        self.db = Database()
        self.app_blocker = AppBlocker(self.db)
        self.website_blocker = WebsiteBlocker(self.db)
        self.scheduler = Scheduler(self.db, self.app_blocker, self.website_blocker)
        self.running = False

    def start(self):
        logger.info("FocusGuard Background Service starting...")
        self.running = True

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        self.scheduler.start_background_loop(poll_interval=1.0)
        logger.info("FocusGuard Background Service is active.")

        while self.running:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break

        self.stop()

    def stop(self):
        logger.info("Stopping FocusGuard Background Service...")
        self.running = False
        self.scheduler.stop_background_loop()
        logger.info("FocusGuard Background Service stopped cleanly.")

    def _handle_signal(self, signum, frame):
        logger.info(f"Received signal {signum}; shutting down...")
        self.running = False

def run_service():
    srv = FocusGuardService()
    srv.start()

if __name__ == "__main__":
    run_service()
