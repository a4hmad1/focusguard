"""Operating System Safety Protection Module.

Ensures that essential system processes, desktop managers, display servers,
and critical services cannot be blocked or terminated by FocusGuard.
"""

import os
import sys
from typing import Set

# Core Linux processes that must NEVER be terminated or blocked
CRITICAL_LINUX_PROCESSES: Set[str] = {
    "systemd",
    "init",
    "kthreadd",
    "dbus-daemon",
    "dbus-broker",
    "xorg",
    "xwayland",
    "wayland",
    "gnome-shell",
    "gnome-session",
    "gnome-session-binary",
    "kwin",
    "kwin_x11",
    "kwin_wayland",
    "plasmashell",
    "mutter",
    "sway",
    "hyprland",
    "xfwm4",
    "xfce4-session",
    "bash",
    "zsh",
    "sh",
    "sudo",
    "sshd",
    "polkitd",
    "pipewire",
    "pulseaudio",
    "wireplumber",
    "networkmanager",
    "wpa_supplicant",
    "udevd",
    "systemd-udevd",
    "systemd-journald",
    "systemd-logind",
    "systemd-resolved",
    "focusguard",
    "python",
    "python3",
    "login",
    "cron",
    "crond",
    "cupsd",
    "agetty",
}

# Core Windows processes that must NEVER be terminated or blocked
CRITICAL_WINDOWS_PROCESSES: Set[str] = {
    "system",
    "system idle process",
    "registry",
    "smss.exe",
    "csrss.exe",
    "wininit.exe",
    "services.exe",
    "lsass.exe",
    "svchost.exe",
    "fontdrvhost.exe",
    "winlogon.exe",
    "dwm.exe",
    "explorer.exe",
    "taskhostw.exe",
    "sihost.exe",
    "conhost.exe",
    "ctfmon.exe",
    "searchhost.exe",
    "shellexperiencehost.exe",
    "startmenuexperiencehost.exe",
    "runtimebroker.exe",
    "focusguard.exe",
    "python.exe",
    "pythonw.exe",
}

def normalize_process_name(name: str) -> str:
    """Normalize process name by converting to lower case and stripping path."""
    if not name:
        return ""
    # Support both Windows and Unix path separators
    normalized_path = name.replace("\\", "/")
    base = os.path.basename(normalized_path).lower()
    return base

def is_critical_process(process_name: str, pid: int = -1) -> bool:
    """
    Check if a process is a critical system process that must be protected.

    Args:
        process_name: The name or executable path of the process.
        pid: The process ID (optional). PIDs <= 1 on Linux are always critical.

    Returns:
        True if the process is protected, False otherwise.
    """
    if pid in (0, 1):
        return True

    # If it's our own process
    if pid == os.getpid():
        return True

    clean_name = normalize_process_name(process_name)
    name_no_ext = clean_name[:-4] if clean_name.endswith(".exe") else clean_name

    # Check Linux critical list
    if clean_name in CRITICAL_LINUX_PROCESSES or name_no_ext in CRITICAL_LINUX_PROCESSES:
        return True

    # Check Windows critical list
    if clean_name in CRITICAL_WINDOWS_PROCESSES or f"{clean_name}.exe" in CRITICAL_WINDOWS_PROCESSES:
        return True

    # Also check if it starts with focusguard
    if clean_name.startswith("focusguard"):
        return True

    return False
