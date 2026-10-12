"""Process Monitoring and Application Enforcement Engine.

Identifies running instances of blocked applications and terminates them,
while ensuring critical system processes are safeguarded.
"""

import time
import logging
import psutil
from typing import List, Set, Dict, Optional, Callable
from focusguard.core.safety import is_critical_process, normalize_process_name
from focusguard.core.database import Database

logger = logging.getLogger("focusguard.engine.app_blocker")

class AppBlocker:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()
        self.on_process_blocked_callback: Optional[Callable[[str, int], None]] = None

    def get_blocked_process_names(self) -> Set[str]:
        """Fetch all currently blocked application process names from database."""
        rules = self.db.get_app_rules(only_blocked=True)
        blocked_names = set()
        for r in rules:
            proc_clean = normalize_process_name(r.process_name)
            if proc_clean:
                blocked_names.add(proc_clean)
                # If Windows .exe or without .exe, add both variants
                if proc_clean.endswith(".exe"):
                    blocked_names.add(proc_clean[:-4])
                else:
                    blocked_names.add(f"{proc_clean}.exe")
        return blocked_names

    def check_and_enforce(self) -> List[Dict[str, str]]:
        """
        Scan all running processes and terminate any that are blocked.

        Returns a list of terminated processes metadata.
        """
        blocked_names = self.get_blocked_process_names()
        if not blocked_names:
            return []

        terminated = []
        for proc in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
            try:
                pid = proc.info["pid"]
                pname = proc.info["name"] or ""
                clean_name = normalize_process_name(pname)
                name_no_ext = clean_name[:-4] if clean_name.endswith(".exe") else clean_name

                # Safety check first: never terminate critical system processes
                if is_critical_process(clean_name, pid=pid):
                    continue

                # Check if process name or executable matches blocked list
                if clean_name in blocked_names or name_no_ext in blocked_names:
                    # Terminate process
                    self._terminate_process(proc, clean_name, pid)
                    terminated.append({"name": pname, "pid": str(pid)})
                    
                    # Log event to database
                    self.db.log_event("APP_BLOCKED", pname, f"Terminated PID {pid}")
                    
                    if self.on_process_blocked_callback:
                        self.on_process_blocked_callback(pname, pid)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                logger.error(f"Error checking process: {e}")

        return terminated

    def _terminate_process(self, proc: psutil.Process, name: str, pid: int) -> None:
        """Attempt graceful termination, then force kill if needed."""
        try:
            logger.info(f"Terminating blocked application: {name} (PID: {pid})")
            proc.terminate()
            # Give short grace period for clean shutdown
            try:
                proc.wait(timeout=1.0)
            except psutil.TimeoutExpired:
                # Force kill if still running
                logger.warning(f"Process {name} (PID: {pid}) did not exit gracefully; force killing.")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def is_process_running(self, process_name: str) -> bool:
        """Check if any instance of a process is currently running."""
        clean_target = normalize_process_name(process_name)
        target_no_ext = clean_target[:-4] if clean_target.endswith(".exe") else clean_target
        for proc in psutil.process_iter(["name"]):
            try:
                pname = normalize_process_name(proc.info["name"] or "")
                name_no_ext = pname[:-4] if pname.endswith(".exe") else pname
                if pname == clean_target or name_no_ext == target_no_ext:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
