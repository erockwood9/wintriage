"""Tests for os_info.check_os_info.

run_json is replaced with a fake, so these test only how check_os_info reacts to what
PowerShell returns, not PowerShell itself.
"""

from wintriage import os_info
from wintriage.models import Status
from wintriage.powershell import PowerShellError


def test_check_os_info_is_ok_when_powershell_returns_data(monkeypatch):
    sample = {"Caption": "Windows 11 Pro", "BuildNumber": "26100", "Version": "10.0.26100"}
    monkeypatch.setattr(os_info, "run_json", lambda command: sample)

    result = os_info.check_os_info()

    assert result.status is Status.OK
    assert "Windows 11 Pro" in result.message
    assert result.data == sample


def test_check_os_info_is_error_when_powershell_fails(monkeypatch):
    def boom(command):
        raise PowerShellError("PowerShell not found on PATH")

    monkeypatch.setattr(os_info, "run_json", boom)

    result = os_info.check_os_info()

    assert result.status is Status.ERROR
    assert "not found" in result.message
