"""FocusGuard Command-Line Interface (CLI).

Provides terminal commands to manage website whitelists/blacklists,
block or allow desktop applications, manage timed sessions and schedules,
and perform emergency unblocking without opening the graphical interface.
"""

import sys
import os
import argparse
from datetime import timedelta
from typing import List, Optional
from focusguard.core.config import APP_NAME, APP_VERSION, is_admin
from focusguard.core.models import WebsiteRule, AppRule, ScheduleRule
from focusguard.core.database import Database
from focusguard.core.duration import parse_duration, format_duration, format_time_remaining
from focusguard.core.safety import is_critical_process
from focusguard.engine.app_detector import AppDetector
from focusguard.engine.app_blocker import AppBlocker
from focusguard.engine.website_blocker import WebsiteBlocker
from focusguard.engine.scheduler import Scheduler

def print_banner():
    print(f"\033[1;36m=== {APP_NAME} CLI v{APP_VERSION} ===\033[0m")

def format_status_badge(text: str, color_code: str) -> str:
    return f"\033[{color_code}m{text}\033[0m"

# --- Command Handlers ---

def cmd_status(args, db: Database, scheduler: Scheduler):
    """Display overall application and restriction status."""
    print_banner()
    status = scheduler.get_current_status()

    mode = status["mode"].upper()
    active = status["is_blocking_active"]

    status_str = format_status_badge("ACTIVE", "1;32") if active else format_status_badge("IDLE", "1;33")
    print(f"\nFocus Guard State : {status_str}")
    if mode == "WHITELIST":
        print(f"Policy Mode       : \033[1;32mSTRICT WHITELIST\033[0m (ALL browser URLs blocked EXCEPT saved approved list)")
    else:
        print(f"Policy Mode       : \033[1mBLACKLIST\033[0m (Blocks specific restricted sites)")
    print(f"Admin Privileges  : {'Yes (root/admin)' if is_admin() else 'No (Standard User)'}")

    if status["has_timed_session"]:
        rem = status["remaining_seconds"]
        print(f"Countdown Timer   : \033[1;32m{format_time_remaining(rem)} remaining\033[0m")
        print("\nActive Sessions:")
        for s in status["active_sessions"]:
            print(f"  - Target: {s['target']} | Ends: {s['end_time']} | Reason: {s['reason']}")

    if status["has_active_schedule"]:
        print("\nActive Recurring Schedules:")
        for sc in status["active_schedules"]:
            print(f"  - {sc['name']}: {sc['days_of_week']} ({sc['start_time']} - {sc['end_time']})")

    # Summary counts
    whitelisted = len(db.get_website_rules(rule_type="whitelist", only_active=True))
    blacklisted = len(db.get_website_rules(rule_type="blacklist", only_active=True))
    blocked_apps = len(db.get_app_rules(only_blocked=True))

    print(f"\nRules Overview:")
    print(f"  - Whitelisted Sites : {whitelisted}")
    print(f"  - Blacklisted Sites : {blacklisted}")
    print(f"  - Blocked Apps      : {blocked_apps}")
    print()

def cmd_allow_site(args, db: Database, blocker: WebsiteBlocker):
    """Add an approved website to the whitelist."""
    raw_url = args.url
    domain = WebsiteRule.extract_domain(raw_url)
    if not domain:
        print(f"\033[1;31mError:\033[0m Invalid website URL '{raw_url}'.")
        sys.exit(1)

    rule = WebsiteRule(
        url=raw_url,
        domain=domain,
        rule_type="whitelist",
        is_active=True,
        category=args.category or "Approved"
    )
    db.add_website_rule(rule)
    print(f"\033[1;32mSuccess:\033[0m Added '\033[1m{domain}\033[0m' to approved whitelist.")

    try:
        blocker.sync_rules()
    except PermissionError as e:
        print(f"\033[1;33mNote:\033[0m {e}")

def cmd_block_site(args, db: Database, blocker: WebsiteBlocker):
    """Add a website to the blacklist."""
    raw_url = args.url
    domain = WebsiteRule.extract_domain(raw_url)
    if not domain:
        print(f"\033[1;31mError:\033[0m Invalid website URL '{raw_url}'.")
        sys.exit(1)

    rule = WebsiteRule(
        url=raw_url,
        domain=domain,
        rule_type="blacklist",
        is_active=True,
        category=args.category or "Restricted"
    )
    db.add_website_rule(rule)
    print(f"\033[1;32mSuccess:\033[0m Added '\033[1m{domain}\033[0m' to blocked blacklist.")

    try:
        blocker.sync_rules()
    except PermissionError as e:
        print(f"\033[1;33mNote:\033[0m {e}")

