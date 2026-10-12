"""Tests for CLI argument parsing and commands."""

import pytest
from focusguard.cli import build_parser, main

def test_cli_parser_commands():
    parser = build_parser()

    # status
    args = parser.parse_args(["status"])
    assert args.command == "status"

    # allow-site
    args = parser.parse_args(["allow-site", "https://example.com"])
    assert args.command == "allow-site"
    assert args.url == "https://example.com"

    # block-site
    args = parser.parse_args(["block-site", "https://distraction.com"])
    assert args.command == "block-site"
    assert args.url == "https://distraction.com"

    # block-app
    args = parser.parse_args(["block-app", "firefox", "--duration", "2h"])
    assert args.command == "block-app"
    assert args.app_name == "firefox"
    assert args.duration == "2h"

    # unblock-app
    args = parser.parse_args(["unblock-app", "firefox"])
    assert args.command == "unblock-app"
    assert args.app_name == "firefox"

    # schedule list
    args = parser.parse_args(["schedule", "list"])
    assert args.command == "schedule"
    assert args.subcommand == "list"

    # mode
    args = parser.parse_args(["mode", "whitelist"])
    assert args.command == "mode"
    assert args.set_mode == "whitelist"

def test_cli_execution_status(capsys):
    ret = main(["status"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Focus Guard State" in captured.out
