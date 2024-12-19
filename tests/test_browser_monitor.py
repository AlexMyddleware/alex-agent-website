import pytest
from models.browser_monitor import FirefoxMonitor

def test_firefox_monitor_initialization():
    monitor = FirefoxMonitor()
    assert isinstance(monitor, FirefoxMonitor)

def test_unblock_sites():
    monitor = FirefoxMonitor()
    with pytest.raises(SystemExit):
        monitor.unblock_sites() 