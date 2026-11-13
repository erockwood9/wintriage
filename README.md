# wintriage

[![CI](https://github.com/erockwood9/wintriage/actions/workflows/ci.yml/badge.svg)](https://github.com/erockwood9/wintriage/actions/workflows/ci.yml)

A Windows tool that simplifies checks and tasks that are often done by hand, and keeps
them all in one place.

**Status:** early development. Only the OS info check works so far.

## Features

- [x] OS info
- [ ] Disk health
- [ ] Battery health
- [ ] System file and Windows image checks
- [ ] Network checks
- [ ] Command-line interface and reports
- [ ] Optional repair of problems found

## Installation

Requires Windows 10 or 11 and Python 3.11 or newer.

```powershell
git clone https://github.com/erockwood9/wintriage.git
cd wintriage
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Usage

There is no command-line interface yet. To run the one check that exists:

```powershell
python -c "from wintriage.os_info import check_os_info; print(check_os_info())"
```

## Development

```powershell
pytest
ruff check .
```

## About

I work in IT support and wanted one place for the checks I usually run by hand. It is also
a project for practicing how to structure and test a Python tool.

## License

[MIT](LICENSE)
