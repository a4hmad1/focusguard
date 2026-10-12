"""FocusGuard Core Configuration and System Paths."""

import os
import sys
import platform
from pathlib import Path

APP_NAME = "FocusGuard"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Cross-Platform Website and Application Blocking Desktop Software"

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"

def get_app_dir() -> Path:
    """Returns the application data directory depending on OS."""
    if IS_WINDOWS:
        app_data = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or str(Path.home())
        base_dir = Path(app_data) / APP_NAME
    else:
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            base_dir = Path(xdg_config) / "focusguard"
        else:
            base_dir = Path.home() / ".config" / "focusguard"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

def get_db_path() -> Path:
    """Returns the SQLite database path."""
    return get_app_dir() / "focusguard.db"

def get_hosts_path() -> Path:
    """Returns the system hosts file path."""
    if IS_WINDOWS:
        system_root = os.environ.get("SystemRoot", "C:\\Windows")
        return Path(system_root) / "System32" / "drivers" / "etc" / "hosts"
    return Path("/etc/hosts")

def get_hosts_backup_path() -> Path:
    """Returns the hosts backup file path."""
    return get_app_dir() / "hosts.focusguard.bak"

def is_admin() -> bool:
    """Check if the current process is running with administrative/root privileges."""
    try:
        if IS_WINDOWS:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        return os.geteuid() == 0
    except Exception:
        return False

# Server settings
DEFAULT_BLOCK_PORT = 8880
DEFAULT_BLOCK_HOST = "127.0.0.1"

# Safety and Recovery
DEFAULT_RECOVERY_PIN = "0000"
RECOVERY_DELAY_SECONDS = 30
