"""System Proxy and PAC (Proxy Auto-Configuration) Management Engine.

Enforces system-wide default-deny browser blocking across Chrome, Firefox,
Edge, Brave, and other major browsers by routing unapproved URLs to the
FocusGuard block server while keeping saved whitelisted URLs open and direct.
"""

import os
import sys
import shutil
import subprocess
import logging
from typing import Optional
from focusguard.core.config import IS_LINUX, IS_WINDOWS, DEFAULT_BLOCK_HOST, DEFAULT_BLOCK_PORT

logger = logging.getLogger("focusguard.engine.proxy_manager")

class SystemProxyManager:
    def __init__(self, pac_url: Optional[str] = None):
        self.pac_url = pac_url or f"http://{DEFAULT_BLOCK_HOST}:{DEFAULT_BLOCK_PORT}/proxy.pac"
        self._is_proxy_enabled = False

    def enable_proxy(self) -> bool:
        """Enable system-wide proxy auto-config pointing to the FocusGuard PAC script."""
        success = False
        if IS_LINUX:
            success = self._enable_linux_proxy()
        elif IS_WINDOWS:
            success = self._enable_windows_proxy()
        else:
            logger.warning("Unsupported OS for native system proxy configuration.")

        if success:
            self._is_proxy_enabled = True
            logger.info(f"System proxy enabled pointing to {self.pac_url}")
        return success

    def disable_proxy(self) -> bool:
        """Disable system proxy and restore normal unrestricted internet access."""
        success = False
        if IS_LINUX:
            success = self._disable_linux_proxy()
        elif IS_WINDOWS:
            success = self._disable_windows_proxy()
        else:
            success = True

        self._is_proxy_enabled = False
        logger.info("System proxy disabled; normal browser access restored.")
        return success

    def is_enabled(self) -> bool:
        """Check if system proxy auto-config is currently enabled."""
        if IS_LINUX:
            return self._check_linux_proxy()
        elif IS_WINDOWS:
            return self._check_windows_proxy()
        return self._is_proxy_enabled

    # --- Linux (GNOME / FreeDesktop / GSettings) ---

    def _enable_linux_proxy(self) -> bool:
        try:
            if shutil.which("gsettings"):
                subprocess.run(
                    ["gsettings", "set", "org.gnome.system.proxy", "mode", "auto"],
                    check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                subprocess.run(
                    ["gsettings", "set", "org.gnome.system.proxy", "autoconfig-url", self.pac_url],
                    check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                return True
        except Exception as e:
            logger.warning(f"Failed to set Linux gsettings proxy: {e}")
        return False

    def _disable_linux_proxy(self) -> bool:
        try:
            if shutil.which("gsettings"):
                subprocess.run(
                    ["gsettings", "set", "org.gnome.system.proxy", "mode", "none"],
                    check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                subprocess.run(
                    ["gsettings", "set", "org.gnome.system.proxy", "autoconfig-url", ""],
                    check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                return True
        except Exception as e:
            logger.warning(f"Failed to reset Linux gsettings proxy: {e}")
        return False

    def _check_linux_proxy(self) -> bool:
        try:
            if shutil.which("gsettings"):
                res = subprocess.run(
                    ["gsettings", "get", "org.gnome.system.proxy", "mode"],
                    capture_output=True, text=True, check=False
                )
                return "auto" in res.stdout
        except Exception:
            pass
        return self._is_proxy_enabled

    # --- Windows (Registry HKCU Internet Settings) ---

    def _enable_windows_proxy(self) -> bool:
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "AutoConfigURL", 0, winreg.REG_SZ, self.pac_url)

            self._refresh_windows_internet_options()
            return True
        except Exception as e:
            logger.warning(f"Failed to set Windows proxy registry: {e}")
            return False

    def _disable_windows_proxy(self) -> bool:
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                try:
                    winreg.DeleteValue(key, "AutoConfigURL")
                except FileNotFoundError:
                    pass

            self._refresh_windows_internet_options()
            return True
        except Exception as e:
            logger.warning(f"Failed to clear Windows proxy registry: {e}")
            return False

    def _check_windows_proxy(self) -> bool:
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_QUERY_VALUE) as key:
                val, _ = winreg.QueryValueEx(key, "AutoConfigURL")
                return bool(val and self.pac_url in val)
        except Exception:
            return False

    def _refresh_windows_internet_options(self) -> None:
        """Notify Windows internet subsystem of proxy setting changes."""
        try:
            import ctypes
            # INTERNET_OPTION_SETTINGS_CHANGED = 39, INTERNET_OPTION_REFRESH = 37
            wininet = ctypes.windll.wininet
            wininet.InternetSetOptionW(0, 39, 0, 0)
            wininet.InternetSetOptionW(0, 37, 0, 0)
        except Exception as e:
            logger.debug(f"InternetSetOption call skipped: {e}")
