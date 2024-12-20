import pytest
from models.browser_monitor import FirefoxMonitor
import os
from unittest.mock import patch
from datetime import datetime

def test_firefox_monitor_initialization():
    monitor = FirefoxMonitor()
    assert isinstance(monitor, FirefoxMonitor)

def test_unblock_sites():
    monitor = FirefoxMonitor()
    with pytest.raises(SystemExit):
        monitor.unblock_sites() 

def test_check_blocking_status_with_specific_url():
    monitor = FirefoxMonitor()
    # Test with a single URL
    test_url = "youtube.com"
    status_report = monitor.check_blocking_status([test_url])
    
    # Check that the report contains our expected elements
    assert "Blocking Status Report" in status_report
    assert test_url in status_report
    assert "🚫 Blocked" in status_report or "✅ Not Blocked" in status_report

def test_check_blocking_status_formatting():
    monitor = FirefoxMonitor()
    status_report = monitor.check_blocking_status(["facebook.com"])
    
    # Check that the report has the expected formatting
    lines = status_report.split('\n')
    assert len(lines) >= 4  # Title, separator, global status, and at least one URL
    assert lines[0] == "Blocking Status Report:"
    assert "-" * 50 in lines  # Check for separator line

def test_firefox_monitor_blocked_sites():
    monitor = FirefoxMonitor()
    # Test that common blocked sites are in the list
    assert "youtube.com" in monitor.blocked_sites
    assert "facebook.com" in monitor.blocked_sites
    assert "reddit.com" in monitor.blocked_sites

def test_firefox_profile_not_found():
    # Mock os.listdir to return an empty list, which will trigger StopIteration
    with patch('os.listdir', return_value=[]):
        monitor = FirefoxMonitor()
        assert monitor.firefox_path is None

def test_firefox_profile_directory_not_found():
    # Mock os.listdir to raise FileNotFoundError
    with patch('os.listdir', side_effect=FileNotFoundError):
        monitor = FirefoxMonitor()
        assert monitor.firefox_path is None

def test_check_blocked_access_no_profile():
    monitor = FirefoxMonitor()
    # Set firefox_path to None to simulate no profile found
    monitor.firefox_path = None
    
    # Test with a start time
    start_time = datetime.now()
    result = monitor.check_blocked_access(start_time)
    
    # Should return empty list when no profile is found
    assert isinstance(result, list)
    assert len(result) == 0