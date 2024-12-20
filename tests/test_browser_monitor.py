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

def test_check_blocked_access_profile_not_exists():
    monitor = FirefoxMonitor()
    # Set firefox_path to a non-existent path
    monitor.firefox_path = "/path/that/does/not/exist"
    
    start_time = datetime.now()
    attempts = monitor.check_blocked_access(start_time)
    
    # Verify attempts is initialized as an empty list
    assert isinstance(attempts, list)
    assert len(attempts) == 0

def test_check_blocked_access_initialize_attempts():
    monitor = FirefoxMonitor()
    # Set firefox_path to a path that exists but isn't a valid database
    # This will make it pass the os.path.exists check but fail later
    monitor.firefox_path = __file__  # Use the current test file as a path that exists
    
    start_time = datetime.now()
    attempts = monitor.check_blocked_access(start_time)
    
    # Verify attempts is initialized as an empty list
    assert isinstance(attempts, list)
    assert len(attempts) == 0

@patch('platform.system')
def test_firefox_profile_path_macos(mock_platform):
    # Mock platform.system to return "Darwin" (macOS)
    mock_platform.return_value = "Darwin"
    
    # Mock expanduser to return a predictable path
    with patch('os.path.expanduser') as mock_expanduser:
        mock_expanduser.return_value = "/Users/testuser/Library/Application Support/Firefox/Profiles"
        
        monitor = FirefoxMonitor()
        # The actual path won't be created since we're mocking os.listdir,
        # but we can verify that expanduser was called with the correct argument
        mock_expanduser.assert_called_once_with("~/Library/Application Support/Firefox/Profiles")

@patch('platform.system')
def test_firefox_profile_path_windows(mock_platform):
    # Mock platform.system to return "Windows"
    mock_platform.return_value = "Windows"
    
    # Mock expandvars to return a predictable path
    with patch('os.path.expandvars') as mock_expandvars:
        mock_expandvars.return_value = r"C:\Users\testuser\AppData\Roaming\Mozilla\Firefox\Profiles"
        
        monitor = FirefoxMonitor()
        # Verify expandvars was called with the correct argument
        mock_expandvars.assert_called_once_with(r"%APPDATA%\Mozilla\Firefox\Profiles")