def cmd_unblock_site(args, db: Database, blocker: WebsiteBlocker):
    """Remove a website rule."""
    target = args.domain_or_url
    removed = db.remove_website_rule(target)
    if removed:
        print(f"\033[1;32mSuccess:\033[0m Removed rule for '{target}'.")
        try:
            blocker.sync_rules()
        except PermissionError:
            pass
    else:
        print(f"\033[1;33mWarning:\033[0m No rule found for '{target}'.")

def cmd_check_site(args, blocker: WebsiteBlocker):
    """Check whether a website is allowed or blocked."""
    raw = args.url
    domain = WebsiteRule.extract_domain(raw)
    allowed = blocker.is_url_allowed(raw)
    mode = blocker.get_mode().upper()

    print_banner()
    print(f"\nTarget URL     : \033[1m{raw}\033[0m")
    print(f"Clean Domain   : \033[1m{domain}\033[0m")
    print(f"Policy Mode    : \033[1m{mode}\033[0m")
    if allowed:
        print(f"Access Status  : \033[1;32mALLOWED (Open in Browsers)\033[0m")
    else:
        print(f"Access Status  : \033[1;31mBLOCKED (Restricted by FocusGuard)\033[0m")
    print()

def cmd_list_sites(args, db: Database):
    """List configured website rules."""
    print_banner()
    rule_type = args.type if hasattr(args, "type") and args.type != "all" else None
    rules = db.get_website_rules(rule_type=rule_type)

    if not rules:
        print("No website rules configured yet.")
        return

    print(f"\n{'DOMAIN':<30} {'TYPE':<12} {'CATEGORY':<15} {'STATUS':<10}")
    print("-" * 70)
    for r in rules:
        status_col = "\033[32mActive\033[0m" if r.is_active else "\033[90mDisabled\033[0m"
        type_col = "\033[34mWhitelist\033[0m" if r.rule_type == "whitelist" else "\033[31mBlacklist\033[0m"
        print(f"{r.domain:<30} {type_col:<21} {r.category:<15} {status_col}")
    print()

def cmd_list_apps(args, db: Database, detector: AppDetector):
    """List detected applications and processes."""
    print_banner()
    installed = detector.get_installed_applications()
    running_procs = detector.get_running_processes()
    running_names = {p["clean_name"] for p in running_procs}
    blocked_rules = {r.process_name.lower(): r for r in db.get_app_rules(only_blocked=True)}

    print(f"\n{'APPLICATION':<25} {'EXECUTABLE':<20} {'STATUS':<12} {'RESTRICTION':<15}")
    print("-" * 75)

    for app in installed:
        exec_lower = app.exec_name.lower()
        is_running = exec_lower in running_names or (f"{exec_lower}.exe" in running_names)
        is_blocked = exec_lower in blocked_rules or (f"{exec_lower}.exe" in blocked_rules)
        is_crit = is_critical_process(app.exec_name)

        status_str = "\033[32mRunning\033[0m" if is_running else "\033[90mStopped\033[0m"

        if is_crit:
            restr_str = "\033[36mProtected\033[0m"
        elif is_blocked:
            restr_str = "\033[31mBlocked\033[0m"
        else:
            restr_str = "\033[32mAllowed\033[0m"

        print(f"{app.name[:24]:<25} {app.exec_name[:19]:<20} {status_str:<21} {restr_str}")
    print(f"\nTotal Detected Applications: {len(installed)}")
    print()

def cmd_block_app(args, db: Database, scheduler: Scheduler, app_blocker: AppBlocker):
    """Block an application, optionally for a specified duration."""
    target_app = args.app_name.strip()
    clean_name = target_app.lower()

    if is_critical_process(clean_name):
        print(f"\033[1;31mSafety Protection:\033[0m Cannot block '{target_app}' because it is an essential system process.")
        sys.exit(1)

    rule = AppRule(
        app_name=target_app,
        process_name=clean_name,
        is_blocked=True,
        category="Distraction"
    )
    db.add_app_rule(rule)

    duration_str = args.duration
    if duration_str:
        td = parse_duration(duration_str)
        if not td:
            print(f"\033[1;31mError:\033[0m Invalid duration format '{duration_str}'. Use formats like 2h, 30m, 1h30m.")
            sys.exit(1)
        scheduler.start_timed_session(duration=td, target=clean_name, session_type="app_timed", reason=f"CLI block-app for {duration_str}")
        print(f"\033[1;32mSuccess:\033[0m Blocked '\033[1m{target_app}\033[0m' for \033[1;36m{format_duration(td)}\033[0m.")
    else:
        print(f"\033[1;32mSuccess:\033[0m Blocked '\033[1m{target_app}\033[0m' indefinitely.")

    # Terminate running instances immediately
    terminated = app_blocker.check_and_enforce()
    if terminated:
        print(f"Terminated {len(terminated)} running instance(s).")

