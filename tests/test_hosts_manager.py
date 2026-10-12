"""Tests for HostsManager file manipulation."""

import pytest
from focusguard.engine.hosts_manager import HostsManager, BLOCK_START_MARKER, BLOCK_END_MARKER

@pytest.fixture
def hosts_setup(tmp_path):
    hosts_file = tmp_path / "hosts"
    backup_file = tmp_path / "hosts.bak"

    initial_content = "127.0.0.1 localhost\n::1 localhost\n192.168.1.1 router.local\n"
    hosts_file.write_text(initial_content)

    mgr = HostsManager(hosts_path=hosts_file, backup_path=backup_file)
    return mgr, hosts_file, backup_file

def test_hosts_apply_blocked_domains(hosts_setup):
    mgr, hosts_file, backup_file = hosts_setup

    domains = ["example.com", "distraction.net"]
    mgr.apply_blocked_domains(domains)

    content = hosts_file.read_text()
    assert BLOCK_START_MARKER in content
    assert BLOCK_END_MARKER in content
    assert "127.0.0.1 example.com" in content
    assert "127.0.0.1 www.example.com" in content
    assert "127.0.0.1 distraction.net" in content
    assert "192.168.1.1 router.local" in content  # original line preserved

    # Verify backup was created
    assert backup_file.exists()
    assert "router.local" in backup_file.read_text()

def test_hosts_clear_all_blocks(hosts_setup):
    mgr, hosts_file, _ = hosts_setup
    mgr.apply_blocked_domains(["badsite.com"])
    assert "badsite.com" in hosts_file.read_text()

    mgr.clear_all_blocks()
    content = hosts_file.read_text()
    assert BLOCK_START_MARKER not in content
    assert "badsite.com" not in content
    assert "127.0.0.1 localhost" in content

def test_hosts_restore_from_backup(hosts_setup):
    mgr, hosts_file, backup_file = hosts_setup
    mgr.apply_blocked_domains(["blocked.org"])
    assert "blocked.org" in hosts_file.read_text()

    mgr.restore_from_backup()
    content = hosts_file.read_text()
    assert "blocked.org" not in content
    assert "router.local" in content
