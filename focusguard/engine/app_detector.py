"""Application and Running Process Detection Engine.

Discovers installed desktop applications on Linux and Windows,
and monitors running system processes.
"""

import os
import sys
import glob
import re
import psutil
from typing import List, Dict, Any, Optional
from focusguard.core.config import IS_LINUX, IS_WINDOWS
from focusguard.core.safety import is_critical_process, normalize_process_name

class InstalledApp:
    def __init__(
        self,
        name: str,
        exec_name: str,
        exec_path: Optional[str] = None,
        icon: Optional[str] = None,
        category: str = "General",
        is_running: bool = False,
        pids: Optional[List[int]] = None
    ):
        self.name = name
        self.exec_name = exec_name
        self.exec_path = exec_path
        self.icon = icon
        self.category = category
        self.is_running = is_running
        self.pids = pids or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "exec_name": self.exec_name,
            "exec_path": self.exec_path,
            "icon": self.icon,
            "category": self.category,
            "is_running": self.is_running,
            "pids": self.pids,
            "is_critical": is_critical_process(self.exec_name)
        }

class AppDetector:
    def __init__(self):
        pass

    def get_installed_applications(self) -> List[InstalledApp]:
        """Detect installed applications on the system."""
        if IS_LINUX:
            return self._scan_linux_applications()
        elif IS_WINDOWS:
            return self._scan_windows_applications()
        else:
            return self._scan_fallback_applications()

    def _scan_linux_applications(self) -> List[InstalledApp]:
        """Parse Linux .desktop files in standard XDG directories."""
        app_dirs = [
            "/usr/share/applications",
            "/usr/local/share/applications",
            os.path.expanduser("~/.local/share/applications"),
            "/var/lib/snapd/desktop/applications",
            "/var/lib/flatpak/exports/share/applications",
            os.path.expanduser("~/.local/share/flatpak/exports/share/applications"),
        ]

        seen_execs = set()
        apps: List[InstalledApp] = []

        for folder in app_dirs:
            if not os.path.exists(folder):
                continue
            for desktop_file in glob.glob(os.path.join(folder, "*.desktop")):
                try:
                    app = self._parse_desktop_file(desktop_file)
                    if app and app.exec_name and app.exec_name.lower() not in seen_execs:
                        seen_execs.add(app.exec_name.lower())
                        apps.append(app)
                except Exception:
                    continue

        return sorted(apps, key=lambda a: a.name.lower())

    def _parse_desktop_file(self, file_path: str) -> Optional[InstalledApp]:
        """Parse a single Linux .desktop file."""
        name = None
        exec_cmd = None
        icon = None
        categories = "General"
        no_display = False

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            in_main_section = False
            for line in f:
                line = line.strip()
                if line == "[Desktop Entry]":
                    in_main_section = True
                    continue
                elif line.startswith("[") and line.endswith("]"):
                    in_main_section = False
                    continue

                if in_main_section:
                    if line.startswith("Name=") and not name:
                        name = line.split("=", 1)[1].strip()
                    elif line.startswith("Exec=") and not exec_cmd:
                        exec_raw = line.split("=", 1)[1].strip()
                        # Remove field codes like %u, %F, %U
                        exec_clean = re.sub(r"%[a-zA-Z]", "", exec_raw).strip()
                        exec_cmd = exec_clean.split()[0] if exec_clean else None
                    elif line.startswith("Icon=") and not icon:
                        icon = line.split("=", 1)[1].strip()
                    elif line.startswith("Categories="):
                        cat_raw = line.split("=", 1)[1].strip()
                        categories = cat_raw.split(";")[0] if cat_raw else "General"
                    elif line.lower() == "nodisplay=true":
                        no_display = True

        if no_display or not name or not exec_cmd:
            return None

        clean_exec = os.path.basename(exec_cmd)
        return InstalledApp(
            name=name,
            exec_name=clean_exec,
            exec_path=exec_cmd if os.path.isabs(exec_cmd) else None,
            icon=icon,
            category=categories
        )

    def _scan_windows_applications(self) -> List[InstalledApp]:
        """Scan Windows registry and Start Menu for installed applications."""
        apps: List[InstalledApp] = []
        seen = set()

        try:
            import winreg
            uninstall_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
            ]

            for hkey, subkey_path in uninstall_paths:
                try:
                    with winreg.OpenKey(hkey, subkey_path) as key:
                        subkeys_count = winreg.QueryInfoKey(key)[0]
                        for i in range(subkeys_count):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as app_key:
                                    try:
                                        display_name = winreg.QueryValueEx(app_key, "DisplayName")[0]
                                    except OSError:
                                        continue

                                    install_loc = ""
                                    try:
                                        install_loc = winreg.QueryValueEx(app_key, "InstallLocation")[0]
                                    except OSError:
                                        pass

                                    display_icon = ""
                                    try:
                                        display_icon = winreg.QueryValueEx(app_key, "DisplayIcon")[0]
                                    except OSError:
                                        pass

                                    # Try to deduce executable
                                    exec_candidate = display_name.lower().replace(" ", "")
                                    if display_icon and display_icon.lower().endswith(".exe"):
                                        exec_candidate = os.path.basename(display_icon.split(",")[0])
                                    elif not exec_candidate.endswith(".exe"):
                                        exec_candidate = f"{exec_candidate}.exe"

                                    if display_name and display_name.lower() not in seen:
                                        seen.add(display_name.lower())
                                        apps.append(InstalledApp(
                                            name=display_name,
                                            exec_name=exec_candidate,
                                            exec_path=install_loc,
                                            icon=display_icon,
                                            category="Applications"
                                        ))
                            except Exception:
                                continue
                except Exception:
                    continue
        except ImportError:
            pass

        return sorted(apps, key=lambda a: a.name.lower())

    def _scan_fallback_applications(self) -> List[InstalledApp]:
        """Fallback application list for other platforms or testing."""
        return [
            InstalledApp("Web Browser", "firefox", category="Internet"),
            InstalledApp("Chrome Browser", "google-chrome", category="Internet"),
            InstalledApp("Terminal", "bash", category="System"),
            InstalledApp("Discord", "discord", category="Social"),
            InstalledApp("Spotify", "spotify", category="Media"),
        ]

    def get_running_processes(self) -> List[Dict[str, Any]]:
        """Get all currently running processes with detailed metadata."""
        processes = []
        for proc in psutil.process_iter(["pid", "name", "exe", "status", "cpu_percent", "memory_percent", "username"]):
            try:
                info = proc.info
                pname = info.get("name") or ""
                clean_name = normalize_process_name(pname)
                pid = info.get("pid", 0)

                processes.append({
                    "pid": pid,
                    "name": pname,
                    "clean_name": clean_name,
                    "exe": info.get("exe") or "",
                    "status": info.get("status") or "running",
                    "cpu_percent": info.get("cpu_percent") or 0.0,
                    "memory_percent": round(info.get("memory_percent") or 0.0, 2),
                    "username": info.get("username") or "",
                    "is_critical": is_critical_process(clean_name, pid=pid)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return sorted(processes, key=lambda p: p["name"].lower())