def cmd_unblock_app(args, db: Database):
    """Unblock an application."""
    target_app = args.app_name.strip()
    db.set_app_blocked_status(target_app, blocked=False)
    print(f"\033[1;32mSuccess:\033[0m Unblocked '\033[1m{target_app}\033[0m'.")

def cmd_schedule_list(args, db: Database):
    """List recurring schedules."""
    print_banner()
    schedules = db.get_schedule_rules()
    if not schedules:
        print("No recurring schedules configured yet.")
        return

    print(f"\n{'ID':<5} {'NAME':<20} {'DAYS':<20} {'TIME':<15} {'MODE':<12} {'ENABLED':<10}")
    print("-" * 85)
    for s in schedules:
        en_str = "\033[32mYes\033[0m" if s.is_enabled else "\033[90mNo\033[0m"
        time_str = f"{s.start_time} - {s.end_time}"
        print(f"{s.id:<5} {s.name:<20} {s.days_of_week:<20} {time_str:<15} {s.mode:<12} {en_str}")
    print()

def cmd_emergency_unblock(args, db: Database, blocker: WebsiteBlocker, scheduler: Scheduler):
    """Emergency fail-safe: lift all restrictions and restore clean hosts file."""
    print("\033[1;33mInitiating Emergency Recovery...\033[0m")
    scheduler.cancel_active_sessions()
    try:
        blocker.unblock_all()
        print("\033[1;32mEmergency Recovery Complete:\033[0m All website and application restrictions lifted.")
    except PermissionError as e:
        print(f"\033[1;31mError:\033[0m {e}")

def cmd_start(args, db: Database, scheduler: Scheduler, blocker: WebsiteBlocker):
    """Start focus shield with strict URL whitelisting and application restrictions."""
    dur_str = getattr(args, "duration", "1h") or "1h"
    td = parse_duration(dur_str)
    if not td:
        print(f"\033[1;31mError:\033[0m Invalid duration format '{dur_str}'. Use formats like 25m, 1h, 2h.")
        sys.exit(1)

    reason = getattr(args, "reason", "Focus session") or "Focus session"
    session_id = scheduler.start_focus(duration=td, reason=reason)
    mode = blocker.get_mode().upper()

    print_banner()
    print(f"\n\033[1;32m=== FOCUS SHIELD ACTIVATED ===\033[0m")
    print(f"Session ID       : #{session_id}")
    print(f"Duration         : \033[1;36m{format_duration(td)}\033[0m")
    if mode == "WHITELIST":
        print(f"Policy           : \033[1;32mSTRICT WHITELIST\033[0m")
        print(f"Browser Status   : \033[1;33mALL browser URLs are now BLOCKED except saved whitelist.\033[0m")
    else:
        print(f"Policy           : \033[1mBLACKLIST\033[0m (Blocking restricted websites)")
    print(f"Stop Command     : Run '\033[1mfocusguard stop\033[0m' at any time to deactivate.\n")

def cmd_stop(args, db: Database, scheduler: Scheduler, blocker: WebsiteBlocker):
    """Stop focus shield and lift all restrictions."""
    count = scheduler.stop_focus()
    try:
        blocker.unblock_all()
    except Exception:
        pass

    print_banner()
    print(f"\n\033[1;32m=== FOCUS SHIELD DEACTIVATED ===\033[0m")
    print(f"Active Sessions  : {count} session(s) ended.")
    print(f"Browser Status   : \033[1;32mAll restrictions lifted. Browsers restored to open access.\033[0m\n")

