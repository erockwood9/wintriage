"""Tests never launch PowerShell: subprocess.run is replaced with a fake.

That keeps them fast and lets them pass on any machine, including CI runners.
"""

import subprocess

import pytest

from wintriage import os_info, powershell
from wintriage.models import Status


def fake_run(stdout="", returncode=0, stderr=""):
    """Build a stand-in for subprocess.run that returns canned output."""

    def _run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, returncode, stdout, stderr)

    return _run


@pytest.fixture(autouse=True)
def pretend_powershell_exists(monkeypatch):
    monkeypatch.setattr(powershell, "find_powershell", lambda: "powershell")


def test_parses_json(monkeypatch):
    monkeypatch.setattr(powershell.subprocess, "run", fake_run('{"BuildNumber": "26100"}'))
    assert powershell.run_json("anything") == {"BuildNumber": "26100"}


def test_nonzero_exit_raises_with_stderr(monkeypatch):
    monkeypatch.setattr(powershell.subprocess, "run", fake_run("", 1, "access denied"))
    with pytest.raises(powershell.PowerShellError, match="access denied"):
        powershell.run_json("anything")


def test_invalid_json_raises(monkeypatch):
    monkeypatch.setattr(powershell.subprocess, "run", fake_run("not json"))
    with pytest.raises(powershell.PowerShellError, match="valid JSON"):
        powershell.run_json("anything")


def test_missing_powershell_raises(monkeypatch):
    monkeypatch.setattr(powershell, "find_powershell", lambda: None)
    with pytest.raises(powershell.PowerShellError, match="not found"):
        powershell.run_json("anything")


def test_timeout_raises(monkeypatch):
    def slow(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, 1)

    monkeypatch.setattr(powershell.subprocess, "run", slow)
    with pytest.raises(powershell.PowerShellError, match="timed out"):
        powershell.run_json("anything", timeout=1)


def test_command_is_passed_as_argument_list(monkeypatch):
    seen = {}

    def spy(cmd, **kwargs):
        seen["cmd"], seen["kwargs"] = cmd, kwargs
        return subprocess.CompletedProcess(cmd, 0, "{}", "")

    monkeypatch.setattr(powershell.subprocess, "run", spy)
    powershell.run_json("Get-Date")
    assert isinstance(seen["cmd"], list) and seen["cmd"][-1] == "Get-Date"
    assert not seen["kwargs"].get("shell")


def test_os_info_ok(monkeypatch):
    sample = {"Caption": "Windows 11 Pro", "BuildNumber": "26100", "Version": "10.0.26100"}
    monkeypatch.setattr(os_info, "run_json", lambda command: sample)
    result = os_info.check_os_info()
    assert result.status is Status.OK
    assert "Windows 11 Pro" in result.message and result.data == sample


def test_os_info_error_when_powershell_fails(monkeypatch):
    def boom(command):
        raise powershell.PowerShellError("PowerShell not found on PATH")

    monkeypatch.setattr(os_info, "run_json", boom)
    result = os_info.check_os_info()
    assert result.status is Status.ERROR and "not found" in result.message
