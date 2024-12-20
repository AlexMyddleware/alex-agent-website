import pytest
from models.browser_monitor import FirefoxMonitor

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