def cmd_mode(args, blocker: WebsiteBlocker):
    """View or switch blocking mode."""
    if args.set_mode:
        m = args.set_mode.lower()
        if m in ("whitelist", "blacklist"):
            blocker.set_mode(m)
            print(f"\033[1;32mMode updated to:\033[0m {m.upper()}")
        else:
            print("\033[1;31mError:\033[0m Mode must be 'whitelist' or 'blacklist'.")
    else:
        print(f"Current blocking mode: \033[1m{blocker.get_mode().upper()}\033[0m")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="focusguard",
        description="FocusGuard - Cross-Platform Website and Application Blocking Software",
        epilog="Run 'focusguard <command> --help' for details on each command."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # status
    subparsers.add_parser("status", help="Display application and restriction status")

    # start
    p_start = subparsers.add_parser("start", help="Activate focus shield and start blocking distractions")
    p_start.add_argument("--duration", "-d", default="1h", help="Duration for focus session (e.g. 25m, 1h, 2h). Default: 1h")
    p_start.add_argument("--reason", "-r", default="Focus session", help="Reason for session")

    # stop
    subparsers.add_parser("stop", help="Deactivate focus shield and lift all restrictions")

    # allow-site
    p_allow = subparsers.add_parser("allow-site", help="Add an approved website to the whitelist")
    p_allow.add_argument("url", help="Website URL or domain (e.g., https://example.com)")
    p_allow.add_argument("--category", "-c", help="Category tag (e.g. Study, Research)")

    # block-site
    p_block_site = subparsers.add_parser("block-site", help="Add a website to the blacklist")
    p_block_site.add_argument("url", help="Website URL or domain (e.g., https://example.org)")
    p_block_site.add_argument("--category", "-c", help="Category tag (e.g. Social, Gaming)")

    # unblock-site
    p_unblock_site = subparsers.add_parser("unblock-site", help="Remove a website restriction")
    p_unblock_site.add_argument("domain_or_url", help="Domain or URL to remove")

    # list-sites
    p_list_sites = subparsers.add_parser("list-sites", help="List configured website rules")
    p_list_sites.add_argument("--type", choices=["all", "whitelist", "blacklist"], default="all")

    # check-site
    p_check_site = subparsers.add_parser("check-site", help="Check whether a URL is permitted or blocked")
    p_check_site.add_argument("url", help="Website URL to test (e.g. google.com or wikipedia.org)")

    # list-apps
    subparsers.add_parser("list-apps", help="List installed desktop applications and processes")

    # block-app
    p_block_app = subparsers.add_parser("block-app", help="Block a desktop application")
    p_block_app.add_argument("app_name", help="Application name or executable (e.g., firefox, discord)")
    p_block_app.add_argument("--duration", "-d", help="Optional duration (e.g. 2h, 45m, 1h30m)")

    # unblock-app
    p_unblock_app = subparsers.add_parser("unblock-app", help="Unblock a desktop application")
    p_unblock_app.add_argument("app_name", help="Application name or executable")

    # schedule
    p_schedule = subparsers.add_parser("schedule", help="Manage recurring blocking schedules")
    sched_sub = p_schedule.add_subparsers(dest="subcommand")
    sched_sub.add_parser("list", help="Display the active blocking schedule")

    # mode
    p_mode = subparsers.add_parser("mode", help="View or set blocking mode (whitelist or blacklist)")
    p_mode.add_argument("set_mode", nargs="?", choices=["whitelist", "blacklist"], help="Mode to set")

    # emergency-unblock
    subparsers.add_parser("emergency-unblock", help="Emergency fail-safe: immediately lift all restrictions")

    # daemon
    p_daemon = subparsers.add_parser("daemon", help="Run background enforcement service")
    p_daemon.add_argument("action", choices=["run"], default="run")

    return parser

def main(args: Optional[List[str]] = None) -> int:
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    db = Database()
    detector = AppDetector()
    app_blocker = AppBlocker(db)
    website_blocker = WebsiteBlocker(db)
    scheduler = Scheduler(db, app_blocker, website_blocker)

    if parsed_args.command == "status":
        cmd_status(parsed_args, db, scheduler)
    elif parsed_args.command == "start":
        cmd_start(parsed_args, db, scheduler, website_blocker)
    elif parsed_args.command == "stop":
        cmd_stop(parsed_args, db, scheduler, website_blocker)
    elif parsed_args.command == "allow-site":
        cmd_allow_site(parsed_args, db, website_blocker)
    elif parsed_args.command == "block-site":
        cmd_block_site(parsed_args, db, website_blocker)
    elif parsed_args.command == "unblock-site":
        cmd_unblock_site(parsed_args, db, website_blocker)
    elif parsed_args.command == "list-sites":
        cmd_list_sites(parsed_args, db)
    elif parsed_args.command == "check-site":
        cmd_check_site(parsed_args, website_blocker)
    elif parsed_args.command == "list-apps":
        cmd_list_apps(parsed_args, db, detector)
    elif parsed_args.command == "block-app":
        cmd_block_app(parsed_args, db, scheduler, app_blocker)
    elif parsed_args.command == "unblock-app":
        cmd_unblock_app(parsed_args, db)
    elif parsed_args.command == "schedule":
        if parsed_args.subcommand == "list" or not parsed_args.subcommand:
            cmd_schedule_list(parsed_args, db)
        else:
            parser.print_help()
    elif parsed_args.command == "mode":
        cmd_mode(parsed_args, website_blocker)
    elif parsed_args.command == "emergency-unblock":
        cmd_emergency_unblock(parsed_args, db, website_blocker, scheduler)
    elif parsed_args.command == "daemon":
        print("Starting FocusGuard background daemon. Press Ctrl+C to terminate...")
        scheduler.start_background_loop()
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop_background_loop()
            print("Daemon stopped.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
