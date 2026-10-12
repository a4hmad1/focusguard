"""Tests for system critical process protection."""

from focusguard.core.safety import is_critical_process, normalize_process_name

def test_normalize_process_name():
    assert normalize_process_name("/usr/bin/firefox") == "firefox"
    assert normalize_process_name("C:\\Windows\\System32\\explorer.exe") == "explorer.exe"
    assert normalize_process_name("Discord.EXE") == "discord.exe"

def test_critical_linux_processes_protected():
    assert is_critical_process("systemd") is True
    assert is_critical_process("init") is True
    assert is_critical_process("gnome-shell") is True
    assert is_critical_process("Xorg") is True
    assert is_critical_process("bash") is True
    assert is_critical_process("focusguard") is True

def test_critical_windows_processes_protected():
    assert is_critical_process("explorer.exe") is True
    assert is_critical_process("svchost.exe") is True
    assert is_critical_process("csrss.exe") is True
    assert is_critical_process("dwm.exe") is True

def test_pid_safety():
    assert is_critical_process("unknown_custom_proc", pid=1) is True
    assert is_critical_process("idle", pid=0) is True

def test_non_critical_apps_allowed_for_blocking():
    assert is_critical_process("discord") is False
    assert is_critical_process("spotify") is False
    assert is_critical_process("steam") is False
    assert is_critical_process("minecraft.exe") is False
