import pytest
from models.browser_monitor import FirefoxMonitor
import os
from unittest.mock import patch, Mock
from datetime import datetime
import tempfile
import sqlite3

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

def test_check_blocked_access_with_visits():
    monitor = FirefoxMonitor()
    
    # Create a temporary SQLite database with test data
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        # Create test database
        conn = sqlite3.connect(temp_file.name)
        c = conn.cursor()
        
        # Create required tables
        c.execute('''CREATE TABLE moz_places
                    (id INTEGER PRIMARY KEY, url TEXT)''')
        c.execute('''CREATE TABLE moz_historyvisits
                    (id INTEGER PRIMARY KEY, place_id INTEGER, visit_date INTEGER)''')
        
        # Insert test data
        c.execute("INSERT INTO moz_places (id, url) VALUES (1, 'https://youtube.com')")
        c.execute("INSERT INTO moz_places (id, url) VALUES (2, 'https://example.com')")
        
        # Get current time for comparison
        start_time = datetime.now()
        
        # Add visit records with timestamps slightly after start_time
        current_time_micro = int(start_time.timestamp() * 1000000) + 1000000  # Add 1 second in microseconds
        c.execute("INSERT INTO moz_historyvisits (place_id, visit_date) VALUES (1, ?)", 
                 (current_time_micro,))
        c.execute("INSERT INTO moz_historyvisits (place_id, visit_date) VALUES (2, ?)", 
                 (current_time_micro,))
        
        conn.commit()
        conn.close()
        
        # Set this as our Firefox profile path
        monitor.firefox_path = temp_file.name
        
        # Run the check
        attempts = monitor.check_blocked_access(start_time)
        
        # Verify results
        assert isinstance(attempts, list)
        assert len(attempts) == 1  # Should only find youtube.com as blocked
        assert 'youtube.com' in attempts[0][0]  # URL is in the first element of each tuple
        
        # Make sure all connections are closed before cleanup
        monitor = None  # Release any references to the database
        import gc
        gc.collect()  # Force garbage collection
        
        try:
            os.unlink(temp_file.name)
        except PermissionError:
            print("Note: Could not delete temporary file immediately due to Windows file locking")

def test_block_sites_firefox_failure():
    """Test the block_sites method when Firefox blocking fails and falls back to hosts blocking."""
    monitor = FirefoxMonitor()
    
    # Mock the firefox_blocker to simulate failure
    with patch.object(monitor.firefox_blocker, 'block_sites', return_value=False):
        # Mock the hosts_blocker to succeed
        with patch.object(monitor.hosts_blocker, 'block_websites', return_value=True):
            # Test the block_sites method
            result = monitor.block_sites()
            
            # Verify that the method returned True (successful fallback)
            assert result is True
            
            # Verify that both methods were called
            monitor.firefox_blocker.block_sites.assert_called_once()
            monitor.hosts_blocker.block_websites.assert_called_once()
