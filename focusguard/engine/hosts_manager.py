"""Hosts File Management and DNS Redirection Engine.

Safely modifies system hosts file (/etc/hosts on Linux,
C:\\Windows\\System32\\drivers\\etc\\hosts on Windows) using marked blocks,
backs up the original file, and flushes OS DNS caches.
"""

import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import List, Set, Optional
from focusguard.core.config import get_hosts_path, get_hosts_backup_path, IS_WINDOWS, IS_LINUX

logger = logging.getLogger("focusguard.engine.hosts_manager")

BLOCK_START_MARKER = "# === FOCUSGUARD MANAGED BLOCK START ==="
BLOCK_END_MARKER = "# === FOCUSGUARD MANAGED BLOCK END ==="

class HostsManager:
    def __init__(self, hosts_path: Optional[Path] = None, backup_path: Optional[Path] = None):
        self.hosts_path = hosts_path or get_hosts_path()
        self.backup_path = backup_path or get_hosts_backup_path()

    def backup_hosts_file_if_needed(self) -> bool:
        """Create a safety backup of the original hosts file if one does not already exist."""
        try:
            if not self.backup_path.exists() and self.hosts_path.exists():
                shutil.copy2(self.hosts_path, self.backup_path)
                logger.info(f"Created hosts backup at {self.backup_path}")
                return True
        except Exception as e:
            logger.warning(f"Could not create hosts backup: {e}")
        return False

    def is_writable(self) -> bool:
        """Check if the hosts file is writable with current process privileges."""
        try:
            return os.access(self.hosts_path, os.W_OK)
        except Exception:
            return False

    def get_currently_blocked_domains(self) -> Set[str]:
        """Read the hosts file and extract domains currently inside the FocusGuard block."""
        if not self.hosts_path.exists():
            return set()

        blocked = set()
        in_managed_block = False

        try:
            with open(self.hosts_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped == BLOCK_START_MARKER:
                        in_managed_block = True
                        continue
                    elif stripped == BLOCK_END_MARKER:
                        in_managed_block = False
                        break

                    if in_managed_block and stripped and not stripped.startswith("#"):
                        parts = stripped.split()
                        if len(parts) >= 2:
                            blocked.add(parts[1].lower())
        except Exception as e:
            logger.error(f"Error reading hosts file: {e}")

        return blocked

    def apply_blocked_domains(self, domains: List[str], redirect_ip: str = "127.0.0.1") -> bool:
        """
        Update the hosts file with the provided blocked domains.
        Expands domains to include 'www.' subdomains where appropriate.
        """
        self.backup_hosts_file_if_needed()

        if not self.is_writable():
            raise PermissionError(
                f"Cannot modify {self.hosts_path}. Administrative privileges required "
                f"({'Run as Administrator' if IS_WINDOWS else 'Run with sudo or root'})."
            )

        # Build clean domain list with subdomains
        unique_domains: Set[str] = set()
        for d in domains:
            d_clean = d.strip().lower()
            if not d_clean:
                continue
            unique_domains.add(d_clean)
            if not d_clean.startswith("www.") and "." in d_clean:
                unique_domains.add(f"www.{d_clean}")

        # Read current hosts file excluding existing FocusGuard block
        original_lines: List[str] = []
        in_managed_block = False

        if self.hosts_path.exists():
            with open(self.hosts_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped == BLOCK_START_MARKER:
                        in_managed_block = True
                        continue
                    elif stripped == BLOCK_END_MARKER:
                        in_managed_block = False
                        continue
                    if not in_managed_block:
                        original_lines.append(line)

        # Build new block
        new_block_lines = [
            f"\n{BLOCK_START_MARKER}\n",
            "# Managed automatically by FocusGuard. Do not edit this section manually.\n",
        ]
        for domain in sorted(unique_domains):
            new_block_lines.append(f"{redirect_ip} {domain}\n")
            new_block_lines.append(f"::1 {domain}\n")
        new_block_lines.append(f"{BLOCK_END_MARKER}\n")

        # Combine lines cleanly
        combined = "".join(original_lines).rstrip() + "\n"
        if unique_domains:
            combined += "".join(new_block_lines)

        # Atomic write
        temp_path = self.hosts_path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(combined)
            temp_path.replace(self.hosts_path)
            self.flush_dns_cache()
            return True
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e

    def clear_all_blocks(self) -> bool:
        """Remove all FocusGuard blocks from hosts file, restoring normal access."""
        if not self.hosts_path.exists():
            return True

        if not self.is_writable():
            raise PermissionError(
                f"Cannot clear blocks from {self.hosts_path}. Administrative privileges required."
            )

        clean_lines = []
        in_managed_block = False

        with open(self.hosts_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                stripped = line.strip()
                if stripped == BLOCK_START_MARKER:
                    in_managed_block = True
                    continue
                elif stripped == BLOCK_END_MARKER:
                    in_managed_block = False
                    continue
                if not in_managed_block:
                    clean_lines.append(line)

        temp_path = self.hosts_path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.writelines(clean_lines)
            temp_path.replace(self.hosts_path)
            self.flush_dns_cache()
            return True
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e

    def restore_from_backup(self) -> bool:
        """Emergency restore of the hosts file from safety backup."""
        if self.backup_path.exists():
            if not self.is_writable():
                raise PermissionError("Administrative privileges required to restore hosts file.")
            shutil.copy2(self.backup_path, self.hosts_path)
            self.flush_dns_cache()
            return True
        return False

    def flush_dns_cache(self) -> None:
        """Flush operating system DNS resolver cache."""
        try:
            if IS_WINDOWS:
                subprocess.run(["ipconfig", "/flushdns"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif IS_LINUX:
                # Try systemd-resolved flush
                for cmd in [
                    ["resolvectl", "flush-caches"],
                    ["systemd-resolve", "--flush-caches"],
                    ["nscd", "-i", "hosts"]
                ]:
                    try:
                        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        break
                    except FileNotFoundError:
                        continue
        except Exception as e:
            logger.debug(f"DNS cache flush skipped: {e}")
