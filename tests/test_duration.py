"""Tests for duration parsing and formatting."""

from datetime import timedelta
from focusguard.core.duration import parse_duration, format_duration, format_time_remaining

def test_parse_duration_units():
    assert parse_duration("2h") == timedelta(hours=2)
    assert parse_duration("30m") == timedelta(minutes=30)
    assert parse_duration("45s") == timedelta(seconds=45)
    assert parse_duration("1d") == timedelta(days=1)

def test_parse_duration_combined():
    assert parse_duration("1h30m") == timedelta(hours=1, minutes=30)
    assert parse_duration("2h 15m") == timedelta(hours=2, minutes=15)
    assert parse_duration("1d 2h") == timedelta(days=1, hours=2)

def test_parse_plain_number_as_minutes():
    assert parse_duration("60") == timedelta(minutes=60)
    assert parse_duration("15") == timedelta(minutes=15)
    assert parse_duration("5") == timedelta(minutes=5)
    assert parse_duration("5m") == timedelta(minutes=5)
    assert parse_duration("5min") == timedelta(minutes=5)

def test_parse_colon_format():
    assert parse_duration("01:30") == timedelta(hours=1, minutes=30)
    assert parse_duration("02:15:30") == timedelta(hours=2, minutes=15, seconds=30)

def test_parse_invalid():
    assert parse_duration("invalid") is None
    assert parse_duration("") is None
    assert parse_duration("0m") is None

def test_format_duration():
    assert format_duration(timedelta(hours=2)) == "2h"
    assert format_duration(timedelta(hours=1, minutes=30)) == "1h 30m"
    assert format_duration(timedelta(seconds=45)) == "45s"

def test_format_time_remaining():
    assert format_time_remaining(3665) == "01:01:05"
    assert format_time_remaining(125) == "02:05"
    assert format_time_remaining(0) == "00:00"
