"""The shape every check hands back, so reports can treat all checks the same way."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Status(StrEnum):
    """Outcome of a check. A StrEnum serializes to JSON as plain text, e.g. "ok"."""

    OK = "ok"
    WARN = "warn"
    CRIT = "crit"
    ERROR = "error"  # the check ran, but something broke
    SKIPPED = "skipped"  # the check could not run (not admin, no battery, no PowerShell)


@dataclass
class CheckResult:
    name: str  # short id, e.g. "os_info"
    status: Status
    message: str  # one human-readable line for the report
    data: dict[str, Any] = field(default_factory=dict)  # raw details, for JSON output
