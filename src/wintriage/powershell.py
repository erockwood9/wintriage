"""Run a PowerShell command and return its output parsed as JSON."""

import json
import shutil
import subprocess
from typing import Any


class PowerShellError(Exception):
    """A PowerShell command could not run, or returned something unusable."""


def find_powershell() -> str | None:
    # Get the installed version of PowerShell. Prefer powershell.exe (older, more common)
    # over pwsh (the modern version).
    return shutil.which("powershell") or shutil.which("pwsh")


def run_json(command: str, timeout: float = 30) -> Any:
    """Run `command` in PowerShell and return its stdout parsed as JSON.

    The command should end in `| ConvertTo-Json`. Raises PowerShellError with a clear
    message for every way this can fail, so callers never see a raw traceback.
    """
    exe = find_powershell()
    if exe is None:
        raise PowerShellError("PowerShell not found on PATH")

    try:
        proc = subprocess.run(
            # A list of arguments, never one string with shell=True. Nothing here is
            # interpreted by a shell, which is what prevents command injection.
            [exe, "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,  # we inspect returncode ourselves to give a better message
        )
    except subprocess.TimeoutExpired as exc:
        raise PowerShellError(f"timed out after {timeout}s") from exc

    if proc.returncode != 0:
        raise PowerShellError(f"exit code {proc.returncode}: {proc.stderr.strip()[:300]}")

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise PowerShellError(f"output was not valid JSON: {exc}") from exc
