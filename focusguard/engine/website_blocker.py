"""Website Blocking and Strict Whitelisting Coordinator Engine.

Enforces system-wide browser filtering such that when Focus Mode runs,
ALL URLs across all web browsers are blocked by default, and ONLY explicitly
saved whitelisted URLs remain open and accessible.
"""

import logging
from typing import List, Set, Optional
from focusguard.core.database import Database
from focusguard.core.models import WebsiteRule
from focusguard.engine.hosts_manager import HostsManager
from focusguard.engine.block_server import BlockPageServer
from focusguard.engine.proxy_manager import SystemProxyManager

logger = logging.getLogger("focusguard.engine.website_blocker")

CURATED_DISTRACTION_DOMAINS: List[str] = [
    # Top social & distraction domains for blacklist mode
    "facebook.com", "instagram.com", "tiktok.com", "twitter.com", "x.com",
    "snapchat.com", "reddit.com", "pinterest.com", "tumblr.com", "threads.net",
    "linkedin.com", "discord.com", "telegram.org",
    "youtube.com", "netflix.com", "twitch.tv", "disneyplus.com", "hulu.com",
    "primevideo.com", "steamcommunity.com", "steampowered.com", "roblox.com",
]

class WebsiteBlocker:
    def __init__(
        self,
        db: Optional[Database] = None,
        hosts_mgr: Optional[HostsManager] = None,
        block_server: Optional[BlockPageServer] = None,
        proxy_mgr: Optional[SystemProxyManager] = None
    ):
        self.db = db or Database()
        self.hosts_mgr = hosts_mgr or HostsManager()
        self.block_server = block_server or BlockPageServer(db=self.db)
        self.proxy_mgr = proxy_mgr or SystemProxyManager()

    def get_mode(self) -> str:
        """Get current blocking mode: defaults to 'whitelist' for strict distraction protection."""
        return self.db.get_setting("blocking_mode", default="whitelist")

    def set_mode(self, mode: str) -> None:
        """Set current blocking mode ('whitelist' or 'blacklist')."""
        if mode not in ("whitelist", "blacklist"):
            raise ValueError("Mode must be either 'whitelist' or 'blacklist'")
        self.db.set_setting("blocking_mode", mode)
        self.sync_rules()

    def is_url_allowed(self, raw_url_or_domain: str) -> bool:
        """Check whether a specific domain or URL is currently allowed to open."""
        domain = WebsiteRule.extract_domain(raw_url_or_domain)
        if not domain:
            return False

        mode = self.get_mode()
        if mode == "whitelist":
            # Only explicitly saved active whitelist rules are allowed
            rules = self.db.get_website_rules(rule_type="whitelist", only_active=True)
            for r in rules:
                d = r.domain.lower()
                if domain == d or domain.endswith("." + d):
                    return True
            return False
        else:
            # Blacklist mode: allowed if not explicitly in blacklist
            bl_rules = self.db.get_website_rules(rule_type="blacklist", only_active=True)
            for r in bl_rules:
                d = r.domain.lower()
                if domain == d or domain.endswith("." + d):
                    return False
            return True

    def sync_rules(self) -> List[str]:
        """
        Enforce active blocking policies.
        In Whitelist mode: activates system proxy with PAC script to block ALL
        browser URLs except saved ones, and ensures block server is running.
        """
        mode = self.get_mode()

        # Ensure block server is running to serve PAC and block pages
        if not self.block_server.is_running:
            self.block_server.start()

        # Activate system proxy for browser-level enforcement
        self.proxy_mgr.enable_proxy()

        # Complement with hosts file entries where applicable
        domains_to_hosts: Set[str] = set()
        if mode == "blacklist":
            bl_rules = self.db.get_website_rules(rule_type="blacklist", only_active=True)
            for r in bl_rules:
                if r.domain:
                    domains_to_hosts.add(r.domain)
        else:
            # In whitelist mode, add curated distraction domains to hosts as an extra layer
            wl_rules = self.db.get_website_rules(rule_type="whitelist", only_active=True)
            whitelisted = {r.domain.lower() for r in wl_rules}
            for dist in CURATED_DISTRACTION_DOMAINS:
                if dist not in whitelisted:
                    domains_to_hosts.add(dist)

        blocked_list = sorted(domains_to_hosts)
        try:
            if blocked_list:
                self.hosts_mgr.apply_blocked_domains(blocked_list)
            else:
                self.hosts_mgr.clear_all_blocks()
        except PermissionError as pe:
            logger.debug(f"Hosts file update skipped (system proxy active): {pe}")

        return blocked_list

    def unblock_all(self) -> bool:
        """Clear all restrictions and restore completely open browser access."""
        # 1. Disable system proxy
        self.proxy_mgr.disable_proxy()

        # 2. Clear hosts file blocks
        try:
            self.hosts_mgr.clear_all_blocks()
        except PermissionError:
            pass

        return True
