"""First collector: operating system details."""

from wintriage.models import CheckResult, Status
from wintriage.powershell import PowerShellError, run_json

# Windows PowerShell 5.1 serializes dates to JSON as "\/Date(1699999999999)\/", which is
# awkward to parse. Formatting LastBootUpTime as an ISO 8601 string inside PowerShell
# gives Python a clean value on every PowerShell version.
COMMAND = (
    "Get-CimInstance Win32_OperatingSystem | "
    "Select-Object Caption, Version, BuildNumber, "
    "@{Name='LastBoot'; Expression={$_.LastBootUpTime.ToUniversalTime().ToString('o')}} | "
    "ConvertTo-Json"
)


def check_os_info() -> CheckResult:
    try:
        data = run_json(COMMAND)
    except PowerShellError as exc:
        return CheckResult("os_info", Status.ERROR, str(exc))

    message = f"{data['Caption']} (build {data['BuildNumber']})"
    return CheckResult("os_info", Status.OK, message, data)
