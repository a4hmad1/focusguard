# FocusGuard: Cross-Platform Website and Application Blocking Desktop Software

![FocusGuard Banner](focusguard/resources/icons/focusguard.svg)

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Ubuntu%20Linux-blue.svg)](#system-architecture)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-Qt%20%2F%20PySide6-41cd52.svg)](https://wiki.qt.io/Qt_for_Python)
[![License](https://img.shields.io/badge/License-Proprietary%20%2F%20MIT-green.svg)](#)

**FocusGuard** is a professional, cross-platform desktop application engineered for students and professionals to eliminate digital distractions, enforce website and application restrictions, maintain custom study schedules, and build a focused deep-work environment.

---

## Table of Contents

1. [Key Features](#1-key-features)
2. [Architecture & Component Design](#2-architecture--component-design)
3. [Graphical User Interface (GUI)](#3-graphical-user-interface-gui)
4. [Command-Line Interface (CLI)](#4-command-line-interface-cli)
5. [Security Model & Restriction Enforcement](#5-security-model--restriction-enforcement)
6. [Installation & Setup](#6-installation--setup)
   - [Ubuntu Linux (.deb & Terminal)](#ubuntu-linux)
   - [Windows (Executable & Installer)](#windows)
7. [Building Distribution Packages](#7-building-distribution-packages)
8. [Automated Testing Suite](#8-automated-testing-suite)
9. [Technical Limitations & Guidance](#9-technical-limitations--guidance)

---

## 1. Key Features

### A. Website Filtering & Whitelisting
- **Dual Filtering Modes**:
  - **Blacklist Mode**: Blocks explicitly selected websites and distraction domains while keeping the rest of the web accessible.
  - **Strict Whitelist Mode**: Blocks all unapproved internet destinations and distraction hubs, allowing *only* explicitly approved educational websites.
- **System-Wide DNS Redirection**: Modifies operating system hosts resolution (`/etc/hosts` on Linux and `%SystemRoot%\System32\drivers\etc\hosts` on Windows) to route restricted domains to a local landing server.
- **Embedded Block Page**: Serves a modern, calming landing page (`http://127.0.0.1:8880`) whenever a blocked site is requested, displaying the blocked domain, focus quote, active session status, and emergency unlock instructions.
- **Automatic Subdomain Normalization**: Automatically handles `www.`, subdomains, ports, and protocols.

### B. Application & Process Management
- **Automatic App & Process Discovery**:
  - Scans system `.desktop` entries on Ubuntu Linux (including Flatpak and Snap apps).
  - Scans Windows Registry uninstall keys and Start Menu shortcuts on Windows.
  - Scans live running processes in real time via `psutil`.
- **Status Indicators**: Identifies applications as `Allowed`, `Blocked`, `Running`, or `System Protected`.
- **Active Process Terminator**: Scans active processes at high frequency; when a restricted application is launched during an active session, it performs graceful termination followed by force-kill if unresponsive.
- **Operating System Safeguard**: Hardcoded protection ensures essential operating system processes (such as `systemd`, `init`, `explorer.exe`, `dwm.exe`, `csrss.exe`, `bash`, `gnome-shell`, and `focusguard` itself) can **never** be blocked or killed.

### C. Time-Based Sessions & Recurring Schedules
- **Flexible Timed Sessions**: Block resources for minutes, hours, or custom durations (e.g., `25m`, `1h`, `2h 30m`, `1d`).
- **Automatic Unblocking**: When a countdown timer reaches zero, restrictions are immediately lifted and normal access is restored automatically.
- **Recurring Weekly Planner**: Configure recurring schedules for specific days of the week (e.g., Mon–Fri 09:00 to 17:00) with independent Whitelist or Blacklist modes.
- **Persistent State**: Active rules, timers, and schedules are stored in an ACID-compliant SQLite database and resume automatically across system reboots.

---

## 2. Architecture & Component Design

FocusGuard is structured into modular layers:

```
focusguard/
├── core/
│   ├── config.py           # Cross-platform paths, privilege detection, constants
│   ├── database.py         # SQLite schema, migrations, CRUD repository
│   ├── duration.py         # Time parser ("2h", "30m", "1h30m") and formatters
│   ├── models.py           # Dataclasses: WebsiteRule, AppRule, ScheduleRule, ActiveSession
│   └── safety.py           # Core OS protection lists and process validator
├── engine/
│   ├── app_detector.py     # Desktop application and running process discovery
│   ├── app_blocker.py      # Process watchdog, enforcement, and termination
│   ├── block_server.py     # Local HTTP web server delivering "Access Blocked" UI
│   ├── hosts_manager.py    # Safe hosts file modifier with automatic backups & DNS cache flush
│   ├── scheduler.py        # Countdown timers, session manager, and weekly schedule evaluator
│   └── website_blocker.py  # Whitelist/Blacklist coordinator syncing rules to hosts
├── gui/
│   ├── app.py              # PySide6 application bootstrapper
│   ├── main_window.py      # Main window with sidebar navigation and 1-second dynamic updater
│   ├── theme.py            # Modern dark-theme stylesheet
│   ├── tabs/
│   │   ├── dashboard_tab.py# Hero countdown timer, quick start, active session summary
│   │   ├── websites_tab.py # Whitelist/Blacklist table, domain add form, presets
│   │   ├── apps_tab.py     # Installed apps list, process status badges, block toggles
│   │   ├── schedules_tab.py# Weekly schedule creator and manager
│   │   └── settings_tab.py # Emergency unblock, hosts backup restore, DNS flush, audit logs
│   └── widgets/
│       ├── stat_card.py    # Metric summary card
│       └── timer_widget.py # Countdown clock with progress bar and presets
├── daemon/
│   └── service.py          # Headless background service runner
├── cli.py                  # Full-featured command-line interface
└── main.py                 # Intelligent entrypoint (routes to GUI or CLI)
```

---

## 3. Graphical User Interface (GUI)

The desktop GUI is built on **Qt 6 / PySide6**:

1. **Dashboard**:
   - Circular/pill status indicator displaying current state (`FOCUS ACTIVE` or `IDLE`).
   - Centerpiece countdown timer with preset quick-launch buttons (`15m`, `25m Pomodoro`, `45m`, `1h`, `2h`).
   - Summary statistics cards for blocked sites, blocked apps, active processes, and current filtering mode.
   - Live table of active timed sessions.
2. **Websites Tab**:
   - Mode switcher button: Toggle between **Blacklist Mode** and **Whitelist Mode**.
   - Direct input for website URLs with category tagging (`Study`, `Social Media`, `Video`, etc.).
   - "Add Top Distractions Pack" one-click button for common social media and streaming portals.
3. **Applications Tab**:
   - Filterable view: All apps, running only, blocked only, or protected system processes.
   - Instant toggle buttons to block/allow individual applications.
   - Timed blocking dialog for individual applications.
4. **Schedules Tab**:
   - Multi-day selector (Monday through Sunday) with time pickers for recurring focus hours.
5. **Settings & Emergency Recovery Tab**:
   - Administrative privilege status.
   - Emergency Unblock button.
   - Hosts file backup recovery and DNS cache flush.
   - Technical limitations overview and recent audit event log.

---

## 4. Command-Line Interface (CLI)

FocusGuard provides a CLI (`focusguard`) for terminal management without needing the graphical interface.

### Example Commands

| Command | Description |
|---|---|
| `focusguard status` | Displays current focus state, timer countdown, mode, and summary |
| `focusguard allow-site https://example.com` | Adds an approved website to the Whitelist |
| `focusguard block-site https://example.org` | Adds a website to the Blacklist |
| `focusguard unblock-site example.org` | Removes a website rule |
| `focusguard list-sites` | Lists all configured website rules, categories, and statuses |
| `focusguard list-apps` | Displays detected desktop applications, executables, and states |
| `focusguard block-app firefox --duration 2h` | Blocks an application for a specified duration (e.g. 2 hours) |
| `focusguard unblock-app firefox` | Immediately unblocks a desktop application |
| `focusguard schedule list` | Displays configured recurring blocking schedules |
| `focusguard mode [whitelist\|blacklist]` | Inspects or toggles system-wide filtering mode |
| `focusguard emergency-unblock` | Emergency fail-safe: immediately clears all blocks and restores access |
| `focusguard daemon run` | Runs the headless background enforcement daemon |

---

## 5. Security Model & Restriction Enforcement

### Administrative Privileges
- Modifying the system hosts file (`/etc/hosts` on Linux, `%SystemRoot%\System32\drivers\etc\hosts` on Windows) requires elevated permissions.
- FocusGuard performs checks upfront. If elevated rights are required, it issues descriptive guidance rather than crashing.
- On Linux, run with `sudo focusguard ...` or enable the background systemd service (`focusguard.service`).
- On Windows, the installer sets `PrivilegesRequired=admin` and shortcuts request administrator elevation via UAC.

### Safety Backups & Fail-Safe Recovery
- Before modifying system configuration, FocusGuard creates a safety backup at `hosts.focusguard.bak`.
- The `emergency-unblock` command or GUI button can be executed at any time to immediately strip FocusGuard blocks and restore normal system access.

---

## 6. Installation & Setup

### Ubuntu Linux

#### Option 1: Install Pre-Built `.deb` Package (Recommended)
Download or build `focusguard_1.0.0_amd64.deb`:
```bash
sudo dpkg -i dist/focusguard_1.0.0_amd64.deb
sudo apt-get install -f   # Installs any missing dependencies
```

Once installed:
- Run from the application launcher: Search for **FocusGuard** in your desktop menu.
- Run from terminal:
  ```bash
  focusguard status
  focusguard --help
  ```

#### Option 2: Run Directly from Source
```bash
cd focusguard
sudo apt-get update
sudo apt-get install -y python3-pyside6.qtwidgets python3-pyside6.qtsvg python3-psutil
python3 -m focusguard.main
```

---

### Windows

#### Option 1: Native Windows Setup Installer
1. Download `FocusGuard-Setup-1.0.0.exe` from the `dist/` directory.
2. Double-click the installer and accept the UAC Administrator prompt.
3. The wizard installs FocusGuard into `C:\Program Files\FocusGuard`, sets up desktop shortcuts, and registers an uninstaller in Add/Remove Programs.

#### Option 2: Portable Standalone Executable
Extract the `dist/FocusGuard/` folder and run `FocusGuard.exe`.

---

## 7. Building Distribution Packages

### Building the Ubuntu Linux `.deb` Package
On an Ubuntu/Debian system:
```bash
chmod +x packaging/deb/build_deb.sh
./packaging/deb/build_deb.sh
```
The output package will be generated at `dist/focusguard_1.0.0_amd64.deb`.

### Building the Windows `.exe` Installer
On a Windows machine with Python 3.8+ and Inno Setup 6:
```cmd
pip install -r requirements.txt
python packaging\windows\build_windows.py
```
Or run the one-click batch script:
```cmd
packaging\windows\build_windows_exe.bat
```
The output executable and installer will be generated in `dist/`.

---

## 8. Automated Testing Suite

FocusGuard includes a test suite covering database persistence, hosts management, safety checks, process detection, duration parsing, and CLI commands.

Run tests using `pytest`:
```bash
python3 -m pytest tests/ -v
```

All 28 unit and integration tests execute with 100% pass rate:
```
tests/test_app_detector.py::test_app_detector_installed_apps PASSED
tests/test_app_detector.py::test_app_detector_running_processes PASSED
tests/test_block_server.py::test_block_server_health PASSED
tests/test_cli.py::test_cli_parser_commands PASSED
tests/test_cli.py::test_cli_execution_status PASSED
tests/test_database.py::test_website_rules_crud PASSED
tests/test_database.py::test_extract_domain PASSED
tests/test_database.py::test_app_rules_crud PASSED
tests/test_database.py::test_schedule_rules PASSED
tests/test_database.py::test_active_sessions_expiration PASSED
tests/test_duration.py::test_parse_duration_units PASSED
tests/test_duration.py::test_parse_duration_combined PASSED
tests/test_duration.py::test_parse_plain_number_as_minutes PASSED
tests/test_duration.py::test_parse_colon_format PASSED
tests/test_duration.py::test_parse_invalid PASSED
tests/test_duration.py::test_format_duration PASSED
tests/test_duration.py::test_format_time_remaining PASSED
tests/test_hosts_manager.py::test_hosts_apply_blocked_domains PASSED
tests/test_hosts_manager.py::test_hosts_clear_all_blocks PASSED
tests/test_hosts_manager.py::test_hosts_restore_from_backup PASSED
tests/test_safety.py::test_normalize_process_name PASSED
tests/test_safety.py::test_critical_linux_processes_protected PASSED
tests/test_safety.py::test_critical_windows_processes_protected PASSED
tests/test_safety.py::test_pid_safety PASSED
tests/test_safety.py::test_non_critical_apps_allowed_for_blocking PASSED
tests/test_scheduler.py::test_start_timed_session PASSED
tests/test_scheduler.py::test_cancel_active_sessions PASSED
tests/test_scheduler.py::test_recurring_schedule_matching PASSED

============================== 28 passed in 0.71s ==============================
```

---

## 9. Technical Limitations & Guidance

1. **DNS-over-HTTPS (DoH)**: Modern browsers may attempt to bypass system DNS resolution by querying encrypted DoH servers directly. FocusGuard redirects known public DoH resolvers (Cloudflare, Google DNS) in its blocking pool. For foolproof enforcement, disable "Secure DNS" in browser settings.
2. **VPN Tunnels & Tor**: VPN clients encapsulate all network traffic, bypassing local OS DNS tables. Use FocusGuard's Application Blocking tab to prevent VPN or proxy software from running during focus sessions.
3. **Core Operating System Protection**: FocusGuard enforces strict non-blockable whitelists for operating system components. Critical services (like display servers, desktop shells, and process managers) cannot be terminated.
