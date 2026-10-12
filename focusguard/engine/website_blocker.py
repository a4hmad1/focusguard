"""Website Blocking and Whitelisting Coordinator Engine.

Synchronizes database rules with system hosts file and local block server,
supporting both Blacklist Mode and strict Whitelist Mode.
"""

import logging
from typing import List, Set, Optional
from focusguard.core.database import Database
from focusguard.core.models import WebsiteRule
from focusguard.engine.hosts_manager import HostsManager
from focusguard.engine.block_server import BlockPageServer

logger = logging.getLogger("focusguard.engine.website_blocker")

# Broad list of common distraction and entertainment domains for Whitelist Mode
CURATED_DISTRACTION_DOMAINS: List[str] = [
    # Social Media
    "facebook.com", "instagram.com", "tiktok.com", "twitter.com", "x.com",
    "snapchat.com", "reddit.com", "pinterest.com", "tumblr.com", "threads.net",
    "linkedin.com", "weibo.com", "vk.com", "discord.com", "telegram.org",
    # Video & Streaming
    "youtube.com", "netflix.com", "twitch.tv", "disneyplus.com", "hulu.com",
    "primevideo.com", "max.com", "dailymotion.com", "vimeo.com", "crunchyroll.com",
    # Gaming & Entertainment
    "steamcommunity.com", "steampowered.com", "roblox.com", "epicgames.com",
    "ea.com", "ign.com", "kotaku.com", "twitch.com", "battlenet.com",
    # News & Gossip
    "buzzfeed.com", "tmz.com", "dailymail.co.uk", "thesun.co.uk", "9gag.com",
    "boredpanda.com", "imgur.com",
    # Shopping & Leisure
    "amazon.com", "ebay.com", "aliexpress.com", "shein.com", "temu.com",
]

# Essential infrastructure domains that must never be blocked in whitelist mode
CRITICAL_INFRASTRUCTURE_DOMAINS: Set[str] = {
    "localhost", "127.0.0.1", "::1",
    "ocsp.digicert.com", "ocsp.sectigo.com", "ocsp.pki.goog",
    "crl.identrust.com", "valid.apple.com"
}

class WebsiteBlocker:
    def __init__(
        self,
        db: Optional[Database] = None,
        hosts_mgr: Optional[HostsManager] = None,
        block_server: Optional[BlockPageServer] = None
    ):
        self.db = db or Database()
        self.hosts_mgr = hosts_mgr or HostsManager()
        self.block_server = block_server or BlockPageServer()

    def get_mode(self) -> str:
        """Get current blocking mode: 'blacklist' or 'whitelist'."""
        return self.db.get_setting("blocking_mode", default="blacklist")

    def set_mode(self, mode: str) -> None:
        """Set current blocking mode."""
        if mode not in ("blacklist", "whitelist"):
            raise ValueError("Mode must be either 'blacklist' or 'whitelist'")
        self.db.set_setting("blocking_mode", mode)
        self.sync_rules()

    def sync_rules(self) -> List[str]:
        """
        Evaluate database rules and update the hosts file.
        Returns the list of domains effectively blocked.
        """
        mode = self.get_mode()
        domains_to_block: Set[str] = set()

        if mode == "blacklist":
            # In blacklist mode, block all active blacklist entries
            rules = self.db.get_website_rules(rule_type="blacklist", only_active=True)
            for rule in rules:
                d = WebsiteRule.extract_domain(rule.domain or rule.url)
                if d and d not in CRITICAL_INFRASTRUCTURE_DOMAINS:
                    domains_to_block.add(d)
        else:
            # In whitelist mode, block curated distraction pool except approved whitelist domains
            whitelist_rules = self.db.get_website_rules(rule_type="whitelist", only_active=True)
            whitelisted_domains = {
                WebsiteRule.extract_domain(r.domain or r.url)
                for r in whitelist_rules
            }

            for dist in CURATED_DISTRACTION_DOMAINS:
                if dist not in whitelisted_domains and dist not in CRITICAL_INFRASTRUCTURE_DOMAINS:
                    domains_to_block.add(dist)

            # Also include any custom blacklist rules
            custom_bl = self.db.get_website_rules(rule_type="blacklist", only_active=True)
            for r in custom_bl:
                d = WebsiteRule.extract_domain(r.domain or r.url)
                if d and d not in whitelisted_domains and d not in CRITICAL_INFRASTRUCTURE_DOMAINS:
                    domains_to_block.add(d)

        # Apply to system hosts file
        blocked_list = sorted(domains_to_block)
        try:
            if blocked_list:
                self.hosts_mgr.apply_blocked_domains(blocked_list)
                # Ensure block server is running
                if not self.block_server.is_running:
                    self.block_server.start()
            else:
                self.hosts_mgr.clear_all_blocks()
        except PermissionError as pe:
            logger.warning(f"Could not apply hosts rules (requires elevation): {pe}")
            raise pe

        return blocked_list

    def unblock_all(self) -> bool:
        """Clear all domain blocks immediately."""
        try:
            return self.hosts_mgr.clear_all_blocks()
        except PermissionError as pe:
            logger.warning(f"Could not clear hosts rules: {pe}")
            raise pe
