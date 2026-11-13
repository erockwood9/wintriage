"""Tests for powershell.run_json.

No test launches PowerShell: subprocess.run is replaced with a fake, so the tests are
fast and pass on any machine, including CI runners.
"""

import subprocess

import pytest

from wintriage import powershell


def fake_run(stdout="", returncode=0, stderr=""):
    """Build a stand-in for subprocess.run that returns canned output."""

    def _run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, returncode, stdout, stderr)

    return _run


@pytest.fixture(autouse=True)
def pretend_powershell_exists(monkeypatch):
    # Runs before every test in this file, so none of them depend on PowerShell being
    # installed. test_missing_powershell_raises overrides it to simulate the opposite.
    monkeypatch.setattr(powershell, "find_powershell", lambda: "powershell")


def test_run_json_returns_parsed_json_on_success(monkeypatch):
    monkeypatch.setattr(powershell.subprocess, "run", fake_run(stdout='{"BuildNumber": "26100"}'))

    assert powershell.run_json("anything") == {"BuildNumber": "26100"}


def test_run_json_raises_when_powershell_exits_nonzero(monkeypatch):
    monkeypatch.setattr(
        powershell.subprocess, "run", fake_run(returncode=1, stderr="access denied")
    )

    with pytest.raises(powershell.PowerShellError, match="access denied"):
        powershell.run_json("anything")


def test_run_json_raises_when_output_is_not_json(monkeypatch):
    monkeypatch.setattr(powershell.subprocess, "run", fake_run(stdout="not json"))

    with pytest.raises(powershell.PowerShellError, match="valid JSON"):
        powershell.run_json("anything")


def test_run_json_raises_when_powershell_is_not_installed(monkeypatch):
    monkeypatch.setattr(powershell, "find_powershell", lambda: None)

    with pytest.raises(powershell.PowerShellError, match="not found"):
        powershell.run_json("anything")


def test_run_json_raises_when_command_times_out(monkeypatch):
    def slow(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, 1)

    monkeypatch.setattr(powershell.subprocess, "run", slow)

    with pytest.raises(powershell.PowerShellError, match="timed out"):
        powershell.run_json("anything", timeout=1)


def test_run_json_passes_command_as_list_without_shell(monkeypatch):
    # Spy: record how subprocess.run was called. A list of arguments (never one string
    # with shell=True) means the command text can't be misread as extra shell commands.
    seen = {}

    def spy(cmd, **kwargs):
        seen["cmd"], seen["kwargs"] = cmd, kwargs
        return subprocess.CompletedProcess(cmd, 0, "{}", "")

    monkeypatch.setattr(powershell.subprocess, "run", spy)

    powershell.run_json("Get-Date")

    assert isinstance(seen["cmd"], list) and seen["cmd"][-1] == "Get-Date"
    assert not seen["kwargs"].get("shell